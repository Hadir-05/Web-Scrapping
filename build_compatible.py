#!/usr/bin/env python3
"""
PyArmor avec exclusions pour les fichiers problématiques
N'obfusque que les fichiers critiques, laisse le reste en clair
"""
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def get_pyarmor_executable():
    venv_pyarmor = Path(sys.executable).parent / "pyarmor.exe"
    if venv_pyarmor.exists():
        return str(venv_pyarmor)
    return "pyarmor"

print("=" * 80)
print("  PYARMOR AVEC EXCLUSIONS (Compatible Streamlit)")
print("=" * 80)
print()

OUTPUT_DIR = Path("CLIENT_FINAL_COMPATIBLE")
pyarmor_cmd = get_pyarmor_executable()

# Nettoyer
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "RESULTATS").mkdir(exist_ok=True)

print("=" * 80)
print("  COPIE COMPLÈTE (sans obfuscation)")
print("=" * 80)
print()

# Copier TOUT d'abord
print("📋 Copie de app.py...")
shutil.copy("app.py", OUTPUT_DIR)

print("📋 Copie de src/...")
shutil.copytree("src", OUTPUT_DIR / "src")

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

print()
print("=" * 80)
print("  OBFUSCATION SÉLECTIVE (fichiers non-critiques uniquement)")
print("=" * 80)
print()

# Liste des fichiers à obfusquer (seulement ceux sans dépendances natives)
files_to_obfuscate = [
    OUTPUT_DIR / "src" / "models" / "data_models.py",
    OUTPUT_DIR / "src" / "utils.py",
]

success_count = 0
for py_file in files_to_obfuscate:
    if py_file.exists() and py_file.stat().st_size < 30000:
        print(f"🔒 {py_file.name}... ", end="", flush=True)

        result = subprocess.run([
            pyarmor_cmd, "obfuscate",
            "--in-place",
            str(py_file)
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅")
            success_count += 1
        else:
            print("⚠️")

print()
print(f"📊 {success_count} fichiers obfusqués")
print()

print("⚠️  ATTENTION:")
print("   Les fichiers critiques (scraper, image_search) restent en CLAIR")
print("   pour éviter les conflits avec torch/CLIP/Streamlit")
print()

# ZIP
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
zip_name = f"AliExpress_Scraper_COMPATIBLE_v1.0_{timestamp}"

print("📦 Création du ZIP...")
shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)

print()
print("=" * 80)
print("  ✅ TERMINÉ")
print("=" * 80)
print()
print(f"📦 Package: {OUTPUT_DIR}/")
print(f"📦 ZIP: {zip_name}.zip")
print()
print("🔒 Protection: PARTIELLE")
print("   - Fichiers de données: Obfusqués")
print("   - Fichiers critiques: En clair (nécessaire pour compatibilité)")
print()
print("🧪 TESTER:")
print(f"   cd {OUTPUT_DIR}")
print("   streamlit run app.py")
print()
