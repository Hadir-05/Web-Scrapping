#!/usr/bin/env python3
"""
Script pour obfusquer le code source avec PyArmor 7.x (ancienne version gratuite)
Cette version permet la distribution sans licence
"""
import os
import shutil
from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("  OBFUSCATION DU CODE SOURCE AVEC PYARMOR 7.x")
print("=" * 60)
print()

# Configuration
SOURCE_DIR = "src"
APP_FILE = "app.py"
OUTPUT_DIR = "distribution_client"

# Vérifier PyArmor
try:
    result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
    version = result.stdout.strip()
    print(f"✅ PyArmor installé : {version}")

    # Vérifier la version
    if "8." in version or "9." in version:
        print()
        print("⚠️  Vous avez PyArmor 8.x qui a des restrictions de licence")
        print("   Pour distribuer gratuitement, il faut PyArmor 7.x")
        print()
        print("📥 Installation de PyArmor 7.x :")
        print("   pip uninstall pyarmor -y")
        print("   pip install pyarmor==7.7.4")
        print()
        response = input("Voulez-vous que je l'installe automatiquement ? (o/n) : ")
        if response.lower() == 'o':
            print()
            print("🔄 Désinstallation de PyArmor 8.x...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "pyarmor", "-y"])
            print()
            print("📥 Installation de PyArmor 7.7.4...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyarmor==7.7.4"])
            print()
            print("✅ PyArmor 7.7.4 installé")
        else:
            print()
            print("❌ Obfuscation annulée")
            print("   Installez manuellement PyArmor 7.7.4 et relancez ce script")
            exit(1)
except FileNotFoundError:
    print("❌ PyArmor n'est pas installé")
    print()
    print("Installation : pip install pyarmor==7.7.4")
    exit(1)

print()

# Nettoyer
if Path(OUTPUT_DIR).exists():
    print(f"🗑️  Suppression de {OUTPUT_DIR}")
    shutil.rmtree(OUTPUT_DIR)

Path(OUTPUT_DIR).mkdir(exist_ok=True)

print()
print("🔒 Obfuscation du code source avec PyArmor 7.x...")
print()

# Obfusquer avec PyArmor 7 (syntaxe différente)
# PyArmor 7 : pyarmor obfuscate
# PyArmor 8 : pyarmor gen

# Obfusquer app.py
print("🔒 Obfuscation de app.py...")
subprocess.run([
    "pyarmor", "obfuscate",
    "--output", OUTPUT_DIR,
    "--recursive",
    APP_FILE
])

print()
print("🔒 Obfuscation de src/...")
# Pour PyArmor 7, on doit obfusquer le dossier src séparément
subprocess.run([
    "pyarmor", "obfuscate",
    "--output", f"{OUTPUT_DIR}/src",
    "--recursive",
    "--no-cross-protection",  # Important pour éviter les erreurs entre modules
    f"{SOURCE_DIR}/*.py"
])

# Obfusquer récursivement tous les sous-dossiers de src/
for subdir in Path(SOURCE_DIR).rglob("*"):
    if subdir.is_dir() and "__pycache__" not in str(subdir):
        rel_path = subdir.relative_to(SOURCE_DIR)
        output_path = Path(OUTPUT_DIR) / "src" / rel_path
        output_path.mkdir(parents=True, exist_ok=True)

        # Obfusquer les fichiers Python de ce sous-dossier
        py_files = list(subdir.glob("*.py"))
        if py_files:
            print(f"🔒 Obfuscation de {subdir}...")
            for py_file in py_files:
                subprocess.run([
                    "pyarmor", "obfuscate",
                    "--output", str(output_path),
                    "--no-cross-protection",
                    str(py_file)
                ], capture_output=True)

print()
print("📋 Copie des fichiers de configuration...")

# Copier les fichiers nécessaires
files_to_copy = [
    "requirements.txt",
    "Lancer_Application.bat",
    "Lancer_Application.sh",
    "LISEZ-MOI.txt",
    "GUIDE_INSTALLATION_CLIENT.md",
    "README_CLIENT.txt",
]

for file in files_to_copy:
    if Path(file).exists():
        shutil.copy(file, OUTPUT_DIR)
        print(f"  ✅ {file}")

# Copier les fichiers __init__.py non-obfusqués (ils sont souvent vides)
for init_file in Path(SOURCE_DIR).rglob("__init__.py"):
    rel_path = init_file.relative_to(SOURCE_DIR)
    dest = Path(OUTPUT_DIR) / "src" / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy(init_file, dest)

print()
print("=" * 60)
print("  ✅ OBFUSCATION TERMINÉE")
print("=" * 60)
print()
print(f"📦 Package prêt dans : {OUTPUT_DIR}/")
print()
print("🧪 TEST DU PACKAGE :")
print(f"  cd {OUTPUT_DIR}")
print("  python app.py")
print()
print("📦 CRÉER LE ZIP :")
print(f"  Compress-Archive -Path {OUTPUT_DIR} -Destination Client_v1.0.zip")
print()
print("✅ Le code obfusqué avec PyArmor 7.x peut être distribué GRATUITEMENT")
print("✅ Il fonctionnera sur n'importe quelle machine")
print()
