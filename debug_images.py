"""
Script de diagnostic pour comprendre pourquoi les images ne s'affichent pas
"""
import json
import os
from pathlib import Path

print("=" * 80)
print("🔍 DIAGNOSTIC DES IMAGES")
print("=" * 80)

# 1. Chercher les fichiers de données
output_dir = Path("output")
print(f"\n📁 Dossier output: {output_dir.exists()}")

# Crawlee storage
storage_dir = Path("storage")
print(f"📁 Dossier storage: {storage_dir.exists()}")

if storage_dir.exists():
    print("\n📂 Contenu de storage/:")
    for item in storage_dir.rglob("*"):
        if item.is_file() and item.suffix == ".json":
            print(f"   {item}")

# 2. Chercher product_data.json
product_files = list(Path(".").rglob("product_data.json"))
print(f"\n📋 Fichiers product_data.json trouvés: {len(product_files)}")
for pf in product_files:
    print(f"   {pf}")

# 3. Si on trouve des données, les analyser
if product_files:
    product_file = product_files[0]
    print(f"\n📖 Analyse de {product_file}:")

    with open(product_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"   Nombre de produits: {len(products)}")

    if len(products) > 0:
        print(f"\n🔍 Premier produit:")
        p = products[0]
        print(f"   Titre: {p.get('title', 'N/A')[:60]}...")
        print(f"   Prix: {p.get('price', 'N/A')}")
        print(f"   URL produit: {p.get('item_url', 'N/A')[:60]}...")

        img_paths = p.get('product_image_paths', [])
        print(f"   Nombre d'images dans product_image_paths: {len(img_paths)}")

        if len(img_paths) > 0:
            print(f"\n🖼️ URLs des images:")
            for idx, img_url in enumerate(img_paths[:3], 1):
                print(f"      {idx}. {img_url[:80]}...")
                print(f"         Type: {type(img_url)}")
                print(f"         Longueur: {len(str(img_url))}")
        else:
            print(f"   ⚠️ PROBLÈME: product_image_paths est VIDE!")
else:
    print("\n❌ AUCUN fichier product_data.json trouvé!")
    print("\n💡 SOLUTION:")
    print("   1. Faites un git pull pour récupérer les derniers correctifs")
    print("   2. Lancez l'application: streamlit run app.py")
    print("   3. Uploadez une image et lancez une nouvelle recherche")
    print("   4. Les images devraient alors s'afficher!")

# 4. Vérifier les images téléchargées
images_dir = output_dir / "images"
if images_dir.exists():
    product_dirs = [d for d in images_dir.iterdir() if d.is_dir()]
    print(f"\n📸 Dossiers produits dans output/images: {len(product_dirs)}")

    total_images = 0
    for prod_dir in sorted(product_dirs)[:5]:
        images = list(prod_dir.glob("*"))
        total_images += len(images)
        print(f"   {prod_dir.name}: {len(images)} images")

    print(f"   Total images téléchargées: {total_images}")
else:
    print(f"\n⚠️ Dossier output/images n'existe pas")

print("\n" + "=" * 80)
