#!/usr/bin/env python3
"""
Alternative à PyArmor : Obfuscation avec PyMinifier
Protection basique mais mieux que rien
"""
import python_minifier
import shutil
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("  OBFUSCATION AVEC PYMINIFIER (Alternative à PyArmor)")
print("=" * 80)
print()
print("⚠️  Note : Protection basique (moins forte que PyArmor)")
print("   Mais mieux que du code source visible")
print()

# Installer pyminifier si nécessaire
try:
    import python_minifier
except ImportError:
    print("📥 Installation de python-minifier...")
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "install", "python-minifier"])
    import python_minifier

# Configuration
OUTPUT_DIR = Path("PACKAGE_CLIENT_MINIFIED")
SOURCE_DIR = Path("src")
APP_FILE = Path("app.py")

print("=" * 80)
print("  PRÉPARATION")
print("=" * 80)
print()

# Nettoyer
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "RESULTATS").mkdir(exist_ok=True)

print("✅ Dossiers créés")
print()

print("=" * 80)
print("  OBFUSCATION DES FICHIERS")
print("=" * 80)
print()

def minify_file(source_file, dest_file):
    """Minifier/obfusquer un fichier Python"""
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Minifier avec obfuscation
        minified = python_minifier.minify(
            source_code,
            rename_locals=True,        # Renommer variables locales
            rename_globals=False,      # Garder les globals (imports, etc.)
            remove_annotations=True,   # Supprimer annotations
            remove_pass=True,          # Supprimer pass
            remove_literal_statements=True,
            combine_imports=True,
            hoist_literals=True,
            convert_posargs_to_args=False,
        )

        # Écrire le fichier minifié
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(minified)

        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        # En cas d'erreur, copier le fichier original
        shutil.copy2(source_file, dest_file)
        return False

# Minifier app.py
print("🔒 Obfuscation de app.py...")
if minify_file(APP_FILE, OUTPUT_DIR / "app.py"):
    print("   ✅ app.py obfusqué")
else:
    print("   ⚠️  app.py copié sans obfuscation")

print()

# Minifier src/
print("🔒 Obfuscation du dossier src/...")
print()

src_output = OUTPUT_DIR / "src"
src_output.mkdir(exist_ok=True)

success_count = 0
fail_count = 0

for py_file in SOURCE_DIR.rglob("*.py"):
    rel_path = py_file.relative_to(SOURCE_DIR)
    dest_file = src_output / rel_path

    print(f"   {rel_path}... ", end="", flush=True)

    if minify_file(py_file, dest_file):
        print("✅")
        success_count += 1
    else:
        print("⚠️")
        fail_count += 1

print()
print(f"📊 Résultat: {success_count} réussis, {fail_count} échoués")
print()

# Copier les autres fichiers
print("=" * 80)
print("  COPIE DES FICHIERS NÉCESSAIRES")
print("=" * 80)
print()

files_to_copy = [
    "requirements.txt",
    "Lancer_Application.bat",
    "Lancer_Application.sh",
    "LISEZ-MOI.txt",
    "README_CLIENT.txt",
    "GUIDE_INSTALLATION_CLIENT.md",
]

for file in files_to_copy:
    if Path(file).exists():
        shutil.copy(file, OUTPUT_DIR)
        print(f"   ✅ {file}")

# Copier RESULTATS/
resultats = Path("RESULTATS")
if resultats.exists():
    for item in resultats.iterdir():
        if item.is_file():
            shutil.copy(item, OUTPUT_DIR / "RESULTATS")
            print(f"   ✅ RESULTATS/{item.name}")

print()

# Créer le ZIP
print("=" * 80)
print("  CRÉATION DU ZIP")
print("=" * 80)
print()

timestamp = datetime.now().strftime("%Y%m%d")
zip_name = f"AliExpress_Scraper_MINIFIED_v1.0.0_{timestamp}"

print(f"📦 Création de {zip_name}.zip...")

shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)
zip_size = Path(f"{zip_name}.zip").stat().st_size / (1024 * 1024)

print(f"   ✅ ZIP créé: {zip_name}.zip")
print(f"   📊 Taille: {zip_size:.2f} MB")

print()
print("=" * 80)
print("  ✅ TERMINÉ")
print("=" * 80)
print()
print(f"📦 Package: {OUTPUT_DIR}/")
print(f"📦 Archive: {zip_name}.zip")
print()
print("🔒 NIVEAU DE PROTECTION:")
print("   ⭐⭐ Basique (code minifié et renommé)")
print("   ⚠️  Moins fort que PyArmor mais mieux que rien")
print()
print("💡 Le code est:")
print("   ✅ Difficile à lire (noms de variables obscurcis)")
print("   ✅ Compressé sur une seule ligne")
print("   ⚠️  Peut être déobfusqué par un expert")
print()
print("🧪 TESTER:")
print(f"   cd {OUTPUT_DIR}")
print("   python app.py")
print()
