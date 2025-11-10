#!/usr/bin/env python3
"""
Compiler l'application en .exe avec PyInstaller
Version simplifiée qui ne nécessite pas PyWebView
"""
import os
import sys
import shutil
from pathlib import Path

print("=" * 70)
print("  COMPILATION EN EXECUTABLE (.exe)")
print("=" * 70)
print()

# Vérifier PyInstaller
try:
    import PyInstaller
    print("✅ PyInstaller est installé")
except ImportError:
    print("❌ PyInstaller n'est pas installé")
    print("Installation : pip install pyinstaller")
    exit(1)

# Nettoyer
for dir in ["build", "dist", "distribution_exe"]:
    if Path(dir).exists():
        print(f"🗑️  Suppression de {dir}")
        shutil.rmtree(dir)

print()
print("🔧 Création du fichier .spec...")

# Créer le fichier spec
spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Fichiers de données à inclure
added_files = []

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'crawlee',
        'playwright',
        'torch',
        'open_clip',
        'PIL',
        'pandas',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'IPython', 'jupyter', 'pytest', 'tkinter'],
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
    name='AliExpress_Scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console visible pour voir les logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AliExpress_Scraper',
)
"""

with open("app_build.spec", "w") as f:
    f.write(spec_content)

print("✅ Fichier .spec créé")
print()
print("🔨 Compilation en cours (5-15 minutes)...")
print()

# Compiler
os.system(f"{sys.executable} -m PyInstaller app_build.spec --clean --noconfirm")

print()
print("=" * 70)

# Vérifier le résultat
exe_path = Path("dist/AliExpress_Scraper/AliExpress_Scraper.exe")
if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print("  ✅ COMPILATION RÉUSSIE")
    print("=" * 70)
    print()
    print(f"📁 Dossier : dist/AliExpress_Scraper/")
    print(f"⭐ Exe : AliExpress_Scraper.exe ({size_mb:.1f} MB)")
    print()
    print("📋 Instructions pour le client :")
    print("  1. Copier TOUT le dossier dist/AliExpress_Scraper/")
    print("  2. Double-cliquer sur AliExpress_Scraper.exe")
    print("  3. Attendre le démarrage de Streamlit")
    print("  4. Ouvrir http://localhost:8501 dans le navigateur")
    print()
else:
    print("  ❌ COMPILATION ÉCHOUÉE")
    print("=" * 70)
    print()
    print("Vérifiez les erreurs ci-dessus")
    print()
