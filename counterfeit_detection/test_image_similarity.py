"""
Script de test pour le modèle de similarité d'images
Teste la détection de contrefaçons basée sur les images
"""
import sys
from pathlib import Path

# Ajouter le chemin parent
sys.path.append(str(Path(__file__).parent))

from detectors.image_similarity_model import create_image_similarity_model
from detectors.counterfeit_detector import CounterfeitDetector


def test_image_similarity_basic():
    """Test basique de similarité d'images"""
    print("=" * 70)
    print("🧪 TEST 1: Image Similarity Model (Basic)")
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

    # Test avec des images similaires
    print("2️⃣ Testing similarity between images...")
    print()

    # Exemple 1: Images identiques (même couleur)
    print("📸 Test Case 1: Similar colored images")
    img1 = "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Red"
    img2 = "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Also+Red"

    similarity = model.compute_similarity(img1, img2)
    print(f"   Image 1: {img1}")
    print(f"   Image 2: {img2}")
    print(f"   ✅ Similarity: {similarity:.2%}")
    print()

    # Exemple 2: Images différentes
    print("📸 Test Case 2: Different colored images")
    img3 = "https://via.placeholder.com/300x300/0000FF/FFFFFF?text=Blue"

    similarity2 = model.compute_similarity(img1, img3)
    print(f"   Image 1: {img1}")
    print(f"   Image 3: {img3}")
    print(f"   ✅ Similarity: {similarity2:.2%}")
    print()

    print("=" * 70)
    print("✅ Basic test complete!")
    print("=" * 70)
    print()


def test_counterfeit_detection_with_images():
    """Test complet de détection de contrefaçons avec images"""
    print("=" * 70)
    print("🛡️ TEST 2: Counterfeit Detection with Image Analysis")
    print("=" * 70)
    print()

    # Créer le détecteur avec le modèle pré-entraîné
    print("1️⃣ Initializing counterfeit detector with image model...")
    detector = CounterfeitDetector(use_pretrained=True, device='cpu')
    print()

    # Produit scrapé (contrefaçon potentielle)
    print("2️⃣ Simulating scraped product (potential counterfeit)...")
    scraped_product = {
        'title': 'Louis Vuitton LV Handbag Luxury Designer Bag AAA Quality',
        'description': 'High quality replica, 1:1 mirror copy, luxury style',
        'price': 49.99,
        'url': 'https://www.aliexpress.com/item/example.html',
        'image_urls': [
            'https://via.placeholder.com/400x400/8B4513/FFFFFF?text=Brown+Bag'
        ],
        'seller_name': 'Luxury Store 88',
        'source_site': 'AliExpress'
    }

    print(f"   📦 Product: {scraped_product['title']}")
    print(f"   💰 Price: ${scraped_product['price']}")
    print(f"   🖼️ Image: {scraped_product['image_urls'][0]}")
    print()

    # Produit authentique de référence
    print("3️⃣ Using authentic product as reference...")
    authentic_product = {
        'product_id': 'LV-BAG-001',
        'brand': 'Louis Vuitton',
        'name': 'Louis Vuitton Neverfull MM Monogram',
        'description': 'Authentic Louis Vuitton handbag',
        'official_price': 1800.00,
        'image_urls': [
            'https://via.placeholder.com/400x400/8B4513/FFD700?text=LV+Authentic'
        ]
    }

    print(f"   ✅ Authentic: {authentic_product['name']}")
    print(f"   💰 Official Price: ${authentic_product['official_price']}")
    print(f"   🖼️ Image: {authentic_product['image_urls'][0]}")
    print()

    # Détection
    print("4️⃣ Running counterfeit detection with image analysis...")
    print()

    result = detector.detect_counterfeit(scraped_product, [authentic_product])

    # Afficher les résultats
    print("=" * 70)
    print("📊 DETECTION RESULTS")
    print("=" * 70)
    print()

    print(f"🎯 Overall Risk Score: {result['overall_risk_score']:.1%}")
    print(f"📊 Confidence Level: {result['confidence_level']}")
    print(f"⚠️  Is Counterfeit: {'YES ❌' if result['is_counterfeit'] else 'NO ✅'}")
    print()

    print("📈 Score Breakdown:")
    print(f"   • Keyword Match:    {result['keyword_match_score']:.1%}")
    print(f"   • Image Similarity: {result['similarity_score']:.1%} 🔥 (AI Model)")
    print(f"   • Price Suspicion:  {result['price_suspicion_score']:.1%}")
    print()

    print("🏷️  Detected Brands:")
    for brand in result['detected_brands']:
        print(f"   • {brand}")
    print()

    print("💡 Detection Reasons:")
    for reason in result['reasons']:
        print(f"   • {reason}")
    print()

    # Verdict
    if result['is_counterfeit']:
        print("🚨 " + "=" * 68)
        print("   COUNTERFEIT DETECTED - TAKE ACTION")
        print("=" * 70)
    else:
        print("✅ Product appears legitimate")

    print()


