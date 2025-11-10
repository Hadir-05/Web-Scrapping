#!/usr/bin/env python3
"""
Script d'obfuscation avec debug détaillé
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("  OBFUSCATION AVEC DEBUG")
print("=" * 70)
print()

# Vérifier PyArmor
print("🔍 Vérification de PyArmor...")
try:
    result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
    version = result.stdout.strip()
    print(f"✅ PyArmor version: {version}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("Installation: pip install pyarmor==7.7.4")
    exit(1)

# Vérifier si c'est PyArmor 8
if "8." in version or "9." in version:
    print()
    print("⚠️  Vous avez PyArmor 8.x - il faut downgrade vers 7.x")
    print()
    print("Commandes à exécuter manuellement:")
    print("  pip uninstall pyarmor -y")
    print("  pip install pyarmor==7.7.4")
    print("  python build_obfuscated_debug.py")
    print()
    exit(1)

print()

# Configuration
OUTPUT_DIR = "distribution_client"

# Nettoyer
if Path(OUTPUT_DIR).exists():
    print(f"🗑️  Suppression de {OUTPUT_DIR}")
    shutil.rmtree(OUTPUT_DIR)

print()
print("📁 Création du dossier de sortie...")
Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(f"{OUTPUT_DIR}/src").mkdir(exist_ok=True)

print()
print("=" * 70)
print("  MÉTHODE SIMPLIFIÉE: Obfuscation avec --src")
print("=" * 70)
print()

# Méthode simplifiée pour PyArmor 7
# On obfusque app.py et on lui dit où trouver src/
print("🔒 Obfuscation de app.py avec le module src/...")
cmd = [
    "pyarmor",
    "obfuscate",
    "--output", OUTPUT_DIR,
    "--src", "src",  # Dire à PyArmor où sont les modules
    "--recursive",
    "app.py"
]

print(f"Commande: {' '.join(cmd)}")
print()

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Vérifier le résultat
app_py_path = Path(OUTPUT_DIR) / "app.py"
if app_py_path.exists():
    print("✅ app.py créé")
    print(f"   Taille: {app_py_path.stat().st_size} bytes")
else:
    print("❌ app.py N'A PAS été créé")
    print()
    print("Essayons une autre méthode...")
    print()

    # Méthode alternative: copier puis obfusquer sur place
    print("🔄 Méthode alternative: copier puis obfusquer")

    # Copier tous les fichiers
    print("📋 Copie des fichiers sources...")
    shutil.copy("app.py", OUTPUT_DIR)
    shutil.copytree("src", f"{OUTPUT_DIR}/src", dirs_exist_ok=True)

    # Obfusquer sur place
    print()
    print("🔒 Obfuscation sur place...")
    os.chdir(OUTPUT_DIR)

    cmd2 = ["pyarmor", "obfuscate", "--in-place", "app.py"]
    print(f"Commande: {' '.join(cmd2)}")
    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    print(result2.stdout)

    # Obfusquer src/
    print()
    print("🔒 Obfuscation de src/...")
    for py_file in Path("src").rglob("*.py"):
        if "__pycache__" not in str(py_file):
            print(f"   Obfuscation de {py_file}...")
            cmd3 = ["pyarmor", "obfuscate", "--in-place", str(py_file)]
            subprocess.run(cmd3, capture_output=True)

    os.chdir("..")

print()
print("📋 Copie des fichiers de configuration...")

# Copier les fichiers nécessaires
files_to_copy = [
    "requirements.txt",
    "Lancer_Application.bat",
    "Lancer_Application.sh",
    "LISEZ-MOI.txt",
    "GUIDE_INSTALLATION_CLIENT.md",
]

for file in files_to_copy:
    if Path(file).exists():
        dest = Path(OUTPUT_DIR) / file
        if not dest.exists():
            shutil.copy(file, OUTPUT_DIR)
            print(f"  ✅ {file}")

print()
print("=" * 70)
print("  VÉRIFICATION DU CONTENU")
print("=" * 70)
print()

# Lister le contenu
print(f"📁 Contenu de {OUTPUT_DIR}/:")
for item in sorted(Path(OUTPUT_DIR).iterdir()):
    if item.is_file():
        size = item.stat().st_size
        print(f"  📄 {item.name} ({size} bytes)")
    else:
        count = len(list(item.rglob("*.py")))
        print(f"  📁 {item.name}/ ({count} fichiers .py)")

print()

# Vérifications finales
app_exists = (Path(OUTPUT_DIR) / "app.py").exists()
src_exists = (Path(OUTPUT_DIR) / "src").exists()
bat_exists = (Path(OUTPUT_DIR) / "Lancer_Application.bat").exists()

print("=" * 70)
if app_exists and src_exists and bat_exists:
    print("  ✅ OBFUSCATION RÉUSSIE")
    print("=" * 70)
    print()
    print(f"📦 Package prêt dans: {OUTPUT_DIR}/")
    print()
    print("🧪 Pour tester:")
    print(f"  cd {OUTPUT_DIR}")
    print("  python app.py")
    print()
    print("📦 Pour créer le ZIP:")
    print(f"  Compress-Archive -Path {OUTPUT_DIR} -Destination Client.zip")
else:
    print("  ⚠️  PROBLÈME DÉTECTÉ")
    print("=" * 70)
    print()
    print("Fichiers manquants:")
    if not app_exists:
        print("  ❌ app.py")
    if not src_exists:
        print("  ❌ src/")
    if not bat_exists:
        print("  ❌ Lancer_Application.bat")
    print()
    print("Essayez la méthode manuelle (voir ci-dessous)")

print()
