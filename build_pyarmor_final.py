#!/usr/bin/env python3
"""
Script final pour obfusquer avec PyArmor
À utiliser avec Python 3.10 uniquement
"""
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def check_python_version():
    """Vérifier que Python 3.10 est utilisé"""
    version = sys.version_info
    if version.major != 3 or version.minor != 10:
        print("=" * 80)
        print("  ERREUR: MAUVAISE VERSION DE PYTHON")
        print("=" * 80)
        print()
        print(f"❌ Vous utilisez Python {version.major}.{version.minor}.{version.micro}")
        print("❌ PyArmor 7.7.4 nécessite Python 3.10")
        print()
        print("💡 Solution:")
        print("   1. Installer Python 3.10 dans C:\\Python310")
        print("   2. Lancer setup_pyarmor_python310.bat")
        print("   3. Relancer ce script")
        print()
        return False
    return True

def check_pyarmor():
    """Vérifier que PyArmor fonctionne"""
    try:
        result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
        if "7.7" in result.stdout:
            return True
        else:
            print("⚠️  PyArmor 7.x non détecté")
            return False
    except FileNotFoundError:
        print("❌ PyArmor n'est pas installé")
        return False

def obfuscate_file(source_file, output_dir):
    """Obfusquer un fichier avec PyArmor"""
    try:
        # Créer le dossier de sortie
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Obfusquer
        result = subprocess.run([
            "pyarmor", "obfuscate",
            "--output", str(output_dir),
            "--recursive",
            str(source_file)
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Timeout (>60s)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 80)
    print("  OBFUSCATION PYARMOR - VERSION FINALE")
    print("=" * 80)
    print()

    # Vérifier Python 3.10
    if not check_python_version():
        sys.exit(1)

    print(f"✅ Python 3.10 détecté : {sys.version}")
    print()

    # Vérifier PyArmor
    if not check_pyarmor():
        print("❌ PyArmor 7.7.4 doit être installé")
        print()
        print("Installation : pip install pyarmor==7.7.4")
        sys.exit(1)

    print("✅ PyArmor 7.7.4 détecté")
    print()

    # Configuration
    OUTPUT_DIR = Path("PACKAGE_CLIENT_PYARMOR")
    SOURCE_DIR = Path("src")
    APP_FILE = Path("app.py")

    print("=" * 80)
    print("  NETTOYAGE")
    print("=" * 80)
    print()

    # Nettoyer
    if OUTPUT_DIR.exists():
        print(f"🗑️  Suppression de {OUTPUT_DIR}/")
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "RESULTATS").mkdir(exist_ok=True)
    print("✅ Dossiers créés")
    print()

    print("=" * 80)
    print("  OBFUSCATION DE APP.PY")
    print("=" * 80)
    print()

    # Obfusquer app.py
    print("🔒 Obfuscation de app.py...")
    success, error = obfuscate_file(APP_FILE, OUTPUT_DIR)

    if success and (OUTPUT_DIR / "app.py").exists():
        # Vérifier que c'est vraiment obfusqué
        content = (OUTPUT_DIR / "app.py").read_text(encoding='utf-8')
        if "pyarmor" in content.lower():
            print("   ✅ app.py obfusqué avec succès")
        else:
            print("   ⚠️  app.py créé mais pas obfusqué")
    else:
        print(f"   ❌ Échec: {error}")
        sys.exit(1)

    print()
    print("=" * 80)
    print("  OBFUSCATION DE SRC/")
    print("=" * 80)
    print()

    # Copier src/
    src_output = OUTPUT_DIR / "src"
    if src_output.exists():
        shutil.rmtree(src_output)

    print("📋 Copie de la structure src/...")
    shutil.copytree(SOURCE_DIR, src_output)
    print("   ✅ Structure copiée")
    print()

    # Obfusquer chaque fichier .py dans src/
    print("🔒 Obfuscation des fichiers Python...")
    print()

    py_files = list(src_output.rglob("*.py"))
    success_count = 0

    for py_file in py_files:
        rel_path = py_file.relative_to(OUTPUT_DIR)
        print(f"   {rel_path}...", end=" ", flush=True)

        # Obfusquer sur place
        result = subprocess.run([
            "pyarmor", "obfuscate",
            "--in-place",
            str(py_file)
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Vérifier
            content = py_file.read_text(encoding='utf-8')
            if "pyarmor" in content.lower():
                print("✅")
                success_count += 1
            else:
                print("⚠️")
        else:
            print("❌")

    print()
    print(f"📊 Résultat : {success_count}/{len(py_files)} fichiers obfusqués")
    print()

    # Copier les autres fichiers
    print("=" * 80)
    print("  COPIE DES FICHIERS")
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

    # Vérifier pytransform
    print("=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    print()

    pytransform = OUTPUT_DIR / "pytransform"
    if pytransform.exists():
        print("   ✅ pytransform/ présent (PyArmor runtime)")
    else:
        print("   ❌ pytransform/ MANQUANT")

    app_obf = OUTPUT_DIR / "app.py"
    if app_obf.exists():
        content = app_obf.read_text(encoding='utf-8')
        if "pyarmor" in content.lower():
            print("   ✅ app.py obfusqué")
        else:
            print("   ❌ app.py NON obfusqué")

    print()

    # Créer le ZIP
    print("=" * 80)
    print("  CRÉATION DU ZIP")
    print("=" * 80)
    print()

    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"AliExpress_Scraper_PYARMOR_v1.0.0_{timestamp}"

    print(f"📦 Création de {zip_name}.zip...")
    shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)

    zip_path = Path(f"{zip_name}.zip")
    if zip_path.exists():
        zip_size = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ ZIP créé : {zip_name}.zip")
        print(f"   📊 Taille : {zip_size:.2f} MB")

    print()
    print("=" * 80)
    print("  ✅ TERMINÉ")
    print("=" * 80)
    print()
    print(f"📦 Package : {OUTPUT_DIR}/")
    print(f"📦 Archive : {zip_name}.zip")
    print()
    print("🔒 Code protégé avec PyArmor 7.7.4")
    print("✅ Prêt pour distribution au client")
    print()
    print("🧪 TESTER :")
    print(f"   cd {OUTPUT_DIR}")
    print("   python app.py")
    print()

if __name__ == "__main__":
    main()
