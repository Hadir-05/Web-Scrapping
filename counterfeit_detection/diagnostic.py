"""
Script de diagnostic pour tester le système de similarité d'images

Ce script vous aide à:
1. Tester directement la similarité entre 2 images
2. Vérifier si le scraping fonctionne
3. Diagnostiquer pourquoi votre image n'est pas trouvée
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from detectors.advanced_image_similarity import create_advanced_similarity_model
from detectors.image_similarity_model import create_image_similarity_model
from scrapers.aliexpress_scraper import AliExpressScraper


def test_similarity_directly(image1_path, image2_path):
    """Test la similarité entre deux images directement"""
    print("=" * 80)
    print("TEST 1: Similarité directe entre deux images")
    print("=" * 80)
    print()

    # Tester avec le modèle avancé
    print("🚀 Test avec modèle AVANCÉ (CLIP + pHash + ORB)...")
    try:
        advanced_model = create_advanced_similarity_model(device='cpu')
        if advanced_model:
            similarity, details = advanced_model.compute_similarity(
                image1_path,
                image2_path,
                return_details=True
            )

            print(f"\n📊 RÉSULTATS DÉTAILLÉS:")
            print(f"   ├─ CLIP:  {details['clip_score']:.2%}")
            print(f"   ├─ pHash: {details['phash_score']:.2%}")
            print(f"   ├─ ORB:   {details['orb_score']:.2%}")
            print(f"   └─ FINAL: {details['final_score']:.2%}")
            print()

            if similarity > 0.90:
                print("✅ Images TRÈS similaires (>90%) - Devraient être trouvées!")
            elif similarity > 0.75:
                print("🟡 Images SIMILAIRES (75-90%) - Bonnes chances d'être trouvées")
            elif similarity > 0.60:
                print("🟠 Similarité MOYENNE (60-75%) - Peuvent être trouvées")
            else:
                print("❌ Images PEU similaires (<60%) - Difficile à trouver")
    except Exception as e:
        print(f"❌ Erreur modèle avancé: {e}")

    print()

    # Tester avec le modèle standard pour comparaison
    print("📊 Test avec modèle STANDARD (ResNet50)...")
    try:
        standard_model = create_image_similarity_model(device='cpu')
        if standard_model:
            similarity = standard_model.compute_similarity(image1_path, image2_path)
            print(f"   └─ Similarité: {similarity:.2%}")
            print()
    except Exception as e:
        print(f"❌ Erreur modèle standard: {e}")

    print()


def test_scraper(search_query, max_pages=1):
    """Test si le scraper fonctionne et récupère des images"""
    print("=" * 80)
    print("TEST 2: Vérification du scraper AliExpress")
    print("=" * 80)
    print()

    print(f"🔍 Recherche: '{search_query}'")
    print(f"📄 Pages: {max_pages}")
    print()

    try:
        scraper = AliExpressScraper()
        results = scraper.search(search_query, max_pages=max_pages)

        if not results:
            print("❌ Aucun résultat trouvé!")
            print("\n💡 Solutions possibles:")
            print("   1. Le scraper est peut-être bloqué par AliExpress")
            print("   2. Essayez un autre terme de recherche")
            print("   3. Vérifiez votre connexion internet")
            return

        print(f"✅ {len(results)} produits trouvés")
        print()

        # Afficher les 3 premiers résultats
        for i, product in enumerate(results[:3], 1):
            print(f"Produit #{i}:")
            print(f"   ├─ Titre: {product.get('title', 'N/A')[:60]}...")
            print(f"   ├─ Prix: ${product.get('price', 'N/A')}")
            print(f"   ├─ URL: {product.get('url', 'N/A')[:60]}...")

            images = product.get('images', [])
            if images:
                print(f"   └─ Images: {len(images)} image(s)")
                print(f"      └─ Première: {images[0][:60]}...")
            else:
                print(f"   └─ ⚠️  PAS D'IMAGES!")
            print()

        # Statistiques
        products_with_images = sum(1 for p in results if p.get('images'))
        print(f"📊 Statistiques:")
        print(f"   ├─ Total produits: {len(results)}")
        print(f"   ├─ Avec images: {products_with_images}")
        print(f"   └─ Sans images: {len(results) - products_with_images}")

        if products_with_images == 0:
            print("\n❌ PROBLÈME: Aucun produit n'a d'images!")
            print("   Le scraper ne récupère pas les images correctement.")
        elif products_with_images < len(results) * 0.5:
            print(f"\n⚠️  ATTENTION: Seulement {products_with_images}/{len(results)} produits ont des images")
        else:
            print(f"\n✅ OK: {products_with_images}/{len(results)} produits ont des images")

    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
        import traceback
        traceback.print_exc()


def test_image_comparison_with_scraped(reference_image, search_query, max_pages=2):
    """Test complet: scrape + compare avec votre image"""
    print("=" * 80)
    print("TEST 3: Comparaison avec résultats scraped")
    print("=" * 80)
    print()

    print(f"📸 Image de référence: {reference_image}")
    print(f"🔍 Recherche: '{search_query}'")
    print()

    try:
        # Charger le modèle
        print("🔄 Chargement du modèle...")
        model = create_advanced_similarity_model(device='cpu')
        if not model:
            print("❌ Impossible de charger le modèle")
            return
        print("✅ Modèle chargé")
        print()

        # Scraper
        print(f"🔍 Scraping AliExpress...")
        scraper = AliExpressScraper()
        results = scraper.search(search_query, max_pages=max_pages)

        if not results:
            print("❌ Aucun résultat trouvé")
            return

        print(f"✅ {len(results)} produits trouvés")
        print()

        # Comparer avec chaque produit
        print("🧠 Calcul de similarité avec chaque produit...")
        print()

        comparisons = []
        for i, product in enumerate(results, 1):
            if not product.get('images'):
                print(f"   [{i}/{len(results)}] ⚠️  Pas d'image - {product.get('title', 'N/A')[:40]}...")
                continue

            try:
                similarity, details = model.compute_similarity(
                    reference_image,
                    product['images'][0],
                    return_details=True
                )

                comparisons.append({
                    'product': product,
                    'similarity': similarity,
                    'details': details
                })

                print(f"   [{i}/{len(results)}] {similarity:.1%} - {product.get('title', 'N/A')[:40]}...")

            except Exception as e:
                print(f"   [{i}/{len(results)}] ❌ Erreur: {e}")

        if not comparisons:
            print("\n❌ Aucune comparaison réussie!")
            return

        # Trier par similarité
        comparisons.sort(key=lambda x: x['similarity'], reverse=True)

        # Afficher le TOP 5
        print()
        print("=" * 80)
        print("🏆 TOP 5 RÉSULTATS LES PLUS SIMILAIRES")
        print("=" * 80)
        print()

        for i, comp in enumerate(comparisons[:5], 1):
            product = comp['product']
            similarity = comp['similarity']
            details = comp['details']

            if similarity >= 0.85:
                emoji = "🔴"
                status = "TRÈS SIMILAIRE"
            elif similarity >= 0.70:
                emoji = "🟠"
                status = "SIMILAIRE"
            elif similarity >= 0.55:
                emoji = "🟡"
                status = "MOYENNEMENT SIMILAIRE"
            else:
                emoji = "🟢"
                status = "PEU SIMILAIRE"

            print(f"{emoji} #{i} - {similarity:.1%} ({status})")
            print(f"   ├─ Titre: {product.get('title', 'N/A')[:60]}...")
            print(f"   ├─ Prix: ${product.get('price', 'N/A')}")
            print(f"   ├─ Scores détaillés:")
            print(f"   │  ├─ CLIP:  {details['clip_score']:.1%}")
            print(f"   │  ├─ pHash: {details['phash_score']:.1%}")
            print(f"   │  └─ ORB:   {details['orb_score']:.1%}")
            print(f"   └─ URL: {product.get('url', 'N/A')[:60]}...")
            print()

        # Analyse
        best_score = comparisons[0]['similarity']
        if best_score > 0.90:
            print("✅ EXCELLENT! Votre image a été trouvée avec haute similarité!")
        elif best_score > 0.75:
            print("🟡 BON: Image similaire trouvée, mais pas identique")
        elif best_score > 0.60:
            print("🟠 MOYEN: Quelques similitudes, mais pas optimal")
        else:
            print("❌ PROBLÈME: Aucune image très similaire trouvée")
            print("\n💡 Causes possibles:")
            print("   1. L'image n'est pas dans les résultats scraped")
            print("   2. Essayez avec plus de pages (--pages 5 ou 10)")
            print("   3. Changez le terme de recherche")
            print("   4. Vérifiez que c'est bien la bonne image")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Menu principal"""
    print()
    print("🛡️ " * 20)
    print()
    print("   DIAGNOSTIC - Système de Recherche par Image")
    print()
    print("🛡️ " * 20)
    print()

    if len(sys.argv) < 2:
        print("USAGE:")
        print()
        print("1. Tester similarité entre 2 images:")
        print("   python diagnostic.py compare image1.jpg image2.jpg")
        print()
        print("2. Tester le scraper:")
        print("   python diagnostic.py scrape \"handbag\"")
        print()
        print("3. Test complet (scrape + compare):")
        print("   python diagnostic.py full image.jpg \"handbag\"")
        print()
        sys.exit(1)

    command = sys.argv[1]

    if command == "compare" and len(sys.argv) >= 4:
        test_similarity_directly(sys.argv[2], sys.argv[3])

    elif command == "scrape" and len(sys.argv) >= 3:
        test_scraper(sys.argv[2])

    elif command == "full" and len(sys.argv) >= 4:
        test_image_comparison_with_scraped(sys.argv[2], sys.argv[3])

    else:
        print("❌ Commande invalide ou arguments manquants")
        print()
        print("Utilisez:")
        print("  python diagnostic.py compare image1.jpg image2.jpg")
        print("  python diagnostic.py scrape \"search term\"")
        print("  python diagnostic.py full myimage.jpg \"search term\"")


if __name__ == "__main__":
    main()
