"""
Script de test pour le modèle de similarité d'images (Version locale)

USAGE:
------
1. Avec vos propres images:
   python test_image_similarity_local.py /chemin/vers/image1.jpg /chemin/vers/image2.jpg

2. Avec images synthétiques (sans arguments):
   python test_image_similarity_local.py

3. Test complet de détection avec vos images:
   python test_image_similarity_local.py --detect /chemin/vers/authentic.jpg /chemin/vers/suspect.jpg
"""
import sys
from pathlib import Path
import tempfile
import os

# Ajouter le chemin parent
sys.path.append(str(Path(__file__).parent))

from PIL import Image
import numpy as np
from detectors.image_similarity_model import create_image_similarity_model
from detectors.counterfeit_detector import CounterfeitDetector


def create_test_image(color, size=(224, 224), pattern='solid'):
    """
    Crée une image de test avec une couleur spécifique

    Args:
        color: Tuple RGB (r, g, b)
        size: Taille de l'image (width, height)
        pattern: 'solid', 'gradient', ou 'checkerboard'

    Returns:
        PIL.Image
    """
    if pattern == 'solid':
        # Image unie
        img_array = np.full((size[1], size[0], 3), color, dtype=np.uint8)

    elif pattern == 'gradient':
        # Gradient horizontal
        img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        for i in range(size[0]):
            factor = i / size[0]
            img_array[:, i] = [int(c * factor) for c in color]

    elif pattern == 'checkerboard':
        # Damier
        img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        square_size = 20
        for i in range(0, size[1], square_size):
            for j in range(0, size[0], square_size):
                if (i // square_size + j // square_size) % 2 == 0:
                    img_array[i:i+square_size, j:j+square_size] = color
                else:
                    img_array[i:i+square_size, j:j+square_size] = [255-c for c in color]

    return Image.fromarray(img_array)


def save_temp_image(image, prefix='test'):
    """Sauvegarde une image dans un fichier temporaire"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', prefix=prefix, delete=False)
    image.save(temp_file.name, 'JPEG')
    return temp_file.name


def test_image_similarity_basic():
    """Test basique de similarité d'images"""
    print("=" * 70)
    print("🧪 TEST 1: Image Similarity Model (Local Synthetic Images)")
    print("=" * 70)
    print()

    # Créer le modèle
    print("1️⃣ Loading pre-trained ResNet50 model...")
    model = create_image_similarity_model(device='cpu')

    if model is None:
        print("❌ Failed to create model")
        return

    print("✅ Model loaded successfully!")
    print()

    # Créer des images de test
    print("2️⃣ Generating synthetic test images...")
    print()

    temp_files = []

    try:
        # Test Case 1: Images très similaires (même couleur, motif similaire)
        print("📸 Test Case 1: Similar red images")
        red_img1 = create_test_image((255, 0, 0), pattern='solid')
        red_img2 = create_test_image((255, 0, 0), pattern='solid')

        red_path1 = save_temp_image(red_img1, 'red1')
        red_path2 = save_temp_image(red_img2, 'red2')
        temp_files.extend([red_path1, red_path2])

        similarity = model.compute_similarity(red_path1, red_path2)
        print(f"   Image 1: Solid red (255, 0, 0)")
        print(f"   Image 2: Solid red (255, 0, 0)")
        print(f"   ✅ Similarity: {similarity:.2%}")
        print(f"   Expected: ~100% (identical images)")
        print()

        # Test Case 2: Images de même couleur mais motifs différents
        print("📸 Test Case 2: Same color, different patterns")
        red_solid = create_test_image((255, 0, 0), pattern='solid')
        red_gradient = create_test_image((255, 0, 0), pattern='gradient')

        solid_path = save_temp_image(red_solid, 'red_solid')
        gradient_path = save_temp_image(red_gradient, 'red_gradient')
        temp_files.extend([solid_path, gradient_path])

        similarity = model.compute_similarity(solid_path, gradient_path)
        print(f"   Image 1: Solid red")
        print(f"   Image 2: Red gradient")
        print(f"   ✅ Similarity: {similarity:.2%}")
        print(f"   Expected: 60-90% (same color, different pattern)")
        print()

        # Test Case 3: Couleurs complètement différentes
        print("📸 Test Case 3: Completely different colors")
        red_img = create_test_image((255, 0, 0), pattern='solid')
        blue_img = create_test_image((0, 0, 255), pattern='solid')

        red_path = save_temp_image(red_img, 'red')
        blue_path = save_temp_image(blue_img, 'blue')
        temp_files.extend([red_path, blue_path])

        similarity = model.compute_similarity(red_path, blue_path)
        print(f"   Image 1: Solid red (255, 0, 0)")
        print(f"   Image 2: Solid blue (0, 0, 255)")
        print(f"   ✅ Similarity: {similarity:.2%}")
        print(f"   Expected: 50-70% (very different colors)")
        print()

        # Test Case 4: Motifs complexes
        print("📸 Test Case 4: Complex patterns")
        checker1 = create_test_image((200, 50, 50), pattern='checkerboard')
        checker2 = create_test_image((200, 50, 50), pattern='checkerboard')

        checker_path1 = save_temp_image(checker1, 'checker1')
        checker_path2 = save_temp_image(checker2, 'checker2')
        temp_files.extend([checker_path1, checker_path2])

        similarity = model.compute_similarity(checker_path1, checker_path2)
        print(f"   Image 1: Checkerboard pattern (red tones)")
        print(f"   Image 2: Checkerboard pattern (red tones)")
        print(f"   ✅ Similarity: {similarity:.2%}")
        print(f"   Expected: ~100% (identical patterns)")
        print()

        print("=" * 70)
        print("✅ TEST 1 COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()

    finally:
        # Nettoyer les fichiers temporaires
        print("🧹 Cleaning up temporary files...")
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        print("✅ Cleanup complete")
        print()


def test_counterfeit_detection_with_synthetic_images():
    """Test complet de détection de contrefaçons avec images synthétiques"""
    print("=" * 70)
    print("🧪 TEST 2: Complete Counterfeit Detection (Synthetic Images)")
    print("=" * 70)
    print()

    print("1️⃣ Creating CounterfeitDetector with pre-trained model...")
    detector = CounterfeitDetector(use_pretrained=True, device='cpu')
    print("✅ Detector initialized!")
    print()

    temp_files = []

    try:
        # Créer des images de référence et suspectes
        print("2️⃣ Generating reference and suspicious images...")

        # Image authentique: Sac Hermès (simulé par pattern complexe rouge/orange)
        authentic_img = create_test_image((200, 80, 20), pattern='checkerboard')
        authentic_path = save_temp_image(authentic_img, 'authentic_hermes')
        temp_files.append(authentic_path)

        # Image contrefaite 1: Très similaire (même pattern, couleur légèrement différente)
        counterfeit_img1 = create_test_image((190, 70, 15), pattern='checkerboard')
        counterfeit_path1 = save_temp_image(counterfeit_img1, 'counterfeit1')
        temp_files.append(counterfeit_path1)

        # Image contrefaite 2: Différente (couleur et pattern différents)
        counterfeit_img2 = create_test_image((50, 100, 200), pattern='gradient')
        counterfeit_path2 = save_temp_image(counterfeit_img2, 'counterfeit2')
        temp_files.append(counterfeit_path2)

        print("✅ Images generated")
        print()

        # Produit authentique de référence
        authentic_product = {
            "brand": "Hermès",
            "model": "Birkin 30",
            "price_range": (8000, 12000),
            "keywords": ["hermès", "birkin", "authentic", "leather", "luxury"],
            "images": [authentic_path]
        }

        # Annonce suspecte 1: Contrefaçon probable (prix bas, image similaire)
        print("3️⃣ Testing suspicious listing #1 (High similarity, low price)...")
        scraped_product_1 = {
            "title": "Sac Hermès Birkin Style - Haute Qualité",
            "price": 299.99,
            "description": "Magnifique sac style Hermès Birkin, haute qualité, livraison rapide",
            "url": "https://example-marketplace.com/hermes-style-bag-123",
            "images": [counterfeit_path1],
            "seller_rating": 4.5
        }

        result_1 = detector.detect_counterfeit(scraped_product_1, [authentic_product])

        print(f"\n   📊 RESULTS for Listing #1:")
        print(f"   └─ Overall Counterfeit Score: {result_1['counterfeit_score']:.1%}")
        print(f"   └─ Is Suspicious: {'🚨 YES' if result_1['is_suspicious'] else '✅ NO'}")
        print(f"   └─ Confidence: {result_1['confidence']}")
        print(f"\n   📈 Breakdown:")
        print(f"   └─ Keyword Match: {result_1['details']['keyword_match_score']:.1%}")
        print(f"   └─ Image Similarity: {result_1['details']['image_similarity_score']:.1%}")
        print(f"   └─ Price Analysis: {result_1['details']['price_analysis_score']:.1%}")
        print(f"   └─ Suspicious Words: {result_1['details']['suspicious_words_score']:.1%}")
        print()

        # Annonce suspecte 2: Moins probable (image différente)
        print("4️⃣ Testing suspicious listing #2 (Low similarity, different pattern)...")
        scraped_product_2 = {
            "title": "Sac à main élégant - Style moderne",
            "price": 1500.00,
            "description": "Sac à main de luxe, cuir véritable, design unique",
            "url": "https://example-marketplace.com/elegant-bag-456",
            "images": [counterfeit_path2],
            "seller_rating": 4.8
        }

        result_2 = detector.detect_counterfeit(scraped_product_2, [authentic_product])

        print(f"\n   📊 RESULTS for Listing #2:")
        print(f"   └─ Overall Counterfeit Score: {result_2['counterfeit_score']:.1%}")
        print(f"   └─ Is Suspicious: {'🚨 YES' if result_2['is_suspicious'] else '✅ NO'}")
        print(f"   └─ Confidence: {result_2['confidence']}")
        print(f"\n   📈 Breakdown:")
        print(f"   └─ Keyword Match: {result_2['details']['keyword_match_score']:.1%}")
        print(f"   └─ Image Similarity: {result_2['details']['image_similarity_score']:.1%}")
        print(f"   └─ Price Analysis: {result_2['details']['price_analysis_score']:.1%}")
        print(f"   └─ Suspicious Words: {result_2['details']['suspicious_words_score']:.1%}")
        print()

        print("=" * 70)
        print("✅ TEST 2 COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()

    finally:
        # Nettoyer les fichiers temporaires
        print("🧹 Cleaning up temporary files...")
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        print("✅ Cleanup complete")
        print()


def test_user_images(image1_path, image2_path):
    """Test de similarité avec les images fournies par l'utilisateur"""
    print("=" * 70)
    print("🧪 TEST: Image Similarity avec vos images locales")
    print("=" * 70)
    print()

    # Vérifier que les images existent
    if not os.path.exists(image1_path):
        print(f"❌ Erreur: Image 1 n'existe pas: {image1_path}")
        return

    if not os.path.exists(image2_path):
        print(f"❌ Erreur: Image 2 n'existe pas: {image2_path}")
        return

    print("1️⃣ Loading pre-trained ResNet50 model...")
    model = create_image_similarity_model(device='cpu')

    if model is None:
        print("❌ Failed to create model")
        return

    print("✅ Model loaded successfully!")
    print()

    print("2️⃣ Analyzing your images...")
    print(f"   📷 Image 1: {image1_path}")
    print(f"   📷 Image 2: {image2_path}")
    print()

    try:
        similarity = model.compute_similarity(image1_path, image2_path)

        print("=" * 70)
        print(f"✅ RÉSULTAT: Similarité = {similarity:.2%}")
        print("=" * 70)
        print()
        print("📊 Interprétation:")
        if similarity >= 0.90:
            print("   🟢 Images TRÈS similaires (>90%) - Probablement le même produit")
        elif similarity >= 0.75:
            print("   🟡 Images SIMILAIRES (75-90%) - Produits apparentés")
        elif similarity >= 0.60:
            print("   🟠 Similarité MOYENNE (60-75%) - Quelques ressemblances")
        else:
            print("   🔴 Images DIFFÉRENTES (<60%) - Produits distincts")
        print()

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()


def test_user_images_detection(authentic_path, suspect_path):
    """Test complet de détection avec images utilisateur"""
    print("=" * 70)
    print("🧪 TEST: Détection de contrefaçon avec vos images")
    print("=" * 70)
    print()

    # Vérifier que les images existent
    if not os.path.exists(authentic_path):
        print(f"❌ Erreur: Image authentique n'existe pas: {authentic_path}")
        return

    if not os.path.exists(suspect_path):
        print(f"❌ Erreur: Image suspecte n'existe pas: {suspect_path}")
        return

    print("1️⃣ Creating CounterfeitDetector with pre-trained model...")
    detector = CounterfeitDetector(use_pretrained=True, device='cpu')
    print("✅ Detector initialized!")
    print()

    print("2️⃣ Analyzing your images...")
    print(f"   📷 Image authentique: {authentic_path}")
    print(f"   📷 Image suspecte: {suspect_path}")
    print()

    # Produit authentique
    authentic_product = {
        "brand": "Luxury Brand",
        "model": "Authentic Product",
        "price_range": (5000, 10000),
        "keywords": ["authentic", "luxury", "original"],
        "images": [authentic_path]
    }

    # Produit suspect
    suspect_product = {
        "title": "Luxury style product - high quality replica",
        "price": 299.99,
        "description": "High quality luxury style product, fast shipping",
        "url": "https://example.com/product",
        "images": [suspect_path],
        "seller_rating": 4.5
    }

    try:
        print("3️⃣ Running counterfeit detection analysis...")
        result = detector.detect_counterfeit(suspect_product, [authentic_product])

        print()
        print("=" * 70)
        print("📊 RÉSULTATS DE DÉTECTION")
        print("=" * 70)
        print()
        print(f"🎯 Score global de contrefaçon: {result['counterfeit_score']:.1%}")
        print(f"🚨 Suspect: {'OUI' if result['is_suspicious'] else 'NON'}")
        print(f"💯 Confiance: {result['confidence']}")
        print()
        print("📈 Détails par critère:")
        print(f"   └─ Similarité d'images: {result['details']['image_similarity_score']:.1%}")
        print(f"   └─ Correspondance mots-clés: {result['details']['keyword_match_score']:.1%}")
        print(f"   └─ Analyse des prix: {result['details']['price_analysis_score']:.1%}")
        print(f"   └─ Mots suspects: {result['details']['suspicious_words_score']:.1%}")
        print()

        if result['is_suspicious']:
            print("⚠️  Ce produit est SUSPECT et pourrait être une contrefaçon!")
        else:
            print("✅ Ce produit semble LÉGITIME.")
        print()

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Fonction principale"""
    print()
    print("🛡️ " * 20)
    print()
    print("   COUNTERFEIT DETECTION - IMAGE SIMILARITY TEST")
    print("   Using Pre-trained ResNet50")
    print()
    print("🛡️ " * 20)
    print()
    print()

    # Vérifier les arguments de ligne de commande
    if len(sys.argv) == 3:
        # Mode: Comparaison simple de deux images
        image1_path = sys.argv[1]
        image2_path = sys.argv[2]

        test_user_images(image1_path, image2_path)

        print()
        print("💡 Pour tester la détection complète:")
        print(f"   python {sys.argv[0]} --detect {image1_path} {image2_path}")
        print()

    elif len(sys.argv) == 4 and sys.argv[1] == '--detect':
        # Mode: Détection complète de contrefaçon
        authentic_path = sys.argv[2]
        suspect_path = sys.argv[3]

        test_user_images_detection(authentic_path, suspect_path)

        print()
        print("💡 Pour juste comparer la similarité:")
        print(f"   python {sys.argv[0]} {authentic_path} {suspect_path}")
        print()

    else:
        # Mode par défaut: Images synthétiques
        if len(sys.argv) > 1:
            print("❌ Usage incorrect!")
            print()
            print("USAGE:")
            print(f"  1. Comparer deux images:")
            print(f"     python {sys.argv[0]} image1.jpg image2.jpg")
            print()
            print(f"  2. Détection complète:")
            print(f"     python {sys.argv[0]} --detect authentic.jpg suspect.jpg")
            print()
            print(f"  3. Tests avec images synthétiques:")
            print(f"     python {sys.argv[0]}")
            print()
            sys.exit(1)

        # Tests avec images synthétiques
        try:
            # Test 1: Similarité basique d'images
            test_image_similarity_basic()

            # Test 2: Détection complète avec images
            test_counterfeit_detection_with_synthetic_images()

            print()
            print("=" * 70)
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print()
            print("💡 Next steps:")
            print("   1. Test with your own images:")
            print(f"      python {sys.argv[0]} /path/to/image1.jpg /path/to/image2.jpg")
            print()
            print("   2. Run actual scrapes with: python demo.py")
            print("   3. View results in dashboard: streamlit run dashboard.py")
            print()

        except KeyboardInterrupt:
            print()
            print("⚠️  Tests interrupted by user")
            print()
        except Exception as e:
            print()
            print(f"❌ Error during tests: {e}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == "__main__":
    main()
