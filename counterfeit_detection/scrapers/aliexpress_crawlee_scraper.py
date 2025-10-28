"""
AliExpress scraper using Crawlee + Playwright
Cette version utilise un navigateur headless pour gérer le JavaScript d'AliExpress

Installation:
pip install crawlee[playwright]
playwright install chromium
"""

from typing import List, Dict, Optional
import asyncio
import logging
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Vérifier si Crawlee est disponible
try:
    from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
    CRAWLEE_AVAILABLE = True
except ImportError:
    CRAWLEE_AVAILABLE = False
    logger.warning("Crawlee not available. Install with: pip install crawlee[playwright]")


class AliExpressCrawleeScraper:
    """
    Scraper AliExpress moderne utilisant Crawlee + Playwright

    Avantages:
    - Gère le JavaScript d'AliExpress
    - Anti-blocking automatique
    - Retry logic intégré
    - Extraction fiable des images
    """

    def __init__(self):
        """Initialise le scraper Crawlee"""
        if not CRAWLEE_AVAILABLE:
            raise ImportError(
                "Crawlee not available. Install with:\n"
                "  pip install crawlee[playwright]\n"
                "  playwright install chromium"
            )

        self.base_url = "https://www.aliexpress.com"
        self.products = []

    async def _handle_product_page(self, context: PlaywrightCrawlingContext) -> None:
        """
        Handler pour chaque page de résultats

        Args:
            context: Contexte Crawlee avec page Playwright
        """
        page = context.page

        try:
            # Attendre que les produits se chargent
            await page.wait_for_selector('div.search-card-item, div.list--gallery--C2f2tvm', timeout=10000)

            # Extraire tous les produits de la page
            products = await page.evaluate("""
                () => {
                    const items = [];

                    // Essayer plusieurs sélecteurs (AliExpress change souvent)
                    const selectors = [
                        'div.search-card-item',
                        'div.list--gallery--C2f2tvm > div',
                        'a[class*="multi--container"]'
                    ];

                    let productElements = [];
                    for (const selector of selectors) {
                        productElements = document.querySelectorAll(selector);
                        if (productElements.length > 0) break;
                    }

                    productElements.forEach(item => {
                        try {
                            // Trouver le lien
                            const link = item.querySelector('a[href*="/item/"]') || item.querySelector('a');
                            const url = link ? link.href : '';

                            // Trouver le titre
                            const titleSelectors = [
                                'h1', 'h3',
                                '[class*="title"]',
                                '[class*="Title"]',
                                '[class*="name"]'
                            ];
                            let title = '';
                            for (const sel of titleSelectors) {
                                const elem = item.querySelector(sel);
                                if (elem && elem.textContent.trim()) {
                                    title = elem.textContent.trim();
                                    break;
                                }
                            }

                            // Trouver le prix
                            const priceSelectors = [
                                '[class*="price"]',
                                '[class*="Price"]',
                                'span.price',
                                'div.price'
                            ];
                            let price = '';
                            for (const sel of priceSelectors) {
                                const elem = item.querySelector(sel);
                                if (elem && elem.textContent.trim()) {
                                    price = elem.textContent.trim();
                                    break;
                                }
                            }

                            // Trouver l'image
                            const img = item.querySelector('img');
                            let imageUrl = '';
                            if (img) {
                                imageUrl = img.src || img.getAttribute('data-src') || img.getAttribute('srcset');
                                // Nettoyer l'URL de l'image
                                if (imageUrl) {
                                    if (imageUrl.startsWith('//')) {
                                        imageUrl = 'https:' + imageUrl;
                                    }
                                    // Enlever les paramètres de taille pour avoir la meilleure qualité
                                    imageUrl = imageUrl.split('_')[0];
                                }
                            }

                            // Trouver le rating
                            const ratingElem = item.querySelector('[class*="rating"], [class*="stars"]');
                            const rating = ratingElem ? ratingElem.textContent.trim() : '';

                            // Trouver les ventes
                            const salesElem = item.querySelector('[class*="sale"], [class*="sold"]');
                            const sales = salesElem ? salesElem.textContent.trim() : '';

                            if (url && title) {
                                items.push({
                                    title: title,
                                    url: url,
                                    price: price,
                                    image_url: imageUrl,
                                    rating: rating,
                                    sales: sales
                                });
                            }
                        } catch (e) {
                            console.error('Error extracting product:', e);
                        }
                    });

                    return items;
                }
            """)

            # Nettoyer et stocker les produits
            for product in products:
                # Extraire le prix numérique
                price_str = product.get('price', '')
                price_match = re.search(r'[\d,\.]+', price_str)
                price = float(price_match.group().replace(',', '')) if price_match else 0.0

                # Nettoyer le rating
                rating_str = product.get('rating', '')
                rating_match = re.search(r'[\d\.]+', rating_str)
                rating = float(rating_match.group()) if rating_match else 0.0

                product_data = {
                    'title': product['title'],
                    'url': product['url'],
                    'price': price,
                    'currency': 'USD',
                    'images': [product['image_url']] if product.get('image_url') else [],
                    'rating': rating,
                    'sales': product.get('sales', ''),
                    'source_site': 'AliExpress',
                    'seller_info': ''  # Peut être extrait si nécessaire
                }

                self.products.append(product_data)

            logger.info(f"Extracted {len(products)} products from page")

        except Exception as e:
            logger.error(f"Error in _handle_product_page: {e}")

    async def _search_async(self, query: str, max_pages: int = 3) -> List[Dict]:
        """
        Recherche asynchrone sur AliExpress

        Args:
            query: Terme de recherche
            max_pages: Nombre de pages à scraper

        Returns:
            Liste de produits trouvés
        """
        self.products = []

        # Construire les URLs de recherche
        search_query = quote_plus(query)
        urls = []

        for page in range(1, max_pages + 1):
            if page == 1:
                url = f"{self.base_url}/wholesale?SearchText={search_query}"
            else:
                url = f"{self.base_url}/wholesale?SearchText={search_query}&page={page}"
            urls.append(url)

        logger.info(f"Crawling {len(urls)} pages for query: '{query}'")

        # Créer le crawler
        crawler = PlaywrightCrawler(
            headless=True,  # Navigateur invisible
            browser_type='chromium',
            max_requests_per_crawl=max_pages * 10,  # Limite de sécurité
            request_handler=self._handle_product_page,
        )

        # Lancer le crawl
        try:
            await crawler.run(urls)
        except Exception as e:
            logger.error(f"Crawler error: {e}")

        logger.info(f"Total products found: {len(self.products)}")
        return self.products

    def search(self, query: str, max_pages: int = 3) -> List[Dict]:
        """
        Recherche synchrone sur AliExpress (wrapper)

        Args:
            query: Terme de recherche
            max_pages: Nombre de pages à scraper

        Returns:
            Liste de produits trouvés
        """
        # Exécuter la version async dans un event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._search_async(query, max_pages))

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Récupère les détails d'un produit (non implémenté pour l'instant)

        Args:
            product_url: URL du produit

        Returns:
            Détails du produit ou None
        """
        logger.warning("get_product_details not implemented yet for Crawlee scraper")
        return None


def create_aliexpress_scraper() -> Optional[AliExpressCrawleeScraper]:
    """
    Factory function pour créer un scraper AliExpress

    Returns:
        Instance du scraper ou None si Crawlee n'est pas disponible
    """
    if not CRAWLEE_AVAILABLE:
        logger.error("Crawlee not available. Cannot create scraper.")
        return None

    try:
        return AliExpressCrawleeScraper()
    except Exception as e:
        logger.error(f"Failed to create AliExpress scraper: {e}")
        return None


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing AliExpress Crawlee Scraper...")
    print()

    if not CRAWLEE_AVAILABLE:
        print("❌ Crawlee not available!")
        print("Install with:")
        print("  pip install crawlee[playwright]")
        print("  playwright install chromium")
    else:
        scraper = create_aliexpress_scraper()
        if scraper:
            print("✅ Scraper created")
            print("Testing search for 'handbag'...")
            results = scraper.search("handbag", max_pages=1)
            print(f"\n✅ Found {len(results)} products")

            if results:
                print("\nFirst 3 products:")
                for i, product in enumerate(results[:3], 1):
                    print(f"\n{i}. {product['title'][:60]}...")
                    print(f"   Price: ${product['price']}")
                    print(f"   Images: {len(product['images'])}")
                    if product['images']:
                        print(f"   Image URL: {product['images'][0][:60]}...")
