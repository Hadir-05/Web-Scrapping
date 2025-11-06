"""
Diagnostic spécifique pour comprendre pourquoi les images ne s'affichent pas dans Export
"""
import json
import os
from pathlib import Path

print("=" * 80)
print("🔍 DIAGNOSTIC IMAGES ONGLET EXPORT")
print("=" * 80)

# 1. Chercher les données de recherche
search_dirs = sorted(Path(".").glob("output_recherche*"), reverse=True)

if not search_dirs:
    print("\n❌ Aucun dossier output_recherche* trouvé!")
    print("\n💡 VOUS DEVEZ D'ABORD:")
    print("   1. git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz")
    print("   2. streamlit run app.py")
    print("   3. Faire un NOUVEAU scraping avec mes correctifs")
    print("   4. Les images devraient alors s'afficher!")
    exit(0)

print(f"\n📂 Dossiers de recherche trouvés: {len(search_dirs)}")
for d in search_dirs[:3]:
    print(f"   {d.name}")

# 2. Analyser le plus récent
latest_dir = search_dirs[0]
print(f"\n📁 Analyse du dossier: {latest_dir.name}")

product_file = latest_dir / "product_data.json"
image_metadata_file = latest_dir / "image_metadata.json"

if not product_file.exists():
    print(f"\n❌ {product_file} n'existe pas!")
    exit(1)

# 3. Charger les données produits
with open(product_file, 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"\n📊 Produits trouvés: {len(products)}")

# 4. Analyser les 3 premiers produits
for idx, product in enumerate(products[:3], 1):
    print(f"\n{'='*60}")
    print(f"🔍 PRODUIT #{idx}")
    print(f"{'='*60}")

    print(f"📌 Titre: {product.get('title', 'N/A')[:60]}...")
    print(f"💰 Prix: {product.get('price', 'N/A')}")

    # Analyser les images
    img_paths = product.get('product_image_paths', [])
    print(f"\n🖼️ Nombre d'URLs dans product_image_paths: {len(img_paths)}")

    if len(img_paths) == 0:
        print("   ❌ PROBLÈME: Aucune URL d'image!")
        print("   💡 Le scraper n'a pas trouvé d'images pour ce produit")
        continue

    # Vérifier la première image
    first_img_url = img_paths[0]
    print(f"\n📸 Première image:")
    print(f"   URL: {first_img_url[:80]}...")
    print(f"   Type: {type(first_img_url)}")
    print(f"   Longueur URL: {len(str(first_img_url))}")

    # Vérifier si c'est une URL valide
    if first_img_url.startswith('http'):
        print(f"   ✅ URL valide (commence par http)")
    else:
        print(f"   ⚠️ URL invalide (ne commence pas par http)")
        print(f"   Contenu: {first_img_url}")

# 5. Vérifier image_metadata.json
print(f"\n{'='*60}")
print(f"🗂️ MÉTADONNÉES DES IMAGES")
print(f"{'='*60}")

if image_metadata_file.exists():
    with open(image_metadata_file, 'r', encoding='utf-8') as f:
        image_metadata = json.load(f)

    print(f"📊 Métadonnées d'images: {len(image_metadata)}")

    # Compter combien ont local_path
    with_local_path = 0
    local_exists = 0

    for img_meta in image_metadata[:5]:
        src = img_meta.get('src', '')
        local_path = img_meta.get('local_path', '')

        if local_path:
            with_local_path += 1
            if Path(local_path).exists():
                local_exists += 1

    print(f"   Images avec local_path: {with_local_path}/{len(image_metadata)}")
    print(f"   Fichiers locaux existants: {local_exists}/{with_local_path}")

    if with_local_path == 0:
        print(f"\n   ⚠️ PROBLÈME: Aucune image n'a de local_path!")
        print(f"   💡 Cela signifie que le handler ITEM_IMG n'a jamais été appelé")
        print(f"   💡 Solution: Vérifier max_requests_per_crawl dans les logs")
else:
    print(f"   ⚠️ Fichier image_metadata.json n'existe pas")

# 6. Vérifier les images téléchargées
images_dir = latest_dir / "images"
if images_dir.exists():
    product_dirs = [d for d in images_dir.iterdir() if d.is_dir()]
    print(f"\n📸 Dossiers produits: {len(product_dirs)}")

    total_images = 0
    for prod_dir in sorted(product_dirs)[:5]:
        images = list(prod_dir.glob("*"))
        total_images += len(images)
        print(f"   {prod_dir.name}: {len(images)} images")

    print(f"   Total images téléchargées: {total_images}")

    if total_images == 0:
        print(f"\n   ❌ AUCUNE IMAGE TÉLÉCHARGÉE!")
        print(f"   💡 Le handler ITEM_IMG n'a pas été exécuté")
else:
    print(f"\n   ❌ Dossier images/ n'existe pas")

# 7. Conclusion
print(f"\n{'='*80}")
print(f"📋 CONCLUSION")
print(f"{'='*80}")

if len(products) > 0 and len(products[0].get('product_image_paths', [])) > 0:
    first_url = products[0]['product_image_paths'][0]
    if first_url.startswith('http'):
        print(f"✅ Les URLs d'images sont présentes dans product_data.json")
        print(f"✅ L'onglet Export DEVRAIT afficher les images depuis ces URLs")
        print(f"\n💡 SI VOUS NE VOYEZ PAS LES IMAGES:")
        print(f"   1. Avez-vous fait: git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz ?")
        print(f"   2. Avez-vous relancé l'app: streamlit run app.py ?")
        print(f"   3. Dans l'onglet Export, les images devraient s'afficher depuis internet avec 🌐")
        print(f"   4. Si ça ne marche toujours pas, envoyez-moi une capture d'écran")
    else:
        print(f"❌ Les URLs d'images sont INVALIDES!")
        print(f"   Exemple: {first_url}")
        print(f"   💡 Il faut refaire un scraping avec les nouveaux correctifs")
else:
    print(f"❌ Aucune image trouvée dans les données")
    print(f"💡 Il faut refaire un scraping pour tester les correctifs")

print(f"\n{'='*80}")
