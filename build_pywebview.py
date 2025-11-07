#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for AliExpress Scraper (PyWebView)
===============================================

This script compiles the application into a standalone executable using PyInstaller.

Usage:
    python build_pywebview.py

The executable will be created in the dist/ folder.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "AliExpress_Scraper"
LAUNCHER_FILE = "launcher_pywebview.py"
ICON_FILE = "icon.ico"  # Si vous avez une icône

# Chemins
PROJECT_DIR = Path(__file__).parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
SPEC_FILE = PROJECT_DIR / f"{APP_NAME}.spec"

def print_header(text):
    """Afficher un header formaté"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step_num, text):
    """Afficher une étape"""
    print(f"\n🔹 Étape {step_num}: {text}")
    print("-" * 70)

def check_dependencies():
    """Vérifier que les dépendances nécessaires sont installées"""
    print_step(1, "Vérification des dépendances")

    required_packages = {
        'pyinstaller': 'PyInstaller',
        'pywebview': 'PyWebView',
        'streamlit': 'Streamlit'
    }

    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name} installé")
        except ImportError:
            print(f"  ❌ {name} manquant")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Packages manquants: {', '.join(missing)}")
        print("\n💡 Installation:")
        print(f"   pip install {' '.join(missing)}")
        return False

    print("\n✅ Toutes les dépendances sont installées")
    return True

def clean_previous_builds():
    """Nettoyer les builds précédents"""
    print_step(2, "Nettoyage des builds précédents")

    dirs_to_clean = [DIST_DIR, BUILD_DIR]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  🗑️  Suppression de {dir_path}")
            shutil.rmtree(dir_path)
            print(f"  ✅ {dir_path} supprimé")
        else:
            print(f"  ℹ️  {dir_path} n'existe pas (OK)")

    if SPEC_FILE.exists():
        print(f"  🗑️  Suppression de {SPEC_FILE}")
        SPEC_FILE.unlink()
        print(f"  ✅ {SPEC_FILE} supprimé")

    print("\n✅ Nettoyage terminé")

def create_pyinstaller_spec():
    """Créer le fichier .spec pour PyInstaller"""
    print_step(3, "Création du fichier .spec")

    # Détecter le séparateur de chemin pour l'OS
    separator = ';' if sys.platform == 'win32' else ':'

    # Vérifier si l'icône existe
    icon_path = PROJECT_DIR / ICON_FILE
    icon_line = f"icon='{icon_path}'," if icon_path.exists() else "# icon='icon.ico',"

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Données à inclure
added_files = [
    ('app.py', '.'),
    ('src', 'src'),
]

a = Analysis(
    ['{LAUNCHER_FILE}'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'pywebview',
        'crawlee',
        'playwright',
        'torch',
        'open_clip',
        'PIL',
        'pandas',
        'numpy',
        'requests',
        'altair',
        'pydantic',
        'pydantic_core',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console (application windowed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
"""

    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"  ✅ Fichier {SPEC_FILE} créé")
    return SPEC_FILE

def build_executable(spec_file):
    """Compiler l'exécutable avec PyInstaller"""
    print_step(4, "Compilation de l'exécutable")

    print("  ⏳ Compilation en cours (cela peut prendre 5-15 minutes)...\n")

    try:
        # Exécuter PyInstaller
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', str(spec_file), '--clean', '--noconfirm'],
            check=True,
            capture_output=False,
            text=True
        )

        print("\n  ✅ Compilation réussie!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Erreur lors de la compilation:")
        print(f"     {e}")
        return False

