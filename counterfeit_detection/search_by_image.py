"""
Moteur de recherche par image pour détecter les contrefaçons

USAGE:
------
python search_by_image.py /chemin/vers/image_reference.jpg "handbag" --site aliexpress --top 5

⚠️  IMPORTANT: Utilisez des termes GÉNÉRIQUES (bag, watch, shoes, etc.)
              PAS de noms de marque (Hermès, Rolex, etc.)

Ce script:
1. Prend une image de référence (votre produit)
2. Scrape le site avec un terme GÉNÉRIQUE (AliExpress, DHgate, etc.)
3. Compare votre image avec TOUTES les images des annonces trouvées
4. Classe les résultats 100% par SIMILARITÉ D'IMAGE (IA ResNet50)
5. Affiche le TOP N des annonces les plus similaires visuellement

Le classement est basé UNIQUEMENT sur l'apparence visuelle des produits,
PAS sur les noms de marque ou les descriptions textuelles.
"""
import sys
import os
from pathlib import Path
import argparse
from typing import List, Dict, Tuple

# Ajouter le chemin parent
sys.path.append(str(Path(__file__).parent))

from scrapers.dhgate_scraper import DHgateScraper

# Essayer d'importer le scraper Crawlee (moderne, recommandé)
try:
    from scrapers.aliexpress_crawlee_scraper import create_aliexpress_scraper
    CRAWLEE_SCRAPER_AVAILABLE = True
except ImportError:
    CRAWLEE_SCRAPER_AVAILABLE = False

# Fallback sur l'ancien scraper BeautifulSoup
if not CRAWLEE_SCRAPER_AVAILABLE:
    from scrapers.aliexpress_scraper import AliExpressScraper

# Essayer d'importer le modèle avancé en priorité
try:
    from detectors.advanced_image_similarity import create_advanced_similarity_model
    ADVANCED_MODEL_AVAILABLE = True
except ImportError:
    ADVANCED_MODEL_AVAILABLE = False

# Fallback sur l'ancien modèle
from detectors.image_similarity_model import create_image_similarity_model

