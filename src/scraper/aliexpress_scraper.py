"""
Module de scraping AliExpress avec recherche par image améliorée
"""
import asyncio
import os
import base64
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, quote, urlparse
from pathlib import Path
import json

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from src.models.data_models import ImageMetadata, ProductData


class AliExpressImageSearchScraper:
    """Scraper AliExpress pour la recherche par image améliorée"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.image_metadata_list: List[ImageMetadata] = []
        self.product_data_list: List[ProductData] = []
        self.image_counter = 0
        self.search_completed = False

    async def search_by_image(
        self,
        image_path: str,
        max_results: int = 20,
        headless: bool = True
    ) -> Tuple[List[ImageMetadata], List[ProductData]]:
        """
        Rechercher des produits sur AliExpress par image

        Args:
            image_path: Chemin vers l'image à rechercher
            max_results: Nombre maximum de résultats
            headless: Mode headless pour le navigateur

        Returns:
            Tuple contenant les listes de ImageMetadata et ProductData
        """
        self.image_metadata_list = []
        self.product_data_list = []
        self.image_counter = 0
        self.search_completed = False

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1,
            headless=headless,
            browser_type='chromium',
        )

        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            page = context.page

            # Effectuer la recherche par image et extraire les résultats
            await self._perform_image_search_and_extract(context, image_path, max_results)

        # Démarrer avec la page principale d'AliExpress
        await crawler.run(['https://www.aliexpress.com/'])

        return self.image_metadata_list, self.product_data_list

    async def _perform_image_search_and_extract(
        self,
        context: PlaywrightCrawlingContext,
        image_path: str,
        max_results: int
    ):
        """
        Effectuer la recherche par image et extraire les résultats
        """
        page = context.page

        try:
            context.log.info("🌐 Navigation vers AliExpress...")

            # Attendre le chargement complet
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            context.log.info("🔍 Recherche du bouton de recherche par image...")

            # Méthode 1 : Chercher l'icône de caméra dans la barre de recherche
            camera_selectors = [
                # Sélecteurs communs pour l'icône de caméra
                'button[aria-label*="Search by image"]',
                'button[aria-label*="search by image"]',
                'span[data-spm-anchor-id*="search.camera"]',
                '.search-bar__pic',
                '.search-upload-image',
                'div[class*="ImageSearch"]',
                'button:has(svg[class*="camera"])',
                'button:has([class*="camera"])',
                'span:has([class*="camera"])',
                # Icône directe
                'i.search-photo-icon',
                '.comet-icon-camerafilled',
                'span.search-bar__camera-icon',
            ]

            camera_element = None
            for selector in camera_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        # Vérifier si l'élément est visible
                        if await elem.is_visible():
                            camera_element = elem
                            context.log.info(f"✅ Bouton trouvé avec le sélecteur: {selector}")
                            break
                    if camera_element:
                        break
                except Exception as e:
                    continue

            if camera_element:
                try:
                    context.log.info("📸 Clic sur le bouton de recherche par image...")

                    # Scroll vers l'élément et attendre
                    await camera_element.scroll_into_view_if_needed()
                    await page.wait_for_timeout(1000)

                    # Cliquer
                    await camera_element.click()
                    await page.wait_for_timeout(2000)

                    context.log.info("📤 Recherche de l'input file...")

                    # Attendre l'input file (peut être caché)
                    file_input = None
                    input_selectors = [
                        'input[type="file"]',
                        'input[accept*="image"]',
                        'input[name*="image"]',
                    ]

                    for selector in input_selectors:
                        try:
                            file_input = await page.wait_for_selector(selector, timeout=5000, state='attached')
                            if file_input:
                                context.log.info(f"✅ Input file trouvé: {selector}")
                                break
                        except:
                            continue

                    if file_input:
                        context.log.info(f"📂 Upload de l'image: {image_path}")
                        await file_input.set_input_files(image_path)

                        # Attendre que l'image soit uploadée et la recherche lancée
                        context.log.info("⏳ Attente de la fin de l'upload et du chargement des résultats...")
                        await page.wait_for_timeout(5000)

                        # Attendre la navigation ou les résultats
                        try:
                            await page.wait_for_load_state('networkidle', timeout=30000)
                        except:
                            await page.wait_for_timeout(5000)

                        # Extraire les produits
                        context.log.info("📦 Extraction des produits depuis les résultats...")
                        await self._extract_products_from_results(context, max_results)

                        self.search_completed = True
                        return

                    else:
                        context.log.warning("❌ Input file non trouvé après le clic")

                except Exception as e:
                    context.log.error(f"❌ Erreur lors de l'upload: {e}")

            # Si on arrive ici, la méthode principale a échoué
            if not self.search_completed:
                context.log.warning("⚠️ Méthode standard échouée, tentative avec URL directe...")
                await self._try_direct_image_search_url(page, image_path, context, max_results)

        except Exception as e:
            context.log.error(f"❌ Erreur globale: {e}")
            # Dernière tentative
            await self._try_direct_image_search_url(page, image_path, context, max_results)

    async def _try_direct_image_search_url(
        self,
        page: Page,
        image_path: str,
        context: PlaywrightCrawlingContext,
        max_results: int
    ):
        """
        Tenter d'utiliser l'URL directe de recherche par image
        """
        try:
            context.log.info("🔗 Tentative d'accès direct à la page de recherche par image...")

            # AliExpress a une page dédiée pour la recherche par image
            # Essayer d'y accéder directement
            search_by_image_urls = [
                'https://www.aliexpress.com/wholesale',
                'https://www.aliexpress.us/wholesale',
            ]

            for url in search_by_image_urls:
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    await page.wait_for_timeout(3000)

                    # Chercher à nouveau le bouton de recherche par image sur cette page
                    camera_elem = await page.query_selector('button[aria-label*="image"], span.search-bar__camera-icon, i.search-photo-icon')

                    if camera_elem and await camera_elem.is_visible():
                        await camera_elem.click()
                        await page.wait_for_timeout(2000)

                        file_input = await page.wait_for_selector('input[type="file"]', timeout=5000)
                        if file_input:
                            await file_input.set_input_files(image_path)
                            await page.wait_for_timeout(5000)
                            await page.wait_for_load_state('networkidle', timeout=30000)

                            await self._extract_products_from_results(context, max_results)
                            self.search_completed = True
                            return

                except Exception as e:
                    context.log.warning(f"Tentative avec {url} échouée: {e}")
                    continue

            # Si tout a échoué, informer l'utilisateur
            if not self.search_completed:
                context.log.error("❌ Impossible d'effectuer la recherche par image. AliExpress a peut-être changé son interface.")

        except Exception as e:
            context.log.error(f"❌ Erreur lors de la tentative directe: {e}")

    async def _extract_products_from_results(self, context: PlaywrightCrawlingContext, max_results: int):
        """
        Extraire les produits depuis la page de résultats de recherche par image
        """
        page = context.page
        url = page.url

        try:
            context.log.info(f"📄 Extraction depuis: {url}")

            # Attendre que les produits soient chargés
            await page.wait_for_timeout(3000)

            # Sélecteurs pour les cartes de produits AliExpress
            product_selectors = [
                # Sélecteurs de liste de produits
                'div[class*="search-card-item"]',
                'div[class*="product-card"]',
                'a[class*="search-card-item"]',
                'div[class*="list-item"]',
                'div[data-product-id]',
                'article[class*="product"]',
                '.list--item--main',
                # Autres sélecteurs communs
                'div.manhattan--container--product',
            ]

            products = []
            for selector in product_selectors:
                try:
                    products = await page.query_selector_all(selector)
                    if len(products) > 0:
                        context.log.info(f"✅ {len(products)} produits trouvés avec: {selector}")
                        break
                except:
                    continue

            if not products:
                context.log.warning("⚠️ Aucun produit trouvé avec les sélecteurs standards")
                # Essayer de trouver tous les liens de produits
                products = await page.query_selector_all('a[href*="/item/"]')
                if products:
                    context.log.info(f"✅ {len(products)} liens de produits trouvés")

            # Limiter au nombre souhaité
            products = products[:max_results]
            context.log.info(f"📊 Traitement de {len(products)} produits...")

            for idx, product in enumerate(products):
                try:
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
                    title = f"Product {idx + 1}"
                    title_selectors = [
                        'h1', 'h2', 'h3',
                        '[class*="title"]',
                        '[class*="name"]',
                        '[class*="product-title"]',
                    ]

                    for selector in title_selectors:
                        try:
                            title_elem = await product.query_selector(selector)
                            if title_elem:
                                title_text = await title_elem.inner_text()
                                if title_text and len(title_text.strip()) > 0:
                                    title = title_text.strip()
                                    break
                        except:
                            continue

                    # Extraire le prix
                    price = "N/A"
                    price_selectors = [
                        '[class*="price"]',
                        '[class*="amount"]',
                        'span:has-text("$")',
                        'span:has-text("€")',
                    ]

                    for selector in price_selectors:
                        try:
                            price_elem = await product.query_selector(selector)
                            if price_elem:
                                price_text = await price_elem.inner_text()
                                if price_text:
                                    price = price_text.strip()
                                    break
                        except:
                            continue

                    # Extraire l'image principale
                    src_image = ""
                    img_elem = await product.query_selector('img')
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        if not src:
                            src = await img_elem.get_attribute('data-src')
                        if not src:
                            src = await img_elem.get_attribute('data-lazy-src')
                        if src:
                            if not src.startswith('http'):
                                src_image = urljoin(url, src)
                            else:
                                src_image = src

                    # Télécharger l'image
                    product_image_paths = []
                    if src_image:
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

                    context.log.info(f"✅ Produit {idx + 1}/{len(products)}: {title[:50]}")

                except Exception as e:
                    context.log.error(f"❌ Erreur produit {idx}: {e}")
                    continue

            context.log.info(f"🎉 Extraction terminée: {len(self.product_data_list)} produits extraits")

        except Exception as e:
            context.log.error(f"❌ Erreur lors de l'extraction des produits: {e}")

    async def _download_image(self, page: Page, image_url: str) -> str:
        """Télécharger une image et retourner le chemin local"""
        try:
            # Créer un nom de fichier unique
            self.image_counter += 1
            ext = '.jpg'
            if '.' in image_url:
                parsed = urlparse(image_url)
                ext = os.path.splitext(parsed.path)[1] or '.jpg'
            filename = f"image_{self.image_counter:04d}{ext}"
            filepath = self.images_dir / filename

            # Télécharger l'image
            try:
                response = await page.request.get(image_url, timeout=10000)
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.body())
                    return str(filepath)
            except Exception as e:
                print(f"Erreur téléchargement {image_url}: {e}")

        except Exception as e:
            print(f"Erreur lors du téléchargement de {image_url}: {e}")

        return ""


async def search_aliexpress_by_image(
    image_path: str,
    output_dir: str = "output",
    max_results: int = 20
) -> Tuple[List[ImageMetadata], List[ProductData]]:
    """
    Fonction utilitaire pour rechercher sur AliExpress par image

    Args:
        image_path: Chemin vers l'image à rechercher
        output_dir: Répertoire de sortie
        max_results: Nombre maximum de résultats

    Returns:
        Tuple contenant les listes de ImageMetadata et ProductData
    """
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, max_results)
