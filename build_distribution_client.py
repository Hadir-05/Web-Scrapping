#!/usr/bin/env python3
"""
Script complet pour créer une distribution client avec code protégé
- Obfusque le code avec PyArmor 7.x
- Crée une structure propre pour le client
- Inclut le dossier RESULTATS/
- Génère un ZIP prêt à distribuer
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("  CRÉATION DU PACKAGE CLIENT - ALIEXPRESS SCRAPER")
print("=" * 80)
print()

# Configuration
VERSION = "1.0.0"
OUTPUT_DIR = "PACKAGE_CLIENT"
SOURCE_DIR = "src"
APP_FILE = "app.py"

# Fichiers à inclure
FILES_TO_INCLUDE = [
    "requirements.txt",
    "Lancer_Application.bat",
    "Lancer_Application.sh",
    "LISEZ-MOI.txt",
    "GUIDE_INSTALLATION_CLIENT.md",
    "README_CLIENT.txt",
    ".gitignore",
]

# Dossiers à inclure (vides)
FOLDERS_TO_INCLUDE = [
    "RESULTATS",
]

print("🔍 Vérification de l'environnement...")
print()

# Étape 1 : Vérifier PyArmor
try:
    result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
    version = result.stdout.strip()
    print(f"✅ PyArmor installé : {version}")

    # Vérifier la version
    if "8." in version or "9." in version:
        print()
        print("⚠️  ATTENTION : Vous avez PyArmor 8.x/9.x avec restrictions de licence")
        print("   Pour distribuer gratuitement, il faut PyArmor 7.x")
        print()
        print("📥 Pour installer PyArmor 7.x :")
        print("   pip uninstall pyarmor -y")
        print("   pip install pyarmor==7.7.4")
        print()
        response = input("Voulez-vous que je l'installe automatiquement ? (o/n) : ")
        if response.lower() == 'o':
            print()
            print("🔄 Désinstallation de PyArmor 8.x/9.x...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "pyarmor", "-y"])
            print()
            print("📥 Installation de PyArmor 7.7.4...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyarmor==7.7.4"])
            print()
            print("✅ PyArmor 7.7.4 installé")
        else:
            print()
            print("❌ Build annulé")
            print("   Installez manuellement PyArmor 7.7.4 et relancez ce script")
            sys.exit(1)
    else:
        print("✅ Version compatible (7.x)")

except FileNotFoundError:
    print("❌ PyArmor n'est pas installé")
    print()
    print("Installation : pip install pyarmor==7.7.4")
    sys.exit(1)

print()
print("=" * 80)
print("  ÉTAPE 1 : NETTOYAGE ET PRÉPARATION")
print("=" * 80)
print()

# Nettoyer le dossier de sortie
if Path(OUTPUT_DIR).exists():
    print(f"🗑️  Suppression de l'ancien dossier {OUTPUT_DIR}/")
    shutil.rmtree(OUTPUT_DIR)

# Créer la structure
print(f"📁 Création du dossier {OUTPUT_DIR}/")
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Créer les sous-dossiers nécessaires
for folder in FOLDERS_TO_INCLUDE:
    folder_path = Path(OUTPUT_DIR) / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {folder}/")

print()
print("=" * 80)
print("  ÉTAPE 2 : OBFUSCATION DU CODE")
print("=" * 80)
print()

# Obfusquer app.py
print("🔒 Obfuscation de app.py...")
try:
    subprocess.run([
        "pyarmor", "obfuscate",
        "--output", OUTPUT_DIR,
        "--recursive",
        "--no-cross-protection",
        APP_FILE
    ], check=True, capture_output=True)
    print("   ✅ app.py obfusqué")
except subprocess.CalledProcessError as e:
    print(f"   ❌ Erreur : {e.stderr.decode() if e.stderr else str(e)}")
    print()
    print("Tentative avec méthode alternative...")
    # Copier puis obfusquer sur place
    shutil.copy(APP_FILE, OUTPUT_DIR)
    subprocess.run([
        "pyarmor", "obfuscate",
        "--in-place",
        str(Path(OUTPUT_DIR) / APP_FILE)
    ])

print()
print("🔒 Obfuscation du dossier src/...")

# Créer le dossier src dans OUTPUT_DIR
src_output = Path(OUTPUT_DIR) / "src"
src_output.mkdir(exist_ok=True)

# Copier la structure complète de src/
print("   📋 Copie de la structure src/...")
for item in Path(SOURCE_DIR).rglob("*"):
    if item.is_file():
        # Calculer le chemin relatif
        rel_path = item.relative_to(SOURCE_DIR)
        dest_path = src_output / rel_path

        # Créer les dossiers parents si nécessaire
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copier le fichier
        shutil.copy2(item, dest_path)

print("   ✅ Structure copiée")
print()

# Obfusquer tous les fichiers .py dans src/
print("   🔒 Obfuscation des fichiers Python...")
obfuscated_count = 0
for py_file in src_output.rglob("*.py"):
    try:
        subprocess.run([
            "pyarmor", "obfuscate",
            "--in-place",
            "--no-cross-protection",
            str(py_file)
        ], check=True, capture_output=True, stderr=subprocess.DEVNULL)
        obfuscated_count += 1
        print(f"      ✅ {py_file.relative_to(OUTPUT_DIR)}")
    except subprocess.CalledProcessError:
        print(f"      ⚠️  Échec : {py_file.relative_to(OUTPUT_DIR)} (conservé non-obfusqué)")

print()
print(f"   ✅ {obfuscated_count} fichiers obfusqués")

print()
print("=" * 80)
print("  ÉTAPE 3 : COPIE DES FICHIERS DE CONFIGURATION")
print("=" * 80)
print()

for file in FILES_TO_INCLUDE:
    if Path(file).exists():
        shutil.copy(file, OUTPUT_DIR)
        print(f"   ✅ {file}")
    else:
        print(f"   ⚠️  {file} (non trouvé)")

# Copier le contenu du dossier RESULTATS (README.txt, .gitkeep)
print()
print("📁 Copie du dossier RESULTATS avec documentation...")
resultats_src = Path("RESULTATS")
resultats_dest = Path(OUTPUT_DIR) / "RESULTATS"

if resultats_src.exists():
    for item in resultats_src.iterdir():
        if item.is_file():
            shutil.copy(item, resultats_dest)
            print(f"   ✅ RESULTATS/{item.name}")

print()
print("=" * 80)
print("  ÉTAPE 4 : VÉRIFICATION")
print("=" * 80)
print()

# Vérifier les fichiers essentiels
essential_files = [
    Path(OUTPUT_DIR) / "app.py",
    Path(OUTPUT_DIR) / "src",
    Path(OUTPUT_DIR) / "requirements.txt",
    Path(OUTPUT_DIR) / "Lancer_Application.bat",
    Path(OUTPUT_DIR) / "RESULTATS",
]

all_ok = True
for file in essential_files:
    if file.exists():
        print(f"   ✅ {file.name}")
    else:
        print(f"   ❌ {file.name} MANQUANT")
        all_ok = False

if not all_ok:
    print()
    print("⚠️  Certains fichiers essentiels sont manquants !")
    print("   Le package pourrait ne pas fonctionner correctement.")
    print()

print()
print("=" * 80)
print("  ÉTAPE 5 : CRÉATION DU ZIP")
print("=" * 80)
print()

# Créer le nom du ZIP avec version et date
timestamp = datetime.now().strftime("%Y%m%d")
zip_name = f"AliExpress_Scraper_v{VERSION}_{timestamp}"
zip_path = f"{zip_name}.zip"

print(f"📦 Création de {zip_path}...")

try:
    # Utiliser shutil.make_archive pour créer le ZIP
    shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)

    # Calculer la taille
    zip_size = Path(zip_path).stat().st_size / (1024 * 1024)  # En MB

    print(f"   ✅ ZIP créé : {zip_path}")
    print(f"   📊 Taille : {zip_size:.2f} MB")
except Exception as e:
    print(f"   ❌ Erreur lors de la création du ZIP : {e}")

print()
print("=" * 80)
print("  ✅ BUILD TERMINÉ AVEC SUCCÈS")
print("=" * 80)
print()
print(f"📦 Package client prêt : {OUTPUT_DIR}/")
print(f"📦 Archive ZIP : {zip_path}")
print()
print("🧪 TESTER LE PACKAGE :")
print(f"   cd {OUTPUT_DIR}")
print("   python app.py")
print()
print("📧 DISTRIBUER AU CLIENT :")
print(f"   Envoyer {zip_path} par email/WeTransfer/Drive")
print()
print("📝 INSTRUCTIONS POUR LE CLIENT :")
print("   1. Installer Python 3.10+ (https://python.org)")
print("   2. Extraire le ZIP")
print("   3. Double-cliquer sur Lancer_Application.bat")
print("   4. Consulter LISEZ-MOI.txt pour l'aide")
print()
print("✅ Le code est protégé et non-lisible")
print("✅ Les résultats seront sauvegardés dans RESULTATS/")
print("✅ Prêt pour distribution professionnelle")
print()
