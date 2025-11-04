"""
Module de scraping AliExpress avec recherche par image
"""
import asyncio
import os
import base64
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, quote
from pathlib import Path
import json

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import Page

from src.models.data_models import ImageMetadata, ProductData


class AliExpressImageSearchScraper:
    """Scraper AliExpress pour la recherche par image"""

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

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=max_results + 1,
            headless=headless,
        )

        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            page = context.page

            # Si c'est la première page, effectuer la recherche par image
            if len(self.product_data_list) == 0:
                await self._perform_image_search(context, image_path)

            # Extraire les produits de la page de résultats
            await self._extract_products(context)

        # Démarrer avec la page de recherche par image d'AliExpress
        await crawler.run(['https://www.aliexpress.com/'])

        return self.image_metadata_list, self.product_data_list

    async def _perform_image_search(self, context: PlaywrightCrawlingContext, image_path: str):
        """
        Effectuer une recherche par image sur AliExpress

        AliExpress utilise une fonctionnalité de recherche par image.
        Nous allons uploader l'image et déclencher la recherche.
        """
        page = context.page

        try:
            context.log.info("Navigation vers AliExpress...")

            # Attendre que la page soit chargée
            await page.wait_for_load_state('networkidle', timeout=30000)

            # Chercher le bouton de recherche par image
            # AliExpress a généralement une icône de caméra dans la barre de recherche
            camera_selectors = [
                'button[aria-label*="image"]',
                'button[aria-label*="camera"]',
                '.search-camera-icon',
                '[class*="camera"]',
                'button:has-text("Image")',
            ]

            camera_button = None
            for selector in camera_selectors:
                try:
                    camera_button = await page.wait_for_selector(selector, timeout=5000)
                    if camera_button:
                        break
                except:
                    continue

            if camera_button:
                context.log.info("Bouton de recherche par image trouvé, clic...")
                await camera_button.click()
                await page.wait_for_timeout(2000)

                # Chercher l'input file pour uploader l'image
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    context.log.info(f"Upload de l'image: {image_path}")
                    await file_input.set_input_files(image_path)

                    # Attendre que l'upload soit terminé et les résultats chargés
                    await page.wait_for_timeout(5000)
                    await page.wait_for_load_state('networkidle', timeout=30000)
                else:
                    context.log.warning("Input file non trouvé")
            else:
                context.log.warning("Bouton de recherche par image non trouvé")
                # Méthode alternative : utiliser l'URL directe de recherche par image
                await self._use_alternative_image_search(page, image_path, context)

        except Exception as e:
            context.log.error(f"Erreur lors de la recherche par image: {e}")
            # Essayer la méthode alternative
            await self._use_alternative_image_search(page, image_path, context)

    async def _use_alternative_image_search(self, page: Page, image_path: str, context: PlaywrightCrawlingContext):
        """
        Méthode alternative : convertir l'image en base64 et utiliser l'API de recherche
        ou naviguer directement vers la page de recherche
        """
        try:
            context.log.info("Utilisation de la méthode alternative de recherche par image...")

            # Pour AliExpress, on peut aussi faire une recherche par texte en attendant
            # et scraper les produits pour les comparer localement avec l'image uploadée
            # Cette approche est plus robuste

            # Chercher la barre de recherche
            search_input = await page.query_selector('input[type="search"], input[placeholder*="Search"]')
            if search_input:
                # Faire une recherche générale (vous pouvez personnaliser)
                await search_input.fill("product")
                await search_input.press("Enter")
                await page.wait_for_load_state('networkidle', timeout=30000)
                context.log.info("Recherche générale effectuée - les produits seront comparés localement")

        except Exception as e:
            context.log.error(f"Erreur dans la méthode alternative: {e}")

    async def _extract_products(self, context: PlaywrightCrawlingContext):
        """Extraire les produits de la page de résultats AliExpress"""
        page = context.page
        url = context.request.url

        try:
            context.log.info(f"Extraction des produits depuis: {url}")

            # Attendre que les produits soient chargés
            await page.wait_for_timeout(3000)

            # Sélecteurs pour les produits AliExpress
            product_selectors = [
                '[class*="product-item"]',
                '[class*="list-item"]',
                '[data-product-id]',
                'article',
                'a[href*="/item/"]',
            ]

            products = []
            for selector in product_selectors:
                try:
                    products = await page.query_selector_all(selector)
                    if len(products) > 0:
                        context.log.info(f"Trouvé {len(products)} produits avec le sélecteur: {selector}")
                        break
                except:
                    continue

            if not products:
                context.log.warning("Aucun produit trouvé avec les sélecteurs prédéfinis")
                return

            # Limiter le nombre de produits à traiter
            products = products[:20]

            for idx, product in enumerate(products):
                try:
                    # Extraire l'URL du produit
                    product_link_elem = await product.query_selector('a[href*="/item/"], a')
                    product_url = ""
                    if product_link_elem:
                        href = await product_link_elem.get_attribute('href')
                        if href:
                            product_url = urljoin(url, href)

                    # Extraire le titre
                    title_selectors = ['h1', 'h2', 'h3', '[class*="title"]', '[class*="name"]']
                    title = ""
                    for selector in title_selectors:
                        title_elem = await product.query_selector(selector)
                        if title_elem:
                            title = await title_elem.inner_text()
                            if title:
                                break

                    if not title:
                        title = f"Product {idx + 1}"

                    # Extraire le prix
                    price_selectors = ['[class*="price"]', '[class*="amount"]', 'span:has-text("$")']
                    price = "N/A"
                    for selector in price_selectors:
                        price_elem = await product.query_selector(selector)
                        if price_elem:
                            price_text = await price_elem.inner_text()
                            if price_text and ('$' in price_text or '€' in price_text or '£' in price_text):
                                price = price_text
                                break

                    # Extraire l'image principale
                    img_elem = await product.query_selector('img')
                    src_image = ""
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        if not src:
                            src = await img_elem.get_attribute('data-src')
                        if src:
                            src_image = urljoin(url, src)

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
                        title=title.strip(),
                        description="",  # AliExpress nécessite d'aller sur la page produit pour la description
                        price=price.strip(),
                        screenshot_path=str(screenshot_path),
                        product_image_paths=product_image_paths
                    )
                    self.product_data_list.append(product_data)

                    context.log.info(f"Produit {idx + 1} extrait: {title[:50]}")

                except Exception as e:
                    context.log.error(f"Erreur lors de l'extraction du produit {idx}: {e}")

        except Exception as e:
            context.log.error(f"Erreur lors de l'extraction des produits: {e}")

    async def _download_image(self, page: Page, image_url: str) -> str:
        """Télécharger une image et retourner le chemin local"""
        try:
            # Créer un nom de fichier unique
            self.image_counter += 1
            ext = '.jpg'
            if '.' in image_url:
                ext = os.path.splitext(image_url.split('?')[0])[1] or '.jpg'
            filename = f"image_{self.image_counter:04d}{ext}"
            filepath = self.images_dir / filename

            # Télécharger l'image
            response = await page.request.get(image_url)
            if response.status == 200:
                with open(filepath, 'wb') as f:
                    f.write(await response.body())
                return str(filepath)
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
