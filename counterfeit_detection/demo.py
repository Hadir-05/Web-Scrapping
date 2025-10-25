"""
Script de démonstration du système de détection de contrefaçons
"""
from database.models import DatabaseManager
from scrapers.aliexpress_scraper import AliExpressScraper
from scrapers.dhgate_scraper import DHgateScraper
from detectors.counterfeit_detector import CounterfeitDetector
from datetime import datetime

def demo_basic_detection():
    """Démonstration basique de détection"""
    print("=" * 60)
    print("🛡️  ANTI-COUNTERFEIT DETECTION SYSTEM - DEMO")
    print("=" * 60)
    print()

    # Initialiser le détecteur
    print("1️⃣  Initializing detector...")
    detector = CounterfeitDetector()
    print(f"   ✅ Monitoring {len(detector.luxury_brands)} luxury brands")
    print()

    # Exemple de produit scrapé (simulé)
    print("2️⃣  Simulating scraped product...")
    scraped_product = {
        'title': 'Louis Vuitton LV Handbag Luxury Designer Bag High Quality AAA',
        'description': 'Luxury style handbag, top quality replica, 1:1 mirror copy',
        'price': 45.99,
        'url': 'https://www.aliexpress.com/item/example.html',
        'image_urls': ['https://example.com/image1.jpg'],
        'seller_name': 'Luxury Store 88',
        'source_site': 'AliExpress'
    }

    print(f"   Title: {scraped_product['title']}")
    print(f"   Price: ${scraped_product['price']}")
    print(f"   Site: {scraped_product['source_site']}")
    print()

    # Produit authentique de référence
    authentic_product = {
        'product_id': 'LV-BAG-001',
        'brand': 'Louis Vuitton',
        'name': 'Louis Vuitton Neverfull MM',
        'description': 'Authentic Louis Vuitton handbag',
        'official_price': 1500.00,
        'image_urls': ['https://example.com/auth-image1.jpg']
    }

    # Détection
    print("3️⃣  Running counterfeit detection...")
    result = detector.detect_counterfeit(scraped_product, [authentic_product])
    print()

    # Résultats
    print("=" * 60)
    print("📊 DETECTION RESULTS")
    print("=" * 60)
    print()

    print(f"🎯 Overall Risk Score: {result['overall_risk_score']:.1%}")
    print(f"📊 Confidence Level: {result['confidence_level']}")
    print(f"⚠️  Is Counterfeit: {'YES' if result['is_counterfeit'] else 'NO'}")
    print()

    print("📈 Score Breakdown:")
    print(f"   • Keyword Match: {result['keyword_match_score']:.1%}")
    print(f"   • Image Similarity: {result['similarity_score']:.1%}")
    print(f"   • Price Suspicion: {result['price_suspicion_score']:.1%}")
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
        print("🚨 " + "=" * 58)
        print("   COUNTERFEIT DETECTED - TAKE ACTION")
        print("=" * 60)
    else:
        print("✅ Product appears legitimate")

    print()


def demo_database():
    """Démonstration de la base de données"""
    print("=" * 60)
    print("💾 DATABASE DEMO")
    print("=" * 60)
    print()

    db = DatabaseManager()

    # Ajouter un produit authentique
    print("1️⃣  Adding authentic product...")
    auth = db.add_authentic_product(
        product_id="LV-BAG-001",
        brand="Louis Vuitton",
        name="Neverfull MM Monogram",
        description="Iconic tote bag",
        category="Handbags",
        official_price=1500.00,
        image_urls=["https://example.com/lv-bag.jpg"],
        keywords=["Louis Vuitton", "LV", "Neverfull", "monogram"]
    )
    print(f"   ✅ Added: {auth.name}")
    print()

    # Ajouter une contrefaçon
    print("2️⃣  Adding detected counterfeit...")
    counterfeit = db.add_counterfeit(
        detection_id=f"DEMO_{int(datetime.now().timestamp())}",
        source_site="AliExpress",
        source_url="https://www.aliexpress.com/item/example.html",
        title="LV Handbag Luxury Style AAA Quality",
        description="Replica handbag",
        price=45.99,
        currency="USD",
        image_urls=["https://example.com/fake.jpg"],
        seller_name="Luxury Store 88",
        authentic_product_id=auth.id,
        similarity_score=0.85,
        keyword_match_score=0.90,
        price_suspicion_score=0.95,
        overall_risk_score=0.88,
        confidence_level="HIGH",
        detected_brands=["Louis Vuitton"],
        status="DETECTED"
    )
    print(f"   ✅ Added counterfeit (Risk: {counterfeit.overall_risk_score:.1%})")
    print()

    # Statistiques
    print("3️⃣  Database Statistics...")
    stats = db.get_statistics()
    print(f"   • Total Counterfeits: {stats['total_counterfeits']}")
    print(f"   • Total Authentic: {stats['total_authentic']}")
    print(f"   • High Risk Items: {stats['high_risk_count']}")
    print()

    # Récupérer les contrefaçons
    print("4️⃣  Recent High-Risk Detections...")
    counterfeits = db.get_counterfeits(filters={'min_risk': 0.7}, limit=5)
    for c in counterfeits:
        print(f"   • {c.source_site}: {c.title[:50]}... (Risk: {c.overall_risk_score:.1%})")
    print()

    db.close()


def demo_scraper():
    """Démonstration du scraper (simulation)"""
    print("=" * 60)
    print("🔍 SCRAPER DEMO (Simulation)")
    print("=" * 60)
    print()

    print("Note: This is a simulation. Real scraping requires active internet.")
    print()

    scraper = AliExpressScraper()

    print(f"Site: {scraper.site_name}")
    print(f"Base URL: {scraper.base_url}")
    print()

    print("Search Query: 'Gucci bag'")
    print("Max Pages: 1")
    print()

    print("⚠️  To run real scraping:")
    print("   products = scraper.search('Gucci bag', max_pages=1)")
    print()

    # Produit simulé
    print("Simulated Product Result:")
    print("   Title: Gucci Style Handbag Designer Luxury AAA")
    print("   Price: $39.99")
    print("   Seller: Fashion Store 123")
    print("   URL: https://www.aliexpress.com/item/...")
    print()


def main():
    """Fonction principale de démo"""
    print("\n")
    print("🛡️ " * 20)
    print()
    print("   LUXURY ANTI-COUNTERFEIT DETECTION SYSTEM")
    print("   Version 1.0 - Demonstration")
    print()
    print("🛡️ " * 20)
    print("\n")

    try:
        # Démo 1: Détection basique
        demo_basic_detection()

        input("\n📱 Press Enter to continue to Database Demo...\n")

        # Démo 2: Base de données
        demo_database()

        input("\n📱 Press Enter to continue to Scraper Demo...\n")

        # Démo 3: Scraper
        demo_scraper()

        print("\n")
        print("=" * 60)
        print("✅ DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("  1. Launch the dashboard: streamlit run dashboard.py")
        print("  2. Run real scans from the 'New Scan' page")
        print("  3. Review detections in the 'Detections List'")
        print()
        print("📖 Read the README.md for complete documentation")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")

    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
