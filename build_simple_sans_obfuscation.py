#!/usr/bin/env python3
"""
Script pour créer un package client SANS obfuscation
À utiliser si PyArmor ne fonctionne pas correctement

ATTENTION : Le code source sera VISIBLE
Cette version est pour tests ou si le client est de confiance
"""
import shutil
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("  CRÉATION DU PACKAGE CLIENT - VERSION SIMPLE (SANS PROTECTION)")
print("=" * 80)
print()
print("⚠️  ATTENTION : Cette version ne protège PAS le code source")
print("⚠️  Le code sera VISIBLE et MODIFIABLE par le client")
print()

response = input("Continuer quand même ? (oui/non) : ")
if response.lower() != "oui":
    print("Annulé.")
    exit(0)

print()
print("=" * 80)
print("  PRÉPARATION DU PACKAGE")
print("=" * 80)
print()

# Configuration
VERSION = "1.0.0"
OUTPUT_DIR = Path("PACKAGE_CLIENT_SIMPLE")

# Fichiers et dossiers à copier
TO_COPY = {
    "files": [
        "app.py",
        "requirements.txt",
        "Lancer_Application.bat",
        "Lancer_Application.sh",
        "LISEZ-MOI.txt",
        "GUIDE_INSTALLATION_CLIENT.md",
        "README_CLIENT.txt",
    ],
    "folders": [
        "src",
        "RESULTATS",
    ]
}

# Nettoyer
if OUTPUT_DIR.exists():
    print(f"🗑️  Suppression de {OUTPUT_DIR}/")
    shutil.rmtree(OUTPUT_DIR)

# Créer
OUTPUT_DIR.mkdir(exist_ok=True)
print(f"📁 Création de {OUTPUT_DIR}/")
print()

# Copier les fichiers
print("📋 Copie des fichiers...")
for file in TO_COPY["files"]:
    if Path(file).exists():
        shutil.copy(file, OUTPUT_DIR)
        print(f"   ✅ {file}")
    else:
        print(f"   ⚠️  {file} (non trouvé)")

print()

# Copier les dossiers
print("📁 Copie des dossiers...")
for folder in TO_COPY["folders"]:
    src = Path(folder)
    dest = OUTPUT_DIR / folder

    if src.exists():
        # Copier le dossier entier
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(src, dest)
        print(f"   ✅ {folder}/")

        # Nettoyer les caches Python
        for cache_dir in dest.rglob("__pycache__"):
            shutil.rmtree(cache_dir)
        for pyc in dest.rglob("*.pyc"):
            pyc.unlink()

    else:
        print(f"   ⚠️  {folder}/ (non trouvé)")

print()
print("=" * 80)
print("  CRÉATION DU ZIP")
print("=" * 80)
print()

# Créer le ZIP
timestamp = datetime.now().strftime("%Y%m%d")
zip_name = f"AliExpress_Scraper_SIMPLE_v{VERSION}_{timestamp}"

print(f"📦 Création de {zip_name}.zip...")

try:
    shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)
    zip_size = Path(f"{zip_name}.zip").stat().st_size / (1024 * 1024)
    print(f"   ✅ ZIP créé : {zip_name}.zip")
    print(f"   📊 Taille : {zip_size:.2f} MB")
except Exception as e:
    print(f"   ❌ Erreur : {e}")

print()
print("=" * 80)
print("  ✅ PACKAGE CRÉÉ")
print("=" * 80)
print()
print(f"📦 Package : {OUTPUT_DIR}/")
print(f"📦 Archive : {zip_name}.zip")
print()
print("⚠️  ATTENTION : CODE SOURCE VISIBLE")
print()
print("💡 Pour protéger le code, utilisez plutôt :")
print("   - build_distribution_client_v2.py (avec PyArmor)")
print("   - OU PyInstaller pour compiler en .exe")
print()
print("🧪 TESTER :")
print(f"   cd {OUTPUT_DIR}")
print("   python app.py")
print()
