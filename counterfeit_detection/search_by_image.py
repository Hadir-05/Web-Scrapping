"""
Moteur de recherche par image pour détecter les contrefaçons

USAGE:
------
python search_by_image.py /chemin/vers/image_reference.jpg "Hermès Birkin" --site aliexpress --top 5

Ce script:
1. Prend une image de référence (produit authentique)
2. Scrape le site spécifié (AliExpress, DHgate, etc.)
3. Compare l'image de référence avec toutes les images des annonces
4. Affiche le TOP N des annonces les plus similaires
"""
import sys
import os
from pathlib import Path
import argparse
from typing import List, Dict, Tuple

# Ajouter le chemin parent
sys.path.append(str(Path(__file__).parent))

from scrapers.aliexpress_scraper import AliExpressScraper
from scrapers.dhgate_scraper import DHgateScraper
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

    def __init__(self, device='cpu'):
        """
        Initialise le moteur de recherche

        Args:
            device: 'cpu' ou 'cuda' pour GPU
        """
        logger.info("🔄 Initializing Image Search Engine...")

        # Charger le modèle de similarité d'images
        self.similarity_model = create_image_similarity_model(device=device)

        if self.similarity_model is None:
            raise RuntimeError("Failed to load image similarity model")

        # Initialiser les scrapers
        self.scrapers = {
            'aliexpress': AliExpressScraper(),
            'dhgate': DHgateScraper()
        }

        logger.info("✅ Image Search Engine initialized!")

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
        logger.info(f"🔍 Recherche: '{search_query}' sur {site.upper()}")
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
Exemples:
  # Rechercher sur AliExpress et afficher le TOP 5 (3 pages ≈ 30-60 produits)
  python search_by_image.py /path/to/hermes_birkin.jpg "Hermès Birkin" --site aliexpress --top 5

  # Rechercher sur DHgate avec plus de résultats (10 pages ≈ 100-200 produits)
  python search_by_image.py /path/to/rolex.jpg "Rolex Submariner" --site dhgate --pages 10 --top 10

  # Recherche rapide (1 page ≈ 10-20 produits)
  python search_by_image.py /path/to/product.jpg "luxury bag" --pages 1 --top 3
        """
    )

    parser.add_argument(
        'image',
        help='Chemin vers l\'image de référence (produit authentique)'
    )

    parser.add_argument(
        'query',
        help='Terme de recherche (ex: "Hermès Birkin", "Rolex Submariner")'
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

    args = parser.parse_args()

    print()
    print("🛡️ " * 20)
    print()
    print("   MOTEUR DE RECHERCHE PAR IMAGE")
    print("   Détection de contrefaçons par similarité d'images")
    print()
    print("🛡️ " * 20)
    print()

    try:
        # Créer le moteur de recherche
        engine = ImageSearchEngine(device=args.device)

        # Lancer la recherche
        results = engine.search_products(
            reference_image_path=args.image,
            search_query=args.query,
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
