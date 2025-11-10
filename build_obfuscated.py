#!/usr/bin/env python3
"""
Script pour obfusquer le code source avec PyArmor
Le client recevra du code illisible mais fonctionnel
"""
import os
import shutil
from pathlib import Path

print("=" * 60)
print("  OBFUSCATION DU CODE SOURCE AVEC PYARMOR")
print("=" * 60)
print()

# Configuration
SOURCE_DIR = "src"
OBFUSCATED_DIR = "src_obfuscated"
OUTPUT_DIR = "distribution_client"

# Vérifier que PyArmor est installé
try:
    import pyarmor
    print("✅ PyArmor est installé")
except ImportError:
    print("❌ PyArmor n'est pas installé")
    print("Installation : pip install pyarmor")
    exit(1)

# Nettoyer les anciennes obfuscations
if Path(OBFUSCATED_DIR).exists():
    print(f"🗑️  Suppression de {OBFUSCATED_DIR}")
    shutil.rmtree(OBFUSCATED_DIR)

if Path(OUTPUT_DIR).exists():
    print(f"🗑️  Suppression de {OUTPUT_DIR}")
    shutil.rmtree(OUTPUT_DIR)

print()
print("🔒 Obfuscation du code source...")
print()

# Obfusquer le dossier src/
os.system(f"pyarmor gen -O {OBFUSCATED_DIR} -r {SOURCE_DIR}")

print()
print("📦 Création du package de distribution...")
print()

# Créer le dossier de distribution
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Copier les fichiers nécessaires
files_to_copy = [
    "app.py",
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

# Obfusquer app.py aussi
print()
print("🔒 Obfuscation de app.py...")
os.system(f"pyarmor gen -O {OUTPUT_DIR} app.py")

# Copier le code obfusqué
print()
print(f"📁 Copie du code obfusqué vers {OUTPUT_DIR}/src/")
shutil.copytree(OBFUSCATED_DIR, f"{OUTPUT_DIR}/src")

# Nettoyer
shutil.rmtree(OBFUSCATED_DIR)

print()
print("=" * 60)
print("  ✅ OBFUSCATION TERMINÉE")
print("=" * 60)
print()
print(f"📦 Package prêt dans : {OUTPUT_DIR}/")
print()
print("📋 Prochaines étapes :")
print("  1. Tester le package : cd distribution_client && python app.py")
print("  2. Créer le ZIP : Compress-Archive -Path distribution_client -Destination Client.zip")
print("  3. Envoyer au client")
print()
print("⚠️  Le code obfusqué est difficilement lisible mais PAS inviolable")
print()