def verify_build():
    """Vérifier que le build a réussi"""
    print_step(5, "Vérification du build")

    exe_name = f"{APP_NAME}.exe" if sys.platform == 'win32' else APP_NAME
    exe_path = DIST_DIR / APP_NAME / exe_name

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Exécutable créé: {exe_path}")
        print(f"  📊 Taille: {size_mb:.1f} MB")

        # Lister les fichiers dans le dossier
        dist_folder = DIST_DIR / APP_NAME
        print(f"\n  📁 Contenu de {dist_folder}:")
        for item in sorted(dist_folder.iterdir()):
            if item.is_file():
                size = item.stat().st_size / (1024 * 1024)
                print(f"     - {item.name} ({size:.2f} MB)")
            else:
                print(f"     - {item.name}/ (dossier)")

        return True
    else:
        print(f"  ❌ Exécutable introuvable: {exe_path}")
        return False

def create_distribution_package():
    """Créer un package de distribution"""
    print_step(6, "Création du package de distribution")

    dist_folder = DIST_DIR / APP_NAME

    if not dist_folder.exists():
        print("  ❌ Dossier de distribution introuvable")
        return False

    # Créer un README pour la distribution
    readme_content = f"""# {APP_NAME}

## Installation

1. Extraire tous les fichiers de ce dossier
2. Double-cliquer sur {APP_NAME}.exe
3. L'application s'ouvre dans une fenêtre

## Utilisation

1. Entrer l'URL de recherche AliExpress
2. Uploader ou fournir l'URL de l'image de référence
3. Cliquer sur "Lancer la recherche"
4. Attendre les résultats
5. Exporter en CSV si besoin

## Dépannage

Si l'application ne démarre pas:
- Vérifier que Windows Defender n'a pas bloqué l'application
- Autoriser l'application dans le pare-feu si demandé
- Contacter le support technique

## Support

Pour toute question, contactez le support technique.

---

Version: 1.0.0
Date: {Path(__file__).stat().st_mtime}
"""

    readme_path = dist_folder / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"  ✅ README créé: {readme_path}")

    # Calculer la taille totale
    total_size = sum(f.stat().st_size for f in dist_folder.rglob('*') if f.is_file())
    total_size_mb = total_size / (1024 * 1024)

    print(f"\n  📦 Package de distribution prêt:")
    print(f"     Emplacement: {dist_folder}")
    print(f"     Taille totale: {total_size_mb:.1f} MB")
    print(f"\n  💡 Pour distribuer:")
    print(f"     1. Compresser le dossier {APP_NAME}")
    print(f"     2. Envoyer le fichier .zip au client")
    print(f"     3. Le client extrait et lance {APP_NAME}.exe")

    return True

def main():
    """Fonction principale"""

    print_header(f"Build {APP_NAME} - PyWebView Edition")

    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Installation des dépendances nécessaire")
        print("\n💡 Commande:")
        print("   pip install pyinstaller pywebview streamlit")
        return 1

    # Nettoyer les builds précédents
    clean_previous_builds()

    # Créer le fichier .spec
    spec_file = create_pyinstaller_spec()

    # Compiler
    if not build_executable(spec_file):
        print("\n❌ Échec de la compilation")
        return 1

    # Vérifier
    if not verify_build():
        print("\n❌ Vérification échouée")
        return 1

    # Créer le package
    create_distribution_package()

    # Succès!
    print_header("✅ BUILD RÉUSSI!")

    print(f"""
🎉 L'exécutable a été créé avec succès!

📁 Emplacement:
   {DIST_DIR / APP_NAME}

📤 Prochaines étapes:
   1. Tester l'exécutable: double-cliquer sur {APP_NAME}.exe
   2. Compresser le dossier {APP_NAME} en .zip
   3. Distribuer le .zip au client

⚠️  Important:
   - Le dossier complet doit être distribué (pas juste le .exe)
   - Le client doit extraire TOUS les fichiers
   - Windows Defender peut bloquer l'app au premier lancement (normal)

🎯 Le client doit:
   1. Extraire le .zip
   2. Double-cliquer sur {APP_NAME}.exe
   3. Autoriser dans Windows Defender si demandé
   4. Utiliser l'application normalement
""")

    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Build annulé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur lors du build: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
