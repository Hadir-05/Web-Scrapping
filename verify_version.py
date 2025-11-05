#!/usr/bin/env python3
"""
Script pour vérifier que vous avez la bonne version du code
"""
import os
from pathlib import Path

print("="*80)
print("VÉRIFICATION DE LA VERSION DU CODE")
print("="*80)

issues = []
ok = []

# 1. Vérifier les nouveaux fichiers
print("\n1️⃣ Vérification des nouveaux fichiers...")
new_files = ['test_clip.py', 'inspect_output.py', 'TROUBLESHOOTING.md']

for file in new_files:
    if Path(file).exists():
        print(f"   ✅ {file} présent")
        ok.append(f"{file} présent")
    else:
        print(f"   ❌ {file} MANQUANT")
        issues.append(f"{file} manquant - Faites: git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz")

# 2. Vérifier app.py (doit avoir le nouveau code sans st.form dans Export)
print("\n2️⃣ Vérification de app.py...")
app_path = Path("app.py")

if app_path.exists():
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()

    # Vérifier qu'il n'y a PAS de st.form dans la section Export
    if 'with st.form("export_form")' in app_content or 'with st.form(' in app_content.split('# Tab 3: Export')[1] if '# Tab 3: Export' in app_content else False:
        print(f"   ❌ app.py utilise encore st.form() dans Export")
        issues.append("app.py a l'ancien code avec st.form - Faites git pull")
    else:
        print(f"   ✅ app.py sans st.form dans Export (bon!)")
        ok.append("app.py sans st.form")

    # Vérifier le debug CLIP extensif
    if "=== CALCUL DE SIMILARITÉ AVEC DEBUG COMPLET ===" in app_content:
        print(f"   ✅ Debug CLIP extensif présent")
        ok.append("Debug CLIP extensif")
    else:
        print(f"   ❌ Debug CLIP manquant")
        issues.append("Debug CLIP manquant dans app.py")

# 3. Vérifier aliexpress_scraper.py (organisation par produit)
print("\n3️⃣ Vérification de aliexpress_scraper.py...")
scraper_path = Path("src/scraper/aliexpress_scraper.py")

if scraper_path.exists():
    with open(scraper_path, 'r', encoding='utf-8') as f:
        scraper_content = f.read()

    # Vérifier product_image_counters
    if "product_image_counters" in scraper_content:
        print(f"   ✅ Organisation par dossier produit présente")
        ok.append("Organisation par produit")
    else:
        print(f"   ❌ Organisation par dossier produit MANQUANTE")
        issues.append("Scraper a l'ancien code - Faites git pull")

    # Vérifier les multiples sélecteurs de prix
    if "price_selectors = [" in scraper_content:
        print(f"   ✅ Multiples sélecteurs de prix présents")
        ok.append("Sélecteurs prix")
    else:
        print(f"   ❌ Anciens sélecteurs de prix")
        issues.append("Sélecteurs prix non mis à jour")

# 4. Vérifier le dossier output
print("\n4️⃣ Vérification du dossier output...")
output_dir = Path("output")

if output_dir.exists():
    images_dir = output_dir / "images"
    if images_dir.exists():
        # Chercher des dossiers product_XXX
        product_dirs = [d for d in images_dir.iterdir() if d.is_dir() and d.name.startswith('product_')]

        if len(product_dirs) > 0:
            print(f"   ✅ {len(product_dirs)} dossiers produits trouvés (nouveau format!)")
            ok.append(f"{len(product_dirs)} dossiers produits")

            # Vérifier un dossier
            sample_dir = product_dirs[0]
            images_in_dir = list(sample_dir.glob('*.jpg')) + list(sample_dir.glob('*.png'))
            print(f"   ✅ {sample_dir.name} contient {len(images_in_dir)} images")
        else:
            # Ancien format
            flat_images = [f for f in images_dir.glob('*') if f.is_file()]
            if len(flat_images) > 0:
                print(f"   ⚠️ {len(flat_images)} images en format plat (ANCIEN FORMAT)")
                issues.append("Dossier output utilise l'ancien format - Supprimez-le et refaites un scraping")
            else:
                print(f"   ℹ️ Dossier images/ vide")
    else:
        print(f"   ℹ️ Dossier images/ n'existe pas encore (normal si pas de scraping)")
else:
    print(f"   ℹ️ Dossier output/ n'existe pas encore (normal si pas de scraping)")

# Résumé
print("\n" + "="*80)
print("RÉSUMÉ")
print("="*80)

if issues:
    print(f"\n❌ {len(issues)} PROBLÈME(S) DÉTECTÉ(S):\n")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")

    print(f"\n💡 SOLUTION:")
    print(f"   1. Faites: git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz")
    print(f"   2. Supprimez le dossier output: rm -rf output/")
    print(f"   3. Relancez l'app: streamlit run app.py")
    print(f"   4. Faites un NOUVEAU scraping")
else:
    print(f"\n✅ TOUT EST BON!")
    print(f"   {len(ok)} vérifications passées")
    print(f"\n   Si vous avez encore des problèmes:")
    print(f"   1. Supprimez output/: rm -rf output/")
    print(f"   2. Relancez l'app: streamlit run app.py")
    print(f"   3. Faites un NOUVEAU scraping avec les nouvelles données")

print("="*80)