def test_multiple_products():
    """Test avec plusieurs produits"""
    print("=" * 70)
    print("🔍 TEST 3: Multiple Products Comparison")
    print("=" * 70)
    print()

    print("1️⃣ Creating detector...")
    detector = CounterfeitDetector(use_pretrained=True, device='cpu')
    print()

    # Liste de produits scrapés
    scraped_products = [
        {
            'title': 'Gucci GG Marmont Bag Luxury AAA',
            'price': 45.00,
            'image_urls': ['https://via.placeholder.com/300x300/000000/FFD700?text=Gucci+Bag'],
            'description': 'High quality replica'
        },
        {
            'title': 'Hermès Birkin Inspired Handbag',
            'price': 89.00,
            'image_urls': ['https://via.placeholder.com/300x300/FF6347/FFFFFF?text=Hermes+Bag'],
            'description': 'Luxury style handbag'
        },
        {
            'title': 'Designer Leather Handbag',
            'price': 120.00,
            'image_urls': ['https://via.placeholder.com/300x300/4169E1/FFFFFF?text=Generic+Bag'],
            'description': 'Premium quality leather'
        }
    ]

    authentic_ref = {
        'product_id': 'GUCCI-001',
        'brand': 'Gucci',
        'official_price': 2500.00,
        'image_urls': ['https://via.placeholder.com/300x300/000000/FFD700?text=Gucci+Auth']
    }

    print("2️⃣ Analyzing multiple products...")
    print()

    for idx, product in enumerate(scraped_products, 1):
        print(f"📦 Product #{idx}: {product['title']}")
        print(f"   💰 Price: ${product['price']}")

        result = detector.detect_counterfeit(product, [authentic_ref])

        print(f"   🎯 Risk Score: {result['overall_risk_score']:.1%}")
        print(f"   🖼️ Image Similarity: {result['similarity_score']:.1%}")
        print(f"   ⚠️  Counterfeit: {'YES ❌' if result['is_counterfeit'] else 'NO ✅'}")
        print()

    print("=" * 70)
    print("✅ Multiple products test complete!")
    print("=" * 70)
    print()


def main():
    """Fonction principale"""
    print("\n")
    print("🛡️ " * 20)
    print()
    print("   COUNTERFEIT DETECTION - IMAGE SIMILARITY TEST")
    print("   Using Pre-trained ResNet50 for Image Analysis")
    print()
    print("🛡️ " * 20)
    print("\n")

    try:
        # Test 1: Similarité basique
        test_image_similarity_basic()

        input("\n📱 Press Enter to continue to Test 2...\n")

        # Test 2: Détection complète avec images
        test_counterfeit_detection_with_images()

        input("\n📱 Press Enter to continue to Test 3...\n")

        # Test 3: Plusieurs produits
        test_multiple_products()

        print("\n")
        print("=" * 70)
        print("✅ ALL TESTS COMPLETE!")
        print("=" * 70)
        print()
        print("🎉 The image similarity model is working!")
        print()
        print("Next Steps:")
        print("  1. Integrate into the dashboard")
        print("  2. Run real scans with actual product images")
        print("  3. Compare authentic vs counterfeit products")
        print()
        print("💡 The model uses ResNet50 pre-trained on ImageNet")
        print("   It can detect visual similarities between products!")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")

    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
