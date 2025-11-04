"""
Module de scraping AliExpress avec recherche hybride - VERSION ROBUSTE
"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, quote, urlparse
from pathlib import Path
import math
import re

from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import Page

from src.models.data_models import ImageMetadata, ProductData


class AliExpressImageSearchScraper:
    """Scraper AliExpress avec recherche hybride - VERSION ROBUSTE avec debug"""

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
        """
        self.image_metadata_list = []
        self.product_data_list = []
        self.image_counter = 0
        self.current_page = 1
        self.target_results = max_results

        if not category:
            category = "product"

        # Calculer le nombre de pages
        products_per_page = 40
        estimated_pages = math.ceil(max_results / products_per_page)
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
            await self._extract_products_from_current_page(context)

            if len(self.product_data_list) < self.target_results and self.current_page == 1:
                await self._enqueue_next_pages(context, category, max_pages)

        # URL directe de recherche
        search_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html"

        await crawler.run([search_url])

        return self.image_metadata_list, self.product_data_list

    async def _enqueue_next_pages(self, context: PlaywrightCrawlingContext, category: str, max_pages: int):
        """Ajouter les URLs des pages suivantes"""
        try:
            for page_num in range(2, max_pages + 1):
                next_url = f"https://www.aliexpress.com/w/wholesale-{quote(category)}.html?page={page_num}"
                context.log.info(f"📑 Ajout page {page_num}")
                await context.add_requests([next_url])
        except Exception as e:
            context.log.error(f"❌ Erreur ajout pages: {e}")

    async def _extract_products_from_current_page(self, context: PlaywrightCrawlingContext):
        """Extraire les produits - VERSION ROBUSTE"""
        page = context.page
        url = page.url

        try:
            # Déterminer le numéro de page
            if 'page=' in url:
                try:
                    page_param = url.split('page=')[1].split('&')[0]
                    self.current_page = int(page_param)
                except:
                    pass

            context.log.info(f"📄 PAGE {self.current_page}: {url}")

            # Attendre le chargement
            context.log.info("⏳ Attente du chargement...")
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)  # Plus de temps pour charger

            # Screenshot initial
            debug_path_1 = self.output_dir / f"debug_page{self.current_page}_initial.png"
            await page.screenshot(path=str(debug_path_1), full_page=False)
            context.log.info(f"📸 Screenshot initial: {debug_path_1}")

            # Scroll massif pour charger tout
            context.log.info("📜 Scroll massif...")
            for i in range(10):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(500)

            # Attendre encore
            await page.wait_for_timeout(3000)

            # Screenshot après scroll
            debug_path_2 = self.output_dir / f"debug_page{self.current_page}_scrolled.png"
            await page.screenshot(path=str(debug_path_2), full_page=False)
            context.log.info(f"📸 Screenshot après scroll: {debug_path_2}")

            # MÉTHODE 1: Chercher TOUS les liens vers /item/
            context.log.info("🔍 MÉTHODE 1: Recherche de tous les liens /item/...")
            all_links = await page.query_selector_all('a[href*="/item/"]')
            context.log.info(f"   → Trouvé {len(all_links)} liens /item/")

            # MÉTHODE 2: Chercher toutes les images
            context.log.info("🔍 MÉTHODE 2: Recherche de toutes les images...")
            all_images = await page.query_selector_all('img[src*="alicdn"], img[data-src*="alicdn"]')
            context.log.info(f"   → Trouvé {len(all_images)} images alicdn")

            # MÉTHODE 3: Sélecteurs larges
            context.log.info("🔍 MÉTHODE 3: Sélecteurs larges...")
            broad_selectors = [
                'div[class*="item"]',
                'div[class*="card"]',
                'div[class*="product"]',
                'a[href*="/item/"]',
            ]

            products = []
            for selector in broad_selectors:
                try:
                    products = await page.query_selector_all(selector)
                    if len(products) > 10:  # Au moins 10 éléments
                        context.log.info(f"   ✅ {len(products)} éléments avec: {selector}")
                        break
                except:
                    continue

            # Si toujours rien, utiliser les liens directs
            if not products or len(products) < 5:
                context.log.warning(f"⚠️ Peu d'éléments trouvés, utilisation des liens directs")
                products = all_links

            if not products or len(products) == 0:
                context.log.error(f"❌ AUCUN PRODUIT TROUVÉ sur page {self.current_page}")

                # Debug: Afficher le HTML
                html_content = await page.content()
                debug_html_path = self.output_dir / f"debug_page{self.current_page}.html"
                with open(debug_html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                context.log.info(f"📝 HTML sauvegardé: {debug_html_path}")

                # Chercher des patterns dans le HTML
                if '/item/' in html_content:
                    count = html_content.count('/item/')
                    context.log.info(f"   ℹ️ HTML contient {count} références à '/item/'")

                return

            context.log.info(f"📊 Traitement de {len(products)} éléments...")

            # Traiter chaque élément
            processed = 0
            for idx, element in enumerate(products):
                if len(self.product_data_list) >= self.target_results:
                    context.log.info(f"🎯 Objectif atteint: {len(self.product_data_list)}")
                    break

                try:
                    # Scroll vers l'élément
                    try:
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(200)
                    except:
                        pass

                    # Extraire URL
                    product_url = ""
                    try:
                        href = await element.get_attribute('href')
                        if href and '/item/' in href:
                            product_url = href if href.startswith('http') else urljoin(url, href)
                    except:
                        pass

                    if not product_url:
                        # Chercher un lien enfant
                        link = await element.query_selector('a[href*="/item/"]')
                        if link:
                            href = await link.get_attribute('href')
                            if href:
                                product_url = href if href.startswith('http') else urljoin(url, href)

                    # Si pas d'URL de produit, passer
                    if not product_url or '/item/' not in product_url:
                        continue

                    # Extraire le titre
                    title = f"Product {len(self.product_data_list) + 1}"

                    # Essayer plusieurs méthodes
                    try:
                        # Méthode 1: attribut title
                        title_attr = await element.get_attribute('title')
                        if title_attr and len(title_attr) > 3:
                            title = title_attr.strip()
                        else:
                            # Méthode 2: texte de l'élément
                            text = await element.inner_text()
                            if text and len(text) > 3:
                                # Prendre les premières lignes non vides
                                lines = [l.strip() for l in text.split('\n') if l.strip()]
                                if lines:
                                    title = lines[0][:100]
                    except:
                        pass

                    # Extraire le prix
                    price = "N/A"
                    try:
                        text = await element.inner_text()
                        # Chercher pattern de prix
                        price_patterns = [
                            r'\$[\d,]+\.?\d*',
                            r'US \$[\d,]+\.?\d*',
                            r'€[\d,]+\.?\d*',
                            r'[\d,]+\.?\d*\s*USD'
                        ]
                        for pattern in price_patterns:
                            match = re.search(pattern, text)
                            if match:
                                price = match.group(0)
                                break
                    except:
                        pass

                    # Extraire l'image
                    src_image = ""
                    try:
                        img = await element.query_selector('img')
                        if img:
                            for attr in ['src', 'data-src', 'data-lazy-src']:
                                src = await img.get_attribute(attr)
                                if src and ('alicdn' in src or 'http' in src) and 'data:image' not in src:
                                    src_image = src if src.startswith('http') else urljoin(url, src)
                                    break
                    except:
                        pass

                    # Télécharger l'image
                    product_image_paths = []
                    if src_image:
                        img_path = await self._download_image(page, src_image)
                        if img_path:
                            product_image_paths.append(img_path)

                            img_metadata = ImageMetadata(
                                src=src_image,
                                link=product_url
                            )
                            self.image_metadata_list.append(img_metadata)

                    # Screenshot du produit
                    screenshot_filename = f"screenshot_product_{len(self.product_data_list) + 1}.png"
                    screenshot_path = self.images_dir / screenshot_filename
                    try:
                        await element.screenshot(path=str(screenshot_path), timeout=3000)
                    except:
                        screenshot_path = Path("")

                    # Créer ProductData
                    product_data = ProductData(
                        item_url=product_url,
                        collection_date=datetime.now(),
                        src_image=src_image,
                        title=title,
                        description="",
                        price=price,
                        screenshot_path=str(screenshot_path),
                        product_image_paths=product_image_paths
                    )
                    self.product_data_list.append(product_data)
                    processed += 1

                    if processed % 5 == 0:
                        context.log.info(f"   ✅ {len(self.product_data_list)} produits extraits")

                except Exception as e:
                    context.log.error(f"   ❌ Erreur élément {idx}: {e}")
                    continue

            context.log.info(f"🎉 Page {self.current_page} terminée: {len(self.product_data_list)} produits total")

        except Exception as e:
            context.log.error(f"❌ Erreur page {self.current_page}: {e}")
            import traceback
            context.log.error(traceback.format_exc())

    async def _download_image(self, page: Page, image_url: str) -> str:
        """Télécharger une image"""
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
            except:
                pass
        except:
            pass
        return ""


async def search_aliexpress_by_image(
    image_path: str,
    category: str = "",
    output_dir: str = "output",
    max_results: int = 20
) -> Tuple[List[ImageMetadata], List[ProductData]]:
    """Rechercher sur AliExpress"""
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, category, max_results)
