"""
Module de scraping AliExpress avec recherche hybride (catégorie + image)
"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, quote, urlparse
from pathlib import Path

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import Page

from src.models.data_models import ImageMetadata, ProductData


class AliExpressImageSearchScraper:
    """Scraper AliExpress avec recherche hybride (catégorie + comparaison d'images)"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.image_metadata_list: List[ImageMetadata] = []
        self.product_data_list: List[ProductData] = []
        self.image_counter = 0

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
            max_results: Nombre maximum de résultats
            headless: Mode headless pour le navigateur

        Returns:
            Tuple contenant les listes de ImageMetadata et ProductData
        """
        self.image_metadata_list = []
        self.product_data_list = []
        self.image_counter = 0

        # Si pas de catégorie, utiliser "product"
        if not category:
            category = "product"

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1,
            headless=headless,
            browser_type='chromium',
        )

        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            page = context.page

            # Effectuer la recherche par catégorie et extraire les résultats
            await self._search_by_category_and_extract(context, category, max_results)

        # Démarrer avec la page principale d'AliExpress
        await crawler.run(['https://www.aliexpress.com/'])

        return self.image_metadata_list, self.product_data_list

    async def _search_by_category_and_extract(
        self,
        context: PlaywrightCrawlingContext,
        category: str,
        max_results: int
    ):
        """
        Effectuer une recherche par catégorie sur AliExpress
        """
        page = context.page

        try:
            context.log.info(f"🌐 Navigation vers AliExpress...")

            # Attendre le chargement
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            context.log.info(f"🔍 Recherche de produits dans la catégorie: {category}")

            # Chercher la barre de recherche
            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="Search"]',
                'input[placeholder*="search"]',
                'input.search-bar-input',
                'input[class*="search"]',
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await page.wait_for_selector(selector, timeout=5000)
                    if search_input and await search_input.is_visible():
                        context.log.info(f"✅ Barre de recherche trouvée: {selector}")
                        break
                except:
                    continue

            if search_input:
                # Remplir la recherche avec la catégorie
                context.log.info(f"⌨️  Saisie de la catégorie: {category}")
                await search_input.fill(category)
                await page.wait_for_timeout(1000)

                # Appuyer sur Entrée ou chercher le bouton de recherche
                try:
                    await search_input.press("Enter")
                    context.log.info("↩️  Envoi de la recherche...")
                except:
                    # Essayer de cliquer sur le bouton de recherche
                    search_button = await page.query_selector('button[type="submit"], button.search-button')
                    if search_button:
                        await search_button.click()

                # Attendre les résultats
                context.log.info("⏳ Attente des résultats...")
                await page.wait_for_timeout(5000)

                try:
                    await page.wait_for_load_state('networkidle', timeout=30000)
                except:
                    await page.wait_for_timeout(3000)

                # Extraire les produits
                context.log.info("📦 Extraction des produits...")
                await self._extract_products_from_results(context, max_results)

            else:
                context.log.error("❌ Impossible de trouver la barre de recherche")
                # Fallback : utiliser l'URL directe de recherche
                search_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html"
                context.log.info(f"🔗 Tentative avec URL directe: {search_url}")
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(5000)
                await self._extract_products_from_results(context, max_results)

        except Exception as e:
            context.log.error(f"❌ Erreur lors de la recherche: {e}")
            # Dernier recours : URL directe
            try:
                search_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html"
                context.log.info(f"🔗 Dernier recours avec URL: {search_url}")
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(5000)
                await self._extract_products_from_results(context, max_results)
            except Exception as e2:
                context.log.error(f"❌ Échec complet: {e2}")

    async def _extract_products_from_results(self, context: PlaywrightCrawlingContext, max_results: int):
        """
        Extraire les produits depuis la page de résultats
        """
        page = context.page
        url = page.url

        try:
            context.log.info(f"📄 Extraction depuis: {url}")

            # Attendre que les produits soient chargés
            await page.wait_for_timeout(3000)

            # Scroll pour charger plus de produits (lazy loading)
            context.log.info("📜 Scroll pour charger les produits...")
            for i in range(3):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(1000)

            # Sélecteurs pour les cartes de produits AliExpress
            product_selectors = [
                # Nouveaux sélecteurs AliExpress 2024/2025
                'div[class*="search-card-item"]',
                'div[class*="product-card"]',
                'a[class*="search-card-item"]',
                'div[class*="list--item"]',
                'div[data-product-id]',
                'article[class*="product"]',
                '.list--item',
                'div.manhattan--container--product',
                # Liens de produits directs
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
                context.log.warning("⚠️ Aucun produit trouvé avec les sélecteurs standards")
                # Screenshot pour debug
                debug_path = self.output_dir / "debug_no_products.png"
                await page.screenshot(path=str(debug_path))
                context.log.info(f"📸 Screenshot de debug sauvegardé: {debug_path}")
                return

            # Limiter au nombre souhaité
            products = products[:max_results]
            context.log.info(f"📊 Traitement de {len(products)} produits...")

            for idx, product in enumerate(products):
                try:
                    # Scroll vers le produit pour s'assurer qu'il est visible
                    try:
                        await product.scroll_into_view_if_needed()
                        await page.wait_for_timeout(500)
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
                    title = f"Product {idx + 1}"
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
                                # Essayer d'abord le titre en attribut
                                title_attr = await title_elem.get_attribute('title')
                                if title_attr and len(title_attr.strip()) > 0:
                                    title = title_attr.strip()
                                    break
                                # Sinon prendre le texte
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
                        # Essayer plusieurs attributs pour l'image
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
                    if src_image and 'data:image' not in src_image:  # Éviter les images data:
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
                # Nettoyer l'extension
                if '?' in ext:
                    ext = ext.split('?')[0]
                if not ext.startswith('.'):
                    ext = '.jpg'
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
        max_results: Nombre maximum de résultats

    Returns:
        Tuple contenant les listes de ImageMetadata et ProductData
    """
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, category, max_results)