import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageSearchEngine:
    """Moteur de recherche par image pour détecter les contrefaçons"""

    def __init__(self, device='cpu', use_advanced=True):
        """
        Initialise le moteur de recherche

        Args:
            device: 'cpu' ou 'cuda' pour GPU
            use_advanced: Si True, utilise le modèle avancé (CLIP+pHash+ORB)
        """
        logger.info("🔄 Initializing Image Search Engine...")

        # Charger le modèle de similarité d'images
        if use_advanced and ADVANCED_MODEL_AVAILABLE:
            logger.info("🚀 Using ADVANCED similarity model (CLIP + pHash + ORB)")
            self.similarity_model = create_advanced_similarity_model(device=device)
            self.model_type = "advanced"
        else:
            if use_advanced:
                logger.warning("⚠️  Advanced model not available, falling back to ResNet50")
            logger.info("📊 Using standard similarity model (ResNet50)")
            self.similarity_model = create_image_similarity_model(device=device)
            self.model_type = "standard"

        if self.similarity_model is None:
            raise RuntimeError("Failed to load image similarity model")

        # Initialiser les scrapers
        # Utiliser Crawlee pour AliExpress si disponible (BEAUCOUP plus fiable)
        if CRAWLEE_SCRAPER_AVAILABLE:
            logger.info("🚀 Using CRAWLEE scraper for AliExpress (Playwright-based)")
            aliexpress_scraper = create_aliexpress_scraper()
            if aliexpress_scraper is None:
                logger.warning("⚠️  Crawlee scraper failed, falling back to BeautifulSoup")
                aliexpress_scraper = AliExpressScraper()
        else:
            logger.warning("⚠️  Crawlee not available, using BeautifulSoup scraper (may not work)")
            logger.warning("   Install Crawlee with: pip install crawlee[playwright]")
            aliexpress_scraper = AliExpressScraper()

        self.scrapers = {
            'aliexpress': aliexpress_scraper,
            'dhgate': DHgateScraper()
        }

        logger.info(f"✅ Image Search Engine initialized! (model: {self.model_type})")

    def search_products(
        self,
        reference_image_path: str,
        search_query: str,
        site: str = 'aliexpress',
        max_pages: int = 3,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Recherche les annonces les plus similaires à l'image de référence

        Args:
            reference_image_path: Chemin vers l'image de référence
            search_query: Terme de recherche (ex: "Hermès Birkin")
            site: Site à scraper ('aliexpress' ou 'dhgate')
            max_pages: Nombre maximum de pages à scraper (1 page ≈ 10-20 produits)
            top_n: Nombre de résultats les plus similaires à retourner

        Returns:
            Liste des TOP N annonces avec leur score de similarité
        """
        # Vérifier que l'image de référence existe
        if not os.path.exists(reference_image_path):
            raise FileNotFoundError(f"Image de référence introuvable: {reference_image_path}")

        # Vérifier que le site est supporté
        if site not in self.scrapers:
            raise ValueError(f"Site non supporté: {site}. Utilisez: {list(self.scrapers.keys())}")

        logger.info(f"📸 Image de référence: {reference_image_path}")
        logger.info(f"🔍 Recherche avec terme générique: '{search_query}' sur {site.upper()}")
        logger.info(f"🎯 Détection: 100% basée sur la SIMILARITÉ D'IMAGE (pas le nom de marque)")
        logger.info(f"📊 Scraping jusqu'à {max_pages} pages...")

        # Scraper le site
        scraper = self.scrapers[site]
        scraped_products = scraper.search(search_query, max_pages=max_pages)

        if not scraped_products:
            logger.warning("❌ Aucune annonce trouvée!")
            return []

        logger.info(f"✅ {len(scraped_products)} annonces trouvées")
        logger.info("🧠 Calcul de la similarité avec l'image de référence...")

        # Calculer la similarité pour chaque annonce
        results_with_similarity = []

        for i, product in enumerate(scraped_products, 1):
            try:
                # Récupérer la première image de l'annonce
                if not product.get('images') or not product['images']:
                    logger.warning(f"   [{i}/{len(scraped_products)}] Pas d'image pour: {product.get('title', 'N/A')[:50]}...")
                    continue

                product_image = product['images'][0]

                # Calculer la similarité
                similarity = self.similarity_model.compute_similarity(
                    reference_image_path,
                    product_image
                )

                # Ajouter le score de similarité au produit
                product['similarity_score'] = similarity
                results_with_similarity.append(product)

                logger.info(f"   [{i}/{len(scraped_products)}] {similarity:.1%} - {product.get('title', 'N/A')[:50]}...")

            except Exception as e:
                logger.error(f"   [{i}/{len(scraped_products)}] Erreur: {e}")
                continue

        if not results_with_similarity:
            logger.warning("❌ Aucune annonce n'a pu être comparée!")
            return []

        # Trier par similarité décroissante
        results_with_similarity.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Retourner le TOP N
        top_results = results_with_similarity[:top_n]

        logger.info(f"\n✅ TOP {len(top_results)} annonces les plus similaires:")

        return top_results

    def display_results(self, results: List[Dict]):
        """
        Affiche les résultats de manière formatée

        Args:
            results: Liste des annonces avec leur score de similarité
        """
        if not results:
            print("\n❌ Aucun résultat à afficher")
            return

        print("\n" + "=" * 80)
        print(f"🏆 TOP {len(results)} ANNONCES LES PLUS SIMILAIRES")
        print(f"    (Classement 100% basé sur la similarité d'IMAGE, pas le nom)")
        print("=" * 80)
        print()

        for i, product in enumerate(results, 1):
            similarity = product.get('similarity_score', 0)

            # Déterminer l'emoji selon le score
            if similarity >= 0.85:
                emoji = "🔴"  # Très suspect
                status = "TRÈS SUSPECT"
            elif similarity >= 0.70:
                emoji = "🟠"  # Suspect
                status = "SUSPECT"
            elif similarity >= 0.55:
                emoji = "🟡"  # Modérément suspect
                status = "MODÉRÉMENT SUSPECT"
            else:
                emoji = "🟢"  # Peu suspect
                status = "PEU SUSPECT"

            print(f"{emoji} #{i} - SIMILARITÉ: {similarity:.1%} ({status})")
            print("-" * 80)
            print(f"📦 Titre: {product.get('title', 'N/A')}")
            print(f"💰 Prix: ${product.get('price', 'N/A')}")
            print(f"🔗 URL: {product.get('url', 'N/A')}")

            if product.get('images'):
                print(f"📸 Image: {product['images'][0]}")

            if product.get('seller_info'):
                print(f"👤 Vendeur: {product['seller_info']}")

            if product.get('rating'):
                print(f"⭐ Note: {product['rating']}")

            print()

        print("=" * 80)
        print()

        # Statistiques
        avg_similarity = sum(p['similarity_score'] for p in results) / len(results)
        max_similarity = max(p['similarity_score'] for p in results)
        min_similarity = min(p['similarity_score'] for p in results)

        print("📊 STATISTIQUES:")
        print(f"   └─ Similarité moyenne: {avg_similarity:.1%}")
        print(f"   └─ Similarité maximale: {max_similarity:.1%}")
        print(f"   └─ Similarité minimale: {min_similarity:.1%}")
        print()

        # Alertes
        high_risk = sum(1 for p in results if p['similarity_score'] >= 0.85)
        medium_risk = sum(1 for p in results if 0.70 <= p['similarity_score'] < 0.85)

        if high_risk > 0:
            print(f"⚠️  ALERTE: {high_risk} annonce(s) à TRÈS HAUTE SIMILARITÉ détectée(s)!")
        if medium_risk > 0:
            print(f"⚠️  {medium_risk} annonce(s) à HAUTE SIMILARITÉ détectée(s)")
        print()


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Moteur de recherche par image pour détecter les contrefaçons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples (UTILISEZ DES TERMES GÉNÉRIQUES, PAS DE NOMS DE MARQUE):

  # Chercher des sacs similaires (sans spécifier la marque)
  python search_by_image.py /path/to/my_bag.jpg "handbag" --top 5

  # Chercher des montres similaires sur DHgate
  python search_by_image.py /path/to/my_watch.jpg "watch" --site dhgate --pages 10 --top 10

  # Chercher des chaussures similaires (recherche rapide)
  python search_by_image.py /path/to/my_shoes.jpg "shoes" --pages 1 --top 3

  # Sans terme de recherche (utilise automatiquement "luxury product")
  python search_by_image.py /path/to/product.jpg --pages 5 --top 5

IMPORTANT: Le système trouve les produits similaires uniquement par IMAGE,
pas par nom de marque! Utilisez des termes génériques pour de meilleurs résultats.
        """
    )

    parser.add_argument(
        'image',
        help='Chemin vers l\'image de référence (produit authentique)'
    )

    parser.add_argument(
        'query',
        nargs='?',
        default=None,
        help='Terme de recherche GÉNÉRIQUE (ex: "bag", "handbag", "watch", "shoes"). '
             'Utilisez des termes génériques pour trouver tous les produits similaires, '
             'pas des noms de marque. Si omis, utilise "luxury product"'
    )

    parser.add_argument(
        '--site',
        choices=['aliexpress', 'dhgate'],
        default='aliexpress',
        help='Site à scraper (défaut: aliexpress)'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=3,
        help='Nombre de pages à scraper (1 page ≈ 10-20 produits, défaut: 3)'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='Nombre de résultats les plus similaires à afficher (défaut: 5)'
    )

    parser.add_argument(
        '--device',
        choices=['cpu', 'cuda'],
        default='cpu',
        help='Device pour le modèle AI (défaut: cpu)'
    )

    parser.add_argument(
        '--model',
        choices=['advanced', 'standard'],
        default='advanced',
        help='Type de modèle: advanced (CLIP+pHash+ORB, RECOMMANDÉ) ou standard (ResNet50)'
    )

    args = parser.parse_args()

    print()
    print("🛡️ " * 20)
    print()
    print("   MOTEUR DE RECHERCHE PAR IMAGE")
    print("   Détection 100% basée sur la SIMILARITÉ D'IMAGE")
    print("   (Pas de détection par nom de marque)")
    print()
    print("🛡️ " * 20)
    print()

    try:
        # Créer le moteur de recherche
        use_advanced = (args.model == 'advanced')
        engine = ImageSearchEngine(device=args.device, use_advanced=use_advanced)

        # Si aucun terme de recherche n'est fourni, utiliser un terme générique
        search_query = args.query
        if not search_query:
            search_query = "luxury product"
            print("ℹ️  Aucun terme de recherche spécifié, utilisation de 'luxury product'")
            print("   💡 Conseil: Utilisez des termes GÉNÉRIQUES comme 'bag', 'watch', 'shoes'")
            print("   ❌ Évitez les noms de marque comme 'Hermès', 'Rolex', etc.")
            print()

        # Lancer la recherche
        results = engine.search_products(
            reference_image_path=args.image,
            search_query=search_query,
            site=args.site,
            max_pages=args.pages,
            top_n=args.top
        )

        # Afficher les résultats
        engine.display_results(results)

        print("✅ Recherche terminée!")
        print()

    except KeyboardInterrupt:
        print()
        print("⚠️  Recherche interrompue par l'utilisateur")
        print()
    except Exception as e:
        print()
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
