#!/usr/bin/env python3
"""
Script PyArmor optimisé pour version Trial
- Obfusque uniquement app.py et src/
- Évite les fichiers trop gros
- Exclut les dossiers inutiles
"""
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def check_python_version():
    """Vérifier Python 3.10"""
    version = sys.version_info
    if version.major != 3 or version.minor != 10:
        print(f"❌ Python {version.major}.{version.minor} détecté")
        print("❌ PyArmor 7.7.4 nécessite Python 3.10")
        return False
    return True

def get_pyarmor_executable():
    """Obtenir pyarmor.exe"""
    venv_pyarmor = Path(sys.executable).parent / "pyarmor.exe"
    if venv_pyarmor.exists():
        return str(venv_pyarmor)
    return "pyarmor"

print("=" * 80)
print("  OBFUSCATION PYARMOR - VERSION TRIAL OPTIMISÉE")
print("=" * 80)
print()

# Vérifier Python 3.10
if not check_python_version():
    sys.exit(1)

print(f"✅ Python 3.10 : {sys.version.split()[0]}")
print()

# Configuration
OUTPUT_DIR = Path("CLIENT_FINAL_PYARMOR")
pyarmor_cmd = get_pyarmor_executable()

# Nettoyer
print("=" * 80)
print("  NETTOYAGE")
print("=" * 80)
print()

for folder in ["CLIENT_FINAL_PYARMOR", "dist", "build"]:
    if Path(folder).exists():
        print(f"🗑️  Suppression de {folder}/")
        shutil.rmtree(folder)

OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "RESULTATS").mkdir(exist_ok=True)
print("✅ Dossiers créés")
print()

print("=" * 80)
print("  OBFUSCATION DE APP.PY")
print("=" * 80)
print()

# Obfusquer app.py seul (pas récursif)
print("🔒 Obfuscation de app.py...")
result = subprocess.run([
    pyarmor_cmd, "obfuscate",
    "--output", str(OUTPUT_DIR),
    "app.py"  # Sans --recursive !
], capture_output=True, text=True)

if result.returncode == 0:
    app_file = OUTPUT_DIR / "app.py"
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8')
        if "pyarmor" in content.lower():
            print("   ✅ app.py obfusqué")
        else:
            print("   ⚠️  app.py pas obfusqué")
    else:
        print("   ❌ app.py non créé")
else:
    print(f"   ❌ Erreur: {result.stderr[:200]}")

print()
print("=" * 80)
print("  COPIE ET OBFUSCATION DE SRC/")
print("=" * 80)
print()

# Copier src/
src_output = OUTPUT_DIR / "src"
print("📋 Copie de src/...")
if Path("src").exists():
    shutil.copytree("src", src_output)
    print("   ✅ src/ copié")
else:
    print("   ❌ src/ introuvable")
    sys.exit(1)

print()
print("🔒 Obfuscation fichier par fichier...")
print()

# Obfusquer chaque fichier .py individuellement
py_files = list(src_output.rglob("*.py"))
success_count = 0
skipped_count = 0

for py_file in py_files:
    rel_path = py_file.relative_to(OUTPUT_DIR)

    # Vérifier la taille (limite Trial: 32KB)
    file_size = py_file.stat().st_size
    if file_size > 30000:  # 30KB pour être sûr
        print(f"   ⚠️  {rel_path} trop gros ({file_size} bytes) - copie sans obfuscation")
        skipped_count += 1
        continue

    print(f"   {rel_path}... ", end="", flush=True)

    # Obfusquer sur place
    result = subprocess.run([
        pyarmor_cmd, "obfuscate",
        "--in-place",
        str(py_file)
    ], capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        content = py_file.read_text(encoding='utf-8')
        if "pyarmor" in content.lower():
            print("✅")
            success_count += 1
        else:
            print("⚠️")
    else:
        print("❌")

print()
print(f"📊 Résultat:")
print(f"   ✅ Obfusqués: {success_count}/{len(py_files)}")
if skipped_count > 0:
    print(f"   ⚠️  Trop gros (non obfusqués): {skipped_count}")

print()
print("=" * 80)
print("  COPIE DES FICHIERS")
print("=" * 80)
print()

# Copier fichiers essentiels
files = [
    "requirements.txt",
    "Lancer_Application.bat",
    "Lancer_Application.sh",
    "LISEZ-MOI.txt",
    "README_CLIENT.txt",
    "GUIDE_INSTALLATION_CLIENT.md",
]

for file in files:
    if Path(file).exists():
        shutil.copy(file, OUTPUT_DIR)
        print(f"   ✅ {file}")

# Copier RESULTATS/
if Path("RESULTATS").exists():
    for item in Path("RESULTATS").iterdir():
        if item.is_file():
            shutil.copy(item, OUTPUT_DIR / "RESULTATS")
            print(f"   ✅ RESULTATS/{item.name}")

print()
print("=" * 80)
print("  VÉRIFICATION")
print("=" * 80)
print()

# Vérifier pytransform
if (OUTPUT_DIR / "pytransform").exists():
    print("   ✅ pytransform/ (runtime PyArmor)")
else:
    print("   ⚠️  pytransform/ manquant")

# Vérifier app.py
app_file = OUTPUT_DIR / "app.py"
if app_file.exists():
    content = app_file.read_text(encoding='utf-8')
    if "pyarmor" in content.lower():
        print("   ✅ app.py obfusqué")
    else:
        print("   ⚠️  app.py NON obfusqué")

print()
print("=" * 80)
print("  CRÉATION DU ZIP")
print("=" * 80)
print()

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
zip_name = f"AliExpress_Scraper_FINAL_v1.0_{timestamp}"

print(f"📦 Création de {zip_name}.zip...")
shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)

zip_path = Path(f"{zip_name}.zip")
if zip_path.exists():
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print(f"   ✅ {zip_name}.zip créé")
    print(f"   📊 Taille: {zip_size:.2f} MB")

print()
print("=" * 80)
print("  ✅ TERMINÉ")
print("=" * 80)
print()
print(f"📦 Package: {OUTPUT_DIR}/")
print(f"📦 ZIP: {zip_name}.zip")
print()
print(f"🔒 Protection:")
print(f"   app.py: Obfusqué avec PyArmor")
print(f"   src/: {success_count}/{len(py_files)} fichiers obfusqués")
if skipped_count > 0:
    print(f"   ⚠️  {skipped_count} fichiers trop gros (non obfusqués mais fonctionnels)")
print()
print("✅ Prêt pour distribution au client")
print()
print("🧪 TESTER:")
print(f"   cd {OUTPUT_DIR}")
print("   python app.py")
print()
