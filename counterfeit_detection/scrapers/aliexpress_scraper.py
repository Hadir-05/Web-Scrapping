"""
AliExpress scraper for counterfeit detection
"""
from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import re
import logging

logger = logging.getLogger(__name__)


class AliExpressScraper(BaseScraper):
    """Scraper pour AliExpress"""

    @property
    def base_url(self) -> str:
        return "https://www.aliexpress.com"

    @property
    def site_name(self) -> str:
        return "AliExpress"

    def search(self, query: str, max_pages: int = 5) -> List[Dict]:
        """
        Recherche des produits sur AliExpress

        Args:
            query: Requête de recherche (ex: "Louis Vuitton bag")
            max_pages: Nombre maximum de pages

        Returns:
            Liste de produits
        """
        products = []

        logger.info(f"Searching AliExpress for: {query}")

        for page in range(1, max_pages + 1):
            # URL de recherche AliExpress
            search_url = f"{self.base_url}/w/wholesale-{query.replace(' ', '-')}.html"

            if page > 1:
                search_url += f"?page={page}"

            soup = self.fetch_page(search_url)

            if not soup:
                logger.warning(f"Failed to fetch page {page}")
                continue

            # Extraire les produits
            # Note: Les sélecteurs peuvent changer, il faut les adapter
            product_items = soup.select('div.list--gallery--C2f2tvm a.multi--container--1UZxxHY')

            if not product_items:
                logger.warning(f"No products found on page {page}")
                break

            for item in product_items:
                try:
                    product_data = self._extract_product_from_listing(item)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Error extracting product: {str(e)}")
                    continue

            logger.info(f"Page {page}: Found {len(product_items)} products")

        logger.info(f"Total products found: {len(products)}")
        return products

    def _extract_product_from_listing(self, item) -> Optional[Dict]:
        """Extrait les données d'un produit depuis la liste de résultats"""

        try:
            # URL du produit
            url = item.get('href', '')
            if url and not url.startswith('http'):
                url = self.base_url + url

            # Titre
            title_elem = item.select_one('h3, h1, .multi--titleText')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Prix
            price_elem = item.select_one('.multi--price-sale, .mGXnE_')
            price_str = price_elem.get_text(strip=True) if price_elem else ''
            price = self.clean_price(price_str)

            # Images
            img_elem = item.select_one('img')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else ''

            if image_url and image_url.startswith('//'):
                image_url = 'https:' + image_url

            # Vendeur (si disponible)
            seller_elem = item.select_one('.store-name, .seller')
            seller_name = seller_elem.get_text(strip=True) if seller_elem else ''

            if not title or not url:
                return None

            return {
                'title': title,
                'url': url,
                'price': price,
                'currency': 'USD',  # AliExpress affiche généralement en USD
                'image_urls': [image_url] if image_url else [],
                'seller_name': seller_name,
                'source_site': self.site_name
            }

        except Exception as e:
            logger.error(f"Error in _extract_product_from_listing: {str(e)}")
            return None

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Récupère les détails complets d'un produit

        Args:
            product_url: URL du produit

        Returns:
            Dictionnaire avec les détails
        """
        soup = self.fetch_page(product_url)

        if not soup:
            return None

        try:
            # Titre
            title_elem = soup.select_one('h1.product-title-text, h1')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Prix
            price_elem = soup.select_one('.product-price-value, .uniform-banner-box-price')
            price_str = price_elem.get_text(strip=True) if price_elem else ''
            price = self.clean_price(price_str)

            # Description
            desc_elem = soup.select_one('.product-description, .detail-desc')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Images
            image_selectors = [
                'img.magnifier-image',
                '.images-view-list img',
                'ul.images-view-list img'
            ]
            images = self.extract_images(soup, image_selectors)

            # Vendeur
            seller_elem = soup.select_one('.shop-name a, .seller-info .name')
            seller_name = seller_elem.get_text(strip=True) if seller_elem else ''

            seller_url_elem = soup.select_one('.shop-name a')
            seller_url = seller_url_elem.get('href', '') if seller_url_elem else ''
            if seller_url and not seller_url.startswith('http'):
                seller_url = self.base_url + seller_url

            # Évaluations
            rating_elem = soup.select_one('.overview-rating-average')
            rating_str = rating_elem.get_text(strip=True) if rating_elem else '0'

            try:
                rating = float(re.search(r'[\d.]+', rating_str).group())
            except:
                rating = 0.0

            return {
                'title': title,
                'url': product_url,
                'price': price,
                'currency': 'USD',
                'description': description[:1000],  # Limiter la longueur
                'image_urls': images[:10],  # Max 10 images
                'seller_name': seller_name,
                'seller_url': seller_url,
                'rating': rating,
                'source_site': self.site_name
            }

        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return None
