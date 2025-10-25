"""
DHgate scraper for counterfeit detection
"""
from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class DHgateScraper(BaseScraper):
    """Scraper pour DHgate"""

    @property
    def base_url(self) -> str:
        return "https://www.dhgate.com"

    @property
    def site_name(self) -> str:
        return "DHgate"

    def search(self, query: str, max_pages: int = 5) -> List[Dict]:
        """
        Recherche des produits sur DHgate

        Args:
            query: Requête de recherche
            max_pages: Nombre maximum de pages

        Returns:
            Liste de produits
        """
        products = []

        logger.info(f"Searching DHgate for: {query}")

        for page in range(1, max_pages + 1):
            # URL de recherche DHgate
            search_url = f"{self.base_url}/wholesale/search.do?act=search&sus=&searchkey={query.replace(' ', '+')}&catalog=#hpf101-1"

            if page > 1:
                search_url += f"&page={page}"

            soup = self.fetch_page(search_url)

            if not soup:
                logger.warning(f"Failed to fetch page {page}")
                continue

            # Extraire les produits
            product_items = soup.select('li.proInfoInner, div.product-item')

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
        """Extrait les données d'un produit depuis la liste"""

        try:
            # URL
            url_elem = item.select_one('a.proThumb, a')
            url = url_elem.get('href', '') if url_elem else ''

            if url and not url.startswith('http'):
                url = self.base_url + url

            # Titre
            title_elem = item.select_one('.proName, .item-title')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Prix
            price_elem = item.select_one('.price, .item-price')
            price_str = price_elem.get_text(strip=True) if price_elem else ''
            price = self.clean_price(price_str)

            # Image
            img_elem = item.select_one('img.pic')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else ''

            if image_url and image_url.startswith('//'):
                image_url = 'https:' + image_url

            # Vendeur
            seller_elem = item.select_one('.store-name, .seller-info')
            seller_name = seller_elem.get_text(strip=True) if seller_elem else ''

            if not title or not url:
                return None

            return {
                'title': title,
                'url': url,
                'price': price,
                'currency': 'USD',
                'image_urls': [image_url] if image_url else [],
                'seller_name': seller_name,
                'source_site': self.site_name
            }

        except Exception as e:
            logger.error(f"Error in _extract_product_from_listing: {str(e)}")
            return None

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """Récupère les détails d'un produit DHgate"""

        soup = self.fetch_page(product_url)

        if not soup:
            return None

        try:
            # Titre
            title_elem = soup.select_one('h1.proTitle, h1')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # Prix
            price_elem = soup.select_one('.price, .itemPrice')
            price_str = price_elem.get_text(strip=True) if price_elem else ''
            price = self.clean_price(price_str)

            # Description
            desc_elem = soup.select_one('.proDetailt, .product-desc')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Images
            image_selectors = [
                'img.pic-thumb',
                '.gallery img',
                'ul.pic-small img'
            ]
            images = self.extract_images(soup, image_selectors)

            # Vendeur
            seller_elem = soup.select_one('.store-name a')
            seller_name = seller_elem.get_text(strip=True) if seller_elem else ''
            seller_url = seller_elem.get('href', '') if seller_elem else ''

            return {
                'title': title,
                'url': product_url,
                'price': price,
                'currency': 'USD',
                'description': description[:1000],
                'image_urls': images[:10],
                'seller_name': seller_name,
                'seller_url': seller_url,
                'source_site': self.site_name
            }

        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return None
