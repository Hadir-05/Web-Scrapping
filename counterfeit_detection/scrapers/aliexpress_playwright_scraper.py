"""
AliExpress scraper using Playwright directly (Python 3.8 compatible)
Alternative à Crawlee qui nécessite Python 3.9+

Installation:
pip install playwright
playwright install chromium
"""

from typing import List, Dict, Optional
import logging
import re
import time
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Vérifier si Playwright est disponible
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Install with: pip install playwright")


class AliExpressPlaywrightScraper:
    """
    Scraper AliExpress utilisant Playwright directement
    Compatible Python 3.8+

    Alternative légère à Crawlee pour scraper AliExpress avec JavaScript
    """

    def __init__(self):
        """Initialise le scraper Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not available. Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )

        self.base_url = "https://www.aliexpress.com"

    def search(self, query: str, max_pages: int = 3) -> List[Dict]:
        """
        Recherche des produits sur AliExpress

        Args:
            query: Terme de recherche
            max_pages: Nombre de pages à scraper

        Returns:
            Liste de produits trouvés
        """
        all_products = []

        with sync_playwright() as p:
            # Lancer le navigateur
            logger.info("🚀 Lancement du navigateur Chromium...")
            browser = p.chromium.launch(
                headless=True,  # Mode invisible
                args=[
                    '--disable-blink-features=AutomationControlled',  # Anti-détection
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            # Créer un contexte avec user agent réaliste
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )

            page = context.new_page()

            try:
                for page_num in range(1, max_pages + 1):
                    logger.info(f"📄 Scraping page {page_num}/{max_pages}...")

                    # Construire l'URL
                    search_query = quote_plus(query)
                    if page_num == 1:
                        url = f"{self.base_url}/wholesale?SearchText={search_query}"
                    else:
                        url = f"{self.base_url}/wholesale?SearchText={search_query}&page={page_num}"

                    logger.info(f"   URL: {url}")

                    # Naviguer vers la page
                    try:
                        page.goto(url, wait_until='networkidle', timeout=30000)
                    except PlaywrightTimeout:
                        logger.warning(f"   ⚠️  Timeout loading page {page_num}")
                        continue

                    # Attendre que les produits se chargent
                    try:
                        page.wait_for_selector(
                            'div.search-card-item, div[class*="list--gallery"], a[class*="multi--container"]',
                            timeout=10000
                        )
                    except PlaywrightTimeout:
                        logger.warning(f"   ⚠️  Products not found on page {page_num}")
                        continue

                    # Petit délai pour laisser tout charger
                    time.sleep(2)

                    # Extraire les produits
                    products = page.evaluate("""
                        () => {
                            const items = [];

                            // Essayer plusieurs sélecteurs
                            const selectors = [
                                'div.search-card-item',
                                'div[class*="list--gallery"] > div',
                                'a[class*="multi--container"]'
                            ];

                            let productElements = [];
                            for (const selector of selectors) {
                                productElements = document.querySelectorAll(selector);
                                if (productElements.length > 0) break;
                            }

                            console.log('Found elements:', productElements.length);

                            productElements.forEach((item, index) => {
                                try {
                                    // Lien
                                    const link = item.querySelector('a[href*="/item/"]') || item.querySelector('a');
                                    const url = link ? link.href : '';

                                    // Titre
                                    const titleSelectors = ['h1', 'h3', '[class*="title"]', '[class*="Title"]'];
                                    let title = '';
                                    for (const sel of titleSelectors) {
                                        const elem = item.querySelector(sel);
                                        if (elem && elem.textContent.trim()) {
                                            title = elem.textContent.trim();
                                            break;
                                        }
                                    }

                                    // Prix
                                    const priceSelectors = ['[class*="price"]', '[class*="Price"]', 'span.price'];
                                    let price = '';
                                    for (const sel of priceSelectors) {
                                        const elem = item.querySelector(sel);
                                        if (elem && elem.textContent.trim()) {
                                            price = elem.textContent.trim();
                                            break;
                                        }
                                    }

                                    // Image
                                    const img = item.querySelector('img');
                                    let imageUrl = '';
                                    if (img) {
                                        imageUrl = img.src || img.getAttribute('data-src') || '';
                                        if (imageUrl.startsWith('//')) {
                                            imageUrl = 'https:' + imageUrl;
                                        }
                                        // Enlever les paramètres de taille
                                        if (imageUrl.includes('_')) {
                                            imageUrl = imageUrl.split('_')[0] + '.jpg';
                                        }
                                    }

                                    // Rating
                                    const ratingElem = item.querySelector('[class*="rating"], [class*="stars"]');
                                    const rating = ratingElem ? ratingElem.textContent.trim() : '';

                                    // Sales
                                    const salesElem = item.querySelector('[class*="sale"], [class*="sold"]');
                                    const sales = salesElem ? salesElem.textContent.trim() : '';

                                    if (url && title && imageUrl) {
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

                    logger.info(f"   ✅ Found {len(products)} products on page {page_num}")

                    # Nettoyer et ajouter les produits
                    for product in products:
                        # Extraire le prix numérique
                        price_str = product.get('price', '')
                        price_match = re.search(r'[\d,\.]+', price_str)
                        price = float(price_match.group().replace(',', '')) if price_match else 0.0

                        # Rating
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
                            'seller_info': ''
                        }

                        all_products.append(product_data)

                    # Délai entre les pages
                    if page_num < max_pages:
                        time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Error during scraping: {e}")
                import traceback
                traceback.print_exc()

            finally:
                # Fermer le navigateur
                browser.close()

        logger.info(f"✅ Total products found: {len(all_products)}")
        return all_products

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Récupère les détails d'un produit (non implémenté)

        Args:
            product_url: URL du produit

        Returns:
            Détails du produit ou None
        """
        logger.warning("get_product_details not implemented yet")
        return None


def create_aliexpress_scraper() -> Optional[AliExpressPlaywrightScraper]:
    """
    Factory function pour créer un scraper AliExpress

    Returns:
        Instance du scraper ou None si Playwright n'est pas disponible
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available. Cannot create scraper.")
        return None

    try:
        return AliExpressPlaywrightScraper()
    except Exception as e:
        logger.error(f"Failed to create scraper: {e}")
        return None


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing AliExpress Playwright Scraper (Python 3.8 compatible)...")
    print()

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available!")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
    else:
        print("✅ Playwright available")
        print()
        scraper = create_aliexpress_scraper()
        if scraper:
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
                        print(f"   Image: {product['images'][0][:60]}...")
