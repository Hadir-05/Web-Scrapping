"""
Module de scraping AliExpress avec recherche hybride (catégorie + image) et pagination
"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, quote, urlparse, parse_qs, urlencode
from pathlib import Path
import math

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import Page

from src.models.data_models import ImageMetadata, ProductData


class AliExpressImageSearchScraper:
    """Scraper AliExpress avec recherche hybride (catégorie + comparaison d'images) et pagination"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.image_metadata_list: List[ImageMetadata] = []
        self.product_data_list: List[ProductData] = []
        self.image_counter = 0
        self.current_page = 1
        self.target_results = 0

    async def search_by_image(
        self,
        image_path: str,
        category: str = "",
        max_results: int = 20,
        headless: bool = True
    ) -> Tuple[List[ImageMetadata], List[ProductData]]:
        """
        Rechercher des produits sur AliExpress avec catégorie + image

        Args:
            image_path: Chemin vers l'image à rechercher
            category: Catégorie du produit (ex: "bag", "ring", "shoes")
            max_results: Nombre maximum de résultats (peut parcourir plusieurs pages)
            headless: Mode headless pour le navigateur

        Returns:
            Tuple contenant les listes de ImageMetadata et ProductData
        """
        self.image_metadata_list = []
        self.product_data_list = []
        self.image_counter = 0
        self.current_page = 1
        self.target_results = max_results

        # Si pas de catégorie, utiliser "product"
        if not category:
            category = "product"

        # Estimer le nombre de pages nécessaires (environ 40-60 produits par page)
        products_per_page = 40
        estimated_pages = math.ceil(max_results / products_per_page)
        # Limiter à 10 pages maximum pour éviter les timeouts
        max_pages = min(estimated_pages, 10)

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=max_pages,
            headless=headless,
            browser_type='chromium',
            max_request_retries=2,
        )

        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            page = context.page

            # Extraire les produits de la page actuelle
            await self._extract_products_from_current_page(context)

            # Si on n'a pas assez de produits et qu'on est sur la première page,
            # ajouter les URLs des pages suivantes
            if len(self.product_data_list) < self.target_results and self.current_page == 1:
                # Essayer de trouver et enqueue les pages suivantes
                await self._enqueue_next_pages(context, category, max_pages)

        # Construire l'URL de recherche initiale
        search_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html"

        await crawler.run([search_url])

        return self.image_metadata_list, self.product_data_list

    async def _enqueue_next_pages(self, context: PlaywrightCrawlingContext, category: str, max_pages: int):
        """Ajouter les URLs des pages suivantes à la queue"""
        try:
            # Générer les URLs pour les pages suivantes
            for page_num in range(2, max_pages + 1):
                # AliExpress utilise le paramètre 'page' dans l'URL
                next_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html?page={page_num}"

                context.log.info(f"📑 Ajout de la page {page_num} à la queue")
                await context.add_requests([next_url])

        except Exception as e:
            context.log.error(f"❌ Erreur lors de l'ajout des pages suivantes: {e}")

    async def _extract_products_from_current_page(self, context: PlaywrightCrawlingContext):
        """
        Extraire les produits de la page actuelle
        """
        page = context.page
        url = page.url

        try:
            # Déterminer le numéro de page actuel
            if 'page=' in url:
                try:
                    page_param = url.split('page=')[1].split('&')[0]
                    self.current_page = int(page_param)
                except:
                    pass

            context.log.info(f"📄 Extraction depuis la page {self.current_page}: {url}")

            # Attendre que la page soit chargée
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            # Scroll pour charger les produits (lazy loading)
            context.log.info("📜 Scroll pour charger les produits...")
            for i in range(5):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(800)

            # Attendre un peu plus pour que les images se chargent
            await page.wait_for_timeout(2000)

            # Sélecteurs pour les cartes de produits AliExpress
            product_selectors = [
                'div[class*="search-card-item"]',
                'div[class*="product-card"]',
                'a[class*="search-card-item"]',
                'div[class*="list--item"]',
                'div[data-product-id]',
                'article[class*="product"]',
                '.list--item',
                'div.manhattan--container--product',
                'a[href*="/item/"]',
            ]

            products = []
            for selector in product_selectors:
                try:
                    products = await page.query_selector_all(selector)
                    if len(products) > 0:
                        context.log.info(f"✅ {len(products)} éléments trouvés avec: {selector}")
                        break
                except:
                    continue

            if not products:
                context.log.warning(f"⚠️ Aucun produit trouvé sur la page {self.current_page}")
                # Screenshot pour debug
                debug_path = self.output_dir / f"debug_page_{self.current_page}.png"
                await page.screenshot(path=str(debug_path), full_page=True)
                context.log.info(f"📸 Screenshot de debug sauvegardé: {debug_path}")
                return

            context.log.info(f"📊 Traitement de {len(products)} produits de la page {self.current_page}...")

            # Traiter chaque produit
            for idx, product in enumerate(products):
                # Arrêter si on a atteint le nombre souhaité
                if len(self.product_data_list) >= self.target_results:
                    context.log.info(f"🎯 Objectif atteint: {len(self.product_data_list)} produits")
                    break

                try:
                    # Scroll vers le produit
                    try:
                        await product.scroll_into_view_if_needed()
                        await page.wait_for_timeout(300)
                    except:
                        pass

                    # Extraire l'URL du produit
                    product_url = ""
                    try:
                        product_url = await product.get_attribute('href')
                        if product_url and not product_url.startswith('http'):
                            product_url = urljoin(url, product_url)
                    except:
                        pass

                    if not product_url:
                        link_elem = await product.query_selector('a[href*="/item/"]')
                        if link_elem:
                            product_url = await link_elem.get_attribute('href')
                            if product_url and not product_url.startswith('http'):
                                product_url = urljoin(url, product_url)

                    # Extraire le titre
                    title = f"Product {len(self.product_data_list) + 1}"
                    title_selectors = [
                        'h1', 'h2', 'h3',
                        'div[class*="title"]',
                        'div[class*="name"]',
                        'span[class*="title"]',
                        'a[title]',
                    ]

                    for selector in title_selectors:
                        try:
                            title_elem = await product.query_selector(selector)
                            if title_elem:
                                title_attr = await title_elem.get_attribute('title')
                                if title_attr and len(title_attr.strip()) > 0:
                                    title = title_attr.strip()
                                    break
                                title_text = await title_elem.inner_text()
                                if title_text and len(title_text.strip()) > 0:
                                    title = title_text.strip()
                                    break
                        except:
                            continue

                    # Extraire le prix
                    price = "N/A"
                    price_selectors = [
                        'div[class*="price"]',
                        'span[class*="price"]',
                        'div[class*="amount"]',
                        'span:has-text("$")',
                        'span:has-text("€")',
                        'span:has-text("US")',
                    ]

                    for selector in price_selectors:
                        try:
                            price_elem = await product.query_selector(selector)
                            if price_elem:
                                price_text = await price_elem.inner_text()
                                if price_text and ('$' in price_text or '€' in price_text or 'US' in price_text):
                                    price = price_text.strip()
                                    break
                        except:
                            continue

                    # Extraire l'image principale
                    src_image = ""
                    img_elem = await product.query_selector('img')
                    if img_elem:
                        for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                            src = await img_elem.get_attribute(attr)
                            if src:
                                if not src.startswith('http'):
                                    src_image = urljoin(url, src)
                                else:
                                    src_image = src
                                break

                    # Télécharger l'image
                    product_image_paths = []
                    if src_image and 'data:image' not in src_image:
                        img_path = await self._download_image(page, src_image)
                        if img_path:
                            product_image_paths.append(img_path)

                            # Ajouter aux métadonnées d'images
                            img_metadata = ImageMetadata(
                                src=src_image,
                                link=product_url or url
                            )
                            self.image_metadata_list.append(img_metadata)

                    # Prendre une capture d'écran du produit
                    screenshot_filename = f"screenshot_product_{len(self.product_data_list) + 1}.png"
                    screenshot_path = self.images_dir / screenshot_filename

                    try:
                        await product.screenshot(path=str(screenshot_path), timeout=5000)
                    except:
                        screenshot_path = Path("")

                    # Créer ProductData
                    product_data = ProductData(
                        item_url=product_url or url,
                        collection_date=datetime.now(),
                        src_image=src_image,
                        title=title,
                        description="",
                        price=price,
                        screenshot_path=str(screenshot_path),
                        product_image_paths=product_image_paths
                    )
                    self.product_data_list.append(product_data)

                    if (idx + 1) % 10 == 0:
                        context.log.info(f"✅ Progression: {len(self.product_data_list)} produits extraits")

                except Exception as e:
                    context.log.error(f"❌ Erreur produit {idx}: {e}")
                    continue

            context.log.info(f"🎉 Page {self.current_page} terminée: {len(self.product_data_list)} produits au total")

        except Exception as e:
            context.log.error(f"❌ Erreur lors de l'extraction de la page {self.current_page}: {e}")

    async def _download_image(self, page: Page, image_url: str) -> str:
        """Télécharger une image et retourner le chemin local"""
        try:
            self.image_counter += 1
            ext = '.jpg'
            if '.' in image_url:
                parsed = urlparse(image_url)
                ext = os.path.splitext(parsed.path)[1] or '.jpg'
                if '?' in ext:
                    ext = ext.split('?')[0]
                if not ext.startswith('.'):
                    ext = '.jpg'
            filename = f"image_{self.image_counter:04d}{ext}"
            filepath = self.images_dir / filename

            try:
                response = await page.request.get(image_url, timeout=10000)
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.body())
                    return str(filepath)
            except Exception as e:
                pass

        except Exception as e:
            pass

        return ""


async def search_aliexpress_by_image(
    image_path: str,
    category: str = "",
    output_dir: str = "output",
    max_results: int = 20
) -> Tuple[List[ImageMetadata], List[ProductData]]:
    """
    Fonction utilitaire pour rechercher sur AliExpress avec catégorie + image

    Args:
        image_path: Chemin vers l'image à rechercher
        category: Catégorie du produit (ex: "bag", "ring", "shoes")
        output_dir: Répertoire de sortie
        max_results: Nombre maximum de résultats (peut parcourir plusieurs pages)

    Returns:
        Tuple contenant les listes de ImageMetadata et ProductData
    """
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, category, max_results)
