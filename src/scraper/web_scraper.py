"""
Module de scraping web utilisant Crawlee
"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

from src.models.data_models import ImageMetadata, ProductData


class WebScraper:
    """Scraper web utilisant Crawlee pour extraire les données de produits"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.image_metadata_list: List[ImageMetadata] = []
        self.product_data_list: List[ProductData] = []
        self.image_counter = 0

    async def scrape_page(
        self,
        url: str,
        max_requests: int = 50,
        headless: bool = True
    ) -> tuple[List[ImageMetadata], List[ProductData]]:
        """
        Scraper une page web pour extraire les produits et images

        Args:
            url: URL de la page à scraper
            max_requests: Nombre maximum de requêtes
            headless: Mode headless pour le navigateur

        Returns:
            Tuple contenant les listes de ImageMetadata et ProductData
        """
        self.image_metadata_list = []
        self.product_data_list = []
        self.image_counter = 0

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=max_requests,
            headless=headless,
        )

        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            await self._handle_page(context)

        await crawler.run([url])

        return self.image_metadata_list, self.product_data_list

    async def _handle_page(self, context: PlaywrightCrawlingContext):
        """Handler pour traiter chaque page"""
        page = context.page
        url = context.request.url

        context.log.info(f'Scraping: {url}')

        # Attendre que la page soit complètement chargée
        await page.wait_for_load_state('networkidle')

        # Extraire les images de la page
        images = await page.query_selector_all('img')

        for img in images:
            try:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt') or ''

                if src:
                    # Résoudre l'URL relative
                    full_src = urljoin(url, src)

                    # Créer ImageMetadata
                    img_metadata = ImageMetadata(
                        src=full_src,
                        link=url
                    )
                    self.image_metadata_list.append(img_metadata)

                    # Télécharger l'image
                    image_path = await self._download_image(page, full_src)

            except Exception as e:
                context.log.error(f'Erreur lors du traitement de l\'image: {e}')

        # Extraire les données de produit
        # Vous pouvez personnaliser cette partie selon la structure du site
        await self._extract_product_data(context, url)

    async def _download_image(self, page, image_url: str) -> str:
        """Télécharger une image et retourner le chemin local"""
        try:
            # Créer un nom de fichier unique
            self.image_counter += 1
            parsed_url = urlparse(image_url)
            ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
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

    async def _extract_product_data(self, context: PlaywrightCrawlingContext, url: str):
        """
        Extraire les données de produit de la page

        Cette méthode peut être personnalisée selon la structure du site web cible
        """
        page = context.page

        try:
            # Exemple générique - à adapter selon le site cible
            # Rechercher les conteneurs de produits communs
            product_selectors = [
                '.product',
                '.product-item',
                '[data-product]',
                'article.product',
                '.item-product'
            ]

            products = []
            for selector in product_selectors:
                products = await page.query_selector_all(selector)
                if products:
                    break

            if not products:
                # Si aucun produit n'est trouvé, créer une entrée pour la page entière
                await self._create_page_product_data(context, url)
                return

            # Traiter chaque produit trouvé
            for idx, product in enumerate(products):
                try:
                    # Extraire les informations du produit
                    title_elem = await product.query_selector('h1, h2, h3, .product-title, .title')
                    title = await title_elem.inner_text() if title_elem else f"Product {idx + 1}"

                    desc_elem = await product.query_selector('.description, .product-description, p')
                    description = await desc_elem.inner_text() if desc_elem else ""

                    price_elem = await product.query_selector('.price, .product-price, [class*="price"]')
                    price = await price_elem.inner_text() if price_elem else "N/A"

                    # Extraire l'image principale
                    img_elem = await product.query_selector('img')
                    src_image = ""
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        if src:
                            src_image = urljoin(url, src)

                    # Extraire toutes les images du produit
                    product_images = await product.query_selector_all('img')
                    product_image_paths = []
                    for img in product_images:
                        src = await img.get_attribute('src')
                        if src:
                            full_src = urljoin(url, src)
                            img_path = await self._download_image(page, full_src)
                            if img_path:
                                product_image_paths.append(img_path)

                    # Prendre une capture d'écran du produit
                    screenshot_filename = f"screenshot_product_{len(self.product_data_list) + 1}.png"
                    screenshot_path = self.images_dir / screenshot_filename
                    await product.screenshot(path=str(screenshot_path))

                    # Créer ProductData
                    product_data = ProductData(
                        item_url=url,
                        collection_date=datetime.now(),
                        src_image=src_image,
                        title=title.strip(),
                        description=description.strip(),
                        price=price.strip(),
                        screenshot_path=str(screenshot_path),
                        product_image_paths=product_image_paths
                    )
                    self.product_data_list.append(product_data)

                except Exception as e:
                    context.log.error(f'Erreur lors de l\'extraction du produit {idx}: {e}')

        except Exception as e:
            context.log.error(f'Erreur lors de l\'extraction des produits: {e}')

    async def _create_page_product_data(self, context: PlaywrightCrawlingContext, url: str):
        """Créer une entrée ProductData pour la page entière si aucun produit n'est trouvé"""
        page = context.page

        try:
            # Extraire le titre de la page
            title = await page.title()

            # Extraire la description (meta description)
            description_elem = await page.query_selector('meta[name="description"]')
            description = ""
            if description_elem:
                description = await description_elem.get_attribute('content') or ""

            # Extraire l'image principale (og:image)
            og_image_elem = await page.query_selector('meta[property="og:image"]')
            src_image = ""
            if og_image_elem:
                src_image = await og_image_elem.get_attribute('content') or ""
                if src_image:
                    src_image = urljoin(url, src_image)

            # Extraire toutes les images de la page
            images = await page.query_selector_all('img')
            product_image_paths = []
            for img in images[:10]:  # Limiter à 10 images
                src = await img.get_attribute('src')
                if src:
                    full_src = urljoin(url, src)
                    img_path = await self._download_image(page, full_src)
                    if img_path:
                        product_image_paths.append(img_path)

            # Prendre une capture d'écran de la page
            screenshot_filename = f"screenshot_page_{len(self.product_data_list) + 1}.png"
            screenshot_path = self.images_dir / screenshot_filename
            await page.screenshot(path=str(screenshot_path), full_page=True)

            # Créer ProductData
            product_data = ProductData(
                item_url=url,
                collection_date=datetime.now(),
                src_image=src_image,
                title=title,
                description=description,
                price="N/A",
                screenshot_path=str(screenshot_path),
                product_image_paths=product_image_paths
            )
            self.product_data_list.append(product_data)

        except Exception as e:
            context.log.error(f'Erreur lors de la création des données de page: {e}')


async def scrape_url(url: str, output_dir: str = "output", max_requests: int = 50) -> tuple[List[ImageMetadata], List[ProductData]]:
    """
    Fonction utilitaire pour scraper une URL

    Args:
        url: URL à scraper
        output_dir: Répertoire de sortie
        max_requests: Nombre maximum de requêtes

    Returns:
        Tuple contenant les listes de ImageMetadata et ProductData
    """
    scraper = WebScraper(output_dir)
    return await scraper.scrape_page(url, max_requests)
