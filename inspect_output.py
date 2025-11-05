#!/usr/bin/env python3
"""
Script pour inspecter le dossier output et diagnostiquer les problèmes
"""
import json
from pathlib import Path

def inspect_output(output_dir="output"):
    """Inspecte le dossier output et affiche des statistiques"""
    output_path = Path(output_dir)

    print("="*80)
    print(f"INSPECTION DU DOSSIER: {output_path.absolute()}")
    print("="*80)

    if not output_path.exists():
        print(f"❌ Le dossier {output_dir} n'existe pas")
        print(f"💡 Lancez d'abord un scraping depuis l'application Streamlit")
        return

    # 1. Vérifier product_data.json
    print("\n1️⃣ Fichier product_data.json:")
    product_data_path = output_path / "product_data.json"

    if product_data_path.exists():
        with open(product_data_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"   ✅ Fichier trouvé")
        print(f"   📦 Nombre de produits: {len(products)}")

        if len(products) > 0:
            print(f"\n   Exemple de produit:")
            prod = products[0]
            print(f"   - URL: {prod.get('item_url', 'N/A')[:60]}...")
            print(f"   - Titre: {prod.get('title', 'N/A')[:60]}...")
            print(f"   - Prix: {prod.get('price', 'N/A')}")
            print(f"   - Images: {len(prod.get('product_image_paths', []))} URLs")
            if prod.get('product_image_paths'):
                print(f"   - Exemple URL image: {prod['product_image_paths'][0][:60]}...")
    else:
        print(f"   ❌ Fichier non trouvé")

    # 2. Vérifier image_metadata.json
    print("\n2️⃣ Fichier image_metadata.json:")
    image_metadata_path = output_path / "image_metadata.json"

    if image_metadata_path.exists():
        with open(image_metadata_path, 'r', encoding='utf-8') as f:
            images = json.load(f)
        print(f"   ✅ Fichier trouvé")
        print(f"   🖼️ Nombre d'entrées: {len(images)}")

        # Vérifier les champs
        has_local_path = 0
        local_path_exists = 0

        for img in images[:5]:  # Vérifier les 5 premiers
            if 'local_path' in img:
                has_local_path += 1
                if Path(img['local_path']).exists():
                    local_path_exists += 1

        print(f"   Vérification (5 premières entrées):")
        print(f"   - Avec 'local_path': {has_local_path}/5")
        print(f"   - Fichiers existants: {local_path_exists}/5")

        if has_local_path > 0:
            print(f"   ✅ Le champ 'local_path' est présent")
            if local_path_exists > 0:
                print(f"   ✅ Les fichiers locaux existent")
            else:
                print(f"   ❌ Les fichiers locaux n'existent PAS")
        else:
            print(f"   ❌ Le champ 'local_path' est MANQUANT")
            print(f"   💡 Problème: Les images ne peuvent pas être trouvées par CLIP")

        if len(images) > 0:
            print(f"\n   Exemple d'entrée:")
            img = images[0]
            print(f"   - src: {img.get('src', 'N/A')[:60]}...")
            print(f"   - link: {img.get('link', 'N/A')[:60]}...")
            print(f"   - local_path: {img.get('local_path', 'MANQUANT')}")
    else:
        print(f"   ❌ Fichier non trouvé")

    # 3. Vérifier le dossier images/
    print("\n3️⃣ Dossier images/:")
    images_dir = output_path / "images"

    if images_dir.exists():
        print(f"   ✅ Dossier trouvé: {images_dir.absolute()}")

        # Compter les sous-dossiers produits
        product_dirs = [d for d in images_dir.iterdir() if d.is_dir() and d.name.startswith('product_')]
        print(f"   📁 Sous-dossiers produits: {len(product_dirs)}")

        if len(product_dirs) > 0:
            print(f"   ✅ Organisation par produit détectée")
            # Inspecter quelques dossiers
            for i, prod_dir in enumerate(sorted(product_dirs)[:3]):
                images_in_dir = list(prod_dir.glob('*'))
                print(f"      {prod_dir.name}: {len(images_in_dir)} fichiers")
                if images_in_dir:
                    print(f"         Exemples: {', '.join([img.name for img in images_in_dir[:3]])}")
        else:
            # Ancien format: images à plat
            all_images = [f for f in images_dir.glob('*') if f.is_file()]
            print(f"   📄 Images à plat (ancien format): {len(all_images)}")

            if len(all_images) > 0:
                print(f"   ⚠️ Format ancien détecté (images non organisées)")
                print(f"   Exemples: {', '.join([img.name for img in all_images[:3]])}")
    else:
        print(f"   ❌ Dossier non trouvé")

    # 4. Résumé et recommandations
    print("\n" + "="*80)
    print("RÉSUMÉ ET DIAGNOSTIC:")
    print("="*80)

    issues = []
    if not product_data_path.exists():
        issues.append("❌ product_data.json manquant")
    if not image_metadata_path.exists():
        issues.append("❌ image_metadata.json manquant")
    elif has_local_path == 0:
        issues.append("❌ Champ 'local_path' manquant dans image_metadata.json")
    elif local_path_exists == 0:
        issues.append("❌ Les fichiers d'images n'existent pas aux chemins spécifiés")
    if not images_dir.exists():
        issues.append("❌ Dossier images/ manquant")

    if issues:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        for issue in issues:
            print(f"   {issue}")

        print("\n💡 SOLUTIONS:")
        if not product_data_path.exists() or not image_metadata_path.exists():
            print("   1. Lancez un nouveau scraping depuis l'application")
            print("   2. Assurez-vous que le scraping se termine avec succès")

        if has_local_path == 0:
            print("   1. Mettez à jour le code du scraper (déjà fait dans la dernière version)")
            print("   2. Relancez un nouveau scraping")

        if not images_dir.exists() or local_path_exists == 0:
            print("   1. Vérifiez que le scraping télécharge bien les images")
            print("   2. Regardez les logs du scraper pour voir les erreurs de téléchargement")
    else:
        print("\n✅ TOUT SEMBLE BON!")
        print("   Si le score CLIP est toujours 0, lancez: python test_clip.py")

if __name__ == "__main__":
    inspect_output()
