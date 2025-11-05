#!/usr/bin/env python3
"""
Script de diagnostic pour comprendre pourquoi les images ne se téléchargent pas
"""
import json
from pathlib import Path
import sys

print("="*80)
print("DIAGNOSTIC - PROBLÈME TÉLÉCHARGEMENT IMAGES")
print("="*80)

output_dir = Path("output")

if not output_dir.exists():
    print("\n❌ Le dossier output/ n'existe pas!")
    print("💡 Vous devez d'abord faire un scraping.")
    sys.exit(1)

print("\n✅ Dossier output/ existe")

# 1. Vérifier product_data.json
print("\n" + "="*80)
print("1️⃣ ANALYSE DE product_data.json")
print("="*80)

product_data_path = output_dir / "product_data.json"
if not product_data_path.exists():
    print("❌ product_data.json n'existe pas!")
    sys.exit(1)

with open(product_data_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ Nombre de produits: {len(products)}")

if len(products) == 0:
    print("❌ Aucun produit trouvé!")
    sys.exit(1)

# Analyser les URLs d'images dans product_data
total_image_urls = 0
products_without_images = 0

for idx, prod in enumerate(products, 1):
    img_paths = prod.get('product_image_paths', [])
    if len(img_paths) == 0:
        products_without_images += 1
    total_image_urls += len(img_paths)

    if idx <= 3:  # Afficher les 3 premiers
        print(f"\nProduit {idx}:")
        print(f"  URL: {prod.get('item_url', 'N/A')[:60]}...")
        print(f"  Prix: {prod.get('price', 'N/A')}")
        print(f"  URLs d'images: {len(img_paths)}")
        for i, img_url in enumerate(img_paths[:3], 1):
            print(f"    {i}. {img_url[:70]}...")

print(f"\n📊 Résumé:")
print(f"  Total URLs d'images dans product_data: {total_image_urls}")
print(f"  Produits sans images: {products_without_images}/{len(products)}")

if total_image_urls == 0:
    print("\n❌ PROBLÈME: Aucune URL d'image trouvée dans product_data.json!")
    print("💡 Cela signifie que l'extraction des images sur la page produit échoue.")
    print("💡 Vérifiez les logs du scraper pour voir:")
    print("   - '🖼️ Extraction des images...'")
    print("   - 'Trouvé: X images'")
    print("   - Si X = 0, le sélecteur ne trouve rien")
    sys.exit(1)

# 2. Vérifier image_metadata.json
print("\n" + "="*80)
print("2️⃣ ANALYSE DE image_metadata.json")
print("="*80)

image_metadata_path = output_dir / "image_metadata.json"
if not image_metadata_path.exists():
    print("❌ image_metadata.json n'existe pas!")
    print("💡 Cela signifie que le handler d'images (ITEM_IMG) n'est JAMAIS appelé.")
    print("💡 Problèmes possibles:")
    print("   1. Les requêtes d'images ne sont pas ajoutées à la queue")
    print("   2. Le router ne route pas vers ITEM_IMG")
    print("   3. Le crawler se termine avant de traiter les images")
    sys.exit(1)

with open(image_metadata_path, 'r', encoding='utf-8') as f:
    images_meta = json.load(f)

print(f"✅ Nombre d'entrées dans image_metadata: {len(images_meta)}")

if len(images_meta) == 0:
    print("❌ image_metadata.json est vide!")
    print("💡 Le fichier existe mais aucune image n'a été traitée.")
    sys.exit(1)

# Vérifier les chemins locaux
has_local_path = 0
local_path_exists = 0

print("\nÉchantillon (3 premières):")
for idx, img_meta in enumerate(images_meta[:3], 1):
    src = img_meta.get('src', 'N/A')
    local_path = img_meta.get('local_path', 'MANQUANT')

    print(f"\nImage {idx}:")
    print(f"  src: {src[:70]}...")
    print(f"  local_path: {local_path}")

    if 'local_path' in img_meta:
        has_local_path += 1
        if Path(local_path).exists():
            local_path_exists += 1
            size = Path(local_path).stat().st_size
            print(f"  ✅ Fichier existe ({size} bytes)")
        else:
            print(f"  ❌ Fichier n'existe PAS")
    else:
        print(f"  ❌ Pas de champ local_path")

print(f"\n📊 Résumé:")
print(f"  Entrées avec local_path: {has_local_path}/{len(images_meta)}")
print(f"  Fichiers existants: {local_path_exists}/{len(images_meta)}")

if has_local_path == 0:
    print("\n❌ PROBLÈME: Aucun champ 'local_path' dans image_metadata.json!")
    print("💡 Version du code trop ancienne. Faites: git pull")
    sys.exit(1)

if local_path_exists == 0:
    print("\n❌ PROBLÈME: Les chemins local_path sont dans les métadonnées mais les fichiers n'existent pas!")
    print("💡 Cela signifie que l'écriture du fichier échoue.")
    print("💡 Vérifiez dans les logs:")
    print("   - '📥 Téléchargement image produit #X'")
    print("   - '✅ Image Y/3: ...'")
    print("   - S'il n'y a pas ces lignes, le téléchargement échoue silencieusement")

# 3. Vérifier le dossier images/
print("\n" + "="*80)
print("3️⃣ ANALYSE DU DOSSIER images/")
print("="*80)

images_dir = output_dir / "images"
if not images_dir.exists():
    print("❌ Le dossier images/ n'existe pas!")
    print("💡 Aucune tentative de création de dossier.")
    sys.exit(1)

print(f"✅ Dossier images/ existe: {images_dir.absolute()}")

# Chercher des sous-dossiers produits
product_dirs = [d for d in images_dir.iterdir() if d.is_dir() and d.name.startswith('product_')]
print(f"📁 Sous-dossiers produits trouvés: {len(product_dirs)}")

if len(product_dirs) == 0:
    print("❌ Aucun sous-dossier product_XXX trouvé!")
    print("💡 Le code ne crée pas les dossiers produits.")

    # Vérifier si des images en format plat
    flat_images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
    if len(flat_images) > 0:
        print(f"⚠️ {len(flat_images)} images en format plat (ancien format)")
    else:
        print("❌ Aucune image du tout dans images/")
    sys.exit(1)

# Analyser chaque dossier produit
print("\nContenu des dossiers produits:")
total_images_on_disk = 0

for prod_dir in sorted(product_dirs)[:5]:  # Les 5 premiers
    images_in_dir = list(prod_dir.glob('*'))
    total_images_on_disk += len(images_in_dir)

    print(f"\n{prod_dir.name}:")
    print(f"  Nombre de fichiers: {len(images_in_dir)}")

    if len(images_in_dir) > 0:
        for img_file in images_in_dir[:3]:
            size = img_file.stat().st_size
            print(f"    ✅ {img_file.name} ({size} bytes)")
    else:
        print(f"    ❌ Dossier vide!")

print(f"\n📊 Résumé:")
print(f"  Total fichiers images sur disque: {total_images_on_disk}")
print(f"  Attendu (d'après metadata): {local_path_exists}")

# 4. DIAGNOSTIC FINAL
print("\n" + "="*80)
print("🔍 DIAGNOSTIC FINAL")
print("="*80)

if total_images_on_disk > 0:
    print("\n✅ Des images EXISTENT sur le disque!")
    print(f"   Total: {total_images_on_disk} fichiers")
    print(f"   Dossiers: {len(product_dirs)} dossiers produits")
    print("\n💡 Si vous ne les voyez pas dans l'app:")
    print("   1. Vérifiez que vous regardez le bon onglet (Résultats Détaillés)")
    print("   2. Actualisez la page (F5)")
    print("   3. Relancez l'app: streamlit run app.py")
else:
    print("\n❌ AUCUNE IMAGE SUR LE DISQUE!")
    print("\n📋 Récapitulatif du problème:")
    print(f"   - URLs d'images trouvées: {total_image_urls}")
    print(f"   - Entrées dans metadata: {len(images_meta)}")
    print(f"   - Fichiers créés: {total_images_on_disk}")

    print("\n🎯 CAUSE PROBABLE:")
    if total_image_urls == 0:
        print("   ❌ Le scraper ne trouve pas les images sur les pages produit")
        print("   💡 Solution: Le sélecteur CSS est incorrect")
    elif len(images_meta) == 0:
        print("   ❌ Le handler ITEM_IMG n'est jamais appelé")
        print("   💡 Solution: Les requêtes d'images ne sont pas ajoutées à la queue")
    else:
        print("   ❌ Le handler est appelé mais l'écriture échoue")
        print("   💡 Solution: Problème avec response.body() ou permissions")

    print("\n📝 PROCHAINES ÉTAPES:")
    print("   1. Lancez un nouveau scraping avec: streamlit run app.py")
    print("   2. REGARDEZ le terminal pendant le scraping")
    print("   3. Cherchez ces lignes:")
    print("      - '🖼️ Extraction des images...'")
    print("      - 'Trouvé: X images'")
    print("      - '📥 Téléchargement image produit #X'")
    print("      - '✅ Image Y/3: ...'")
    print("   4. COPIEZ-COLLEZ ici la section complète d'UN produit")
    print("      (de '🛍️ Traitement produit' jusqu'à '✅ Produit sauvegardé')")

print("\n" + "="*80)
