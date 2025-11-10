#!/usr/bin/env python3
"""
Script amélioré pour créer une distribution client avec code protégé
Version 2 - avec meilleure gestion des erreurs et diagnostics
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def print_header(text):
    """Afficher un en-tête formaté"""
    print()
    print("=" * 80)
    print(f"  {text}")
    print("=" * 80)
    print()

def check_pyarmor():
    """Vérifier l'installation de PyArmor"""
    try:
        result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ PyArmor installé : {version}")

        if "8." in version or "9." in version:
            print()
            print("⚠️  ATTENTION : PyArmor 8.x/9.x détecté")
            print("   Ces versions ont des restrictions de licence")
            print()
            print("💡 Pour distribuer gratuitement, utilisez PyArmor 7.x:")
            print("   pip uninstall pyarmor -y")
            print("   pip install pyarmor==7.7.4")
            print()
            return False

        return True

    except FileNotFoundError:
        print("❌ PyArmor n'est pas installé")
        print()
        print("Installation : pip install pyarmor==7.7.4")
        return False

def obfuscate_file_pyarmor(file_path, output_dir=None):
    """Obfusquer un fichier avec PyArmor"""
    try:
        if output_dir:
            # Obfusquer vers un autre dossier
            cmd = [
                "pyarmor", "obfuscate",
                "--output", str(output_dir),
                "--no-cross-protection",
                str(file_path)
            ]
        else:
            # Obfusquer sur place
            cmd = [
                "pyarmor", "obfuscate",
                "--in-place",
                "--no-cross-protection",
                str(file_path)
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return True
        else:
            print(f"      ❌ Erreur: {result.stderr[:100]}")
            return False

    except Exception as e:
        print(f"      ❌ Exception: {str(e)[:100]}")
        return False

def verify_obfuscation(file_path):
    """Vérifier si un fichier est obfusqué"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Lire les 500 premiers caractères

        # Indicateurs d'obfuscation PyArmor
        indicators = [
            "from pytransform import pyarmor_runtime",
            "pyarmor_runtime()",
            "__pyarmor__",
            "from pyarmor_runtime"
        ]

        for indicator in indicators:
            if indicator in content:
                return True

        return False

    except Exception as e:
        print(f"      ⚠️  Impossible de vérifier: {e}")
        return False

def main():
    print_header("CRÉATION DU PACKAGE CLIENT - ALIEXPRESS SCRAPER V2")

    # Configuration
    VERSION = "1.0.0"
    OUTPUT_DIR = Path("PACKAGE_CLIENT")
    SOURCE_DIR = Path("src")
    APP_FILE = Path("app.py")

    FILES_TO_INCLUDE = [
        "requirements.txt",
        "Lancer_Application.bat",
        "Lancer_Application.sh",
        "LISEZ-MOI.txt",
        "GUIDE_INSTALLATION_CLIENT.md",
        "README_CLIENT.txt",
    ]

    print("🔍 Vérification de l'environnement...")
    print()

    # Vérifier PyArmor
    if not check_pyarmor():
        print()
        print("❌ Veuillez installer PyArmor 7.7.4 et relancer ce script")
        sys.exit(1)

    print_header("ÉTAPE 1 : PRÉPARATION")

    # Nettoyer
    if OUTPUT_DIR.exists():
        print(f"🗑️  Suppression de l'ancien {OUTPUT_DIR}/")
        shutil.rmtree(OUTPUT_DIR)

    # Créer la structure
    print(f"📁 Création de la structure...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "RESULTATS").mkdir(exist_ok=True)
    print("   ✅ Structure créée")

    print_header("ÉTAPE 2 : OBFUSCATION DE APP.PY")

    # Méthode 1: Obfusquer directement vers OUTPUT_DIR
    print("🔒 Tentative d'obfuscation de app.py (méthode 1)...")
    success = obfuscate_file_pyarmor(APP_FILE, OUTPUT_DIR)

    app_output = OUTPUT_DIR / "app.py"

    if not app_output.exists() or not success:
        print("   ⚠️  Méthode 1 échouée, tentative méthode 2...")

        # Méthode 2: Copier puis obfusquer sur place
        shutil.copy(APP_FILE, app_output)
        print("   📋 Fichier copié, obfuscation sur place...")
        success = obfuscate_file_pyarmor(app_output)

    # Vérifier le résultat
    if app_output.exists():
        is_obfuscated = verify_obfuscation(app_output)
        if is_obfuscated:
            print("   ✅ app.py obfusqué et vérifié")
        else:
            print("   ⚠️  app.py existe mais n'est PAS obfusqué")
            print("   ℹ️  Le code est lisible (obfuscation a échoué)")
    else:
        print("   ❌ app.py n'a pas été créé")
        print()
        print("❌ ERREUR CRITIQUE : Impossible de créer app.py")
        sys.exit(1)

    print_header("ÉTAPE 3 : OBFUSCATION DU DOSSIER SRC/")

    src_output = OUTPUT_DIR / "src"
    src_output.mkdir(exist_ok=True)

    # Copier toute la structure
    print("📋 Copie de la structure src/...")
    for item in SOURCE_DIR.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(SOURCE_DIR)
            dest_path = src_output / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)

    print("   ✅ Structure copiée")
    print()

    # Obfusquer tous les fichiers .py
    print("🔒 Obfuscation des fichiers Python...")
    print()

    py_files = list(src_output.rglob("*.py"))
    total_files = len(py_files)
    obfuscated_count = 0
    failed_count = 0

    for idx, py_file in enumerate(py_files, 1):
        rel_path = py_file.relative_to(OUTPUT_DIR)
        print(f"   [{idx}/{total_files}] {rel_path}... ", end="", flush=True)

        success = obfuscate_file_pyarmor(py_file)

        if success and verify_obfuscation(py_file):
            print("✅")
            obfuscated_count += 1
        else:
            print("❌ (conservé non-obfusqué)")
            failed_count += 1

    print()
    print(f"📊 Résultats obfuscation src/:")
    print(f"   ✅ Réussis: {obfuscated_count}/{total_files}")
    print(f"   ❌ Échoués: {failed_count}/{total_files}")

    if failed_count > 0:
        print()
        print("   ⚠️  ATTENTION : Certains fichiers ne sont PAS obfusqués")
        print("   ⚠️  Le code source est VISIBLE dans ces fichiers")

    print_header("ÉTAPE 4 : COPIE DES FICHIERS")

    # Copier les fichiers de config
    for file in FILES_TO_INCLUDE:
        if Path(file).exists():
            shutil.copy(file, OUTPUT_DIR)
            print(f"   ✅ {file}")

    # Copier le README du dossier RESULTATS
    resultats_src = Path("RESULTATS")
    resultats_dest = OUTPUT_DIR / "RESULTATS"

    if resultats_src.exists():
        for item in resultats_src.iterdir():
            if item.is_file():
                shutil.copy(item, resultats_dest)
                print(f"   ✅ RESULTATS/{item.name}")

    print_header("ÉTAPE 5 : VÉRIFICATION FINALE")

    # Vérifier les fichiers essentiels
    checks = {
        "app.py": OUTPUT_DIR / "app.py",
        "src/": OUTPUT_DIR / "src",
        "requirements.txt": OUTPUT_DIR / "requirements.txt",
        "RESULTATS/": OUTPUT_DIR / "RESULTATS",
        "pytransform/": OUTPUT_DIR / "pytransform",  # Dossier PyArmor
    }

    all_ok = True
    for name, path in checks.items():
        if path.exists():
            if name == "app.py":
                is_obf = verify_obfuscation(path)
                status = "🔒 obfusqué" if is_obf else "⚠️  lisible"
                print(f"   ✅ {name} ({status})")
            else:
                print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} MANQUANT")
            all_ok = False

    if not all_ok:
        print()
        print("⚠️  Le package est incomplet !")

    print_header("ÉTAPE 6 : CRÉATION DU ZIP")

    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"AliExpress_Scraper_v{VERSION}_{timestamp}"

    print(f"📦 Création de {zip_name}.zip...")

    try:
        shutil.make_archive(zip_name, 'zip', OUTPUT_DIR)
        zip_size = Path(f"{zip_name}.zip").stat().st_size / (1024 * 1024)
        print(f"   ✅ ZIP créé : {zip_name}.zip")
        print(f"   📊 Taille : {zip_size:.2f} MB")
    except Exception as e:
        print(f"   ❌ Erreur : {e}")

    print_header("RÉSUMÉ FINAL")

    print(f"📦 Package généré : {OUTPUT_DIR}/")
    print(f"📦 Archive : {zip_name}.zip")
    print()

    # Résumé de la protection
    app_protected = verify_obfuscation(OUTPUT_DIR / "app.py")
    protection_level = (obfuscated_count / total_files * 100) if total_files > 0 else 0

    print("🔒 NIVEAU DE PROTECTION :")
    print(f"   app.py : {'✅ PROTÉGÉ' if app_protected else '❌ NON PROTÉGÉ'}")
    print(f"   src/ : {protection_level:.1f}% protégé ({obfuscated_count}/{total_files} fichiers)")
    print()

    if not app_protected or protection_level < 100:
        print("⚠️  ATTENTION : LE CODE N'EST PAS COMPLÈTEMENT PROTÉGÉ")
        print()
        print("💡 Solutions possibles :")
        print("   1. Vérifier que PyArmor 7.7.4 est bien installé")
        print("   2. Essayer d'obfusquer manuellement (voir OBFUSCATION_MANUELLE.md)")
        print("   3. Utiliser PyInstaller pour compiler en .exe")
        print()
    else:
        print("✅ Code complètement protégé et prêt pour distribution")
        print()

    print("🧪 TESTER LE PACKAGE :")
    print(f"   cd {OUTPUT_DIR}")
    print("   python app.py")
    print()

if __name__ == "__main__":
    main()
