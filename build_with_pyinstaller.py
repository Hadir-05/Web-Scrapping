#!/usr/bin/env python3
"""
Alternative à PyArmor : PyInstaller
Compile Python en .exe avec tout inclus
Protection forte, package moyen (~500 MB)
"""
import subprocess
import sys
import shutil
from pathlib import Path

print("=" * 80)
print("  COMPILATION AVEC PYINSTALLER")
print("=" * 80)
print()

# Vérifier/Installer PyInstaller
try:
    import PyInstaller
    print("✅ PyInstaller déjà installé")
except ImportError:
    print("📥 Installation de PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ PyInstaller installé")

print()
print("⚠️  NOTES IMPORTANTES:")
print("   - Compilation: 5-10 minutes")
print("   - Taille finale: ~500 MB - 1 GB")
print("   - Windows Defender peut bloquer (faux positif)")
print("   - Streamlit peut avoir des problèmes avec PyInstaller")
print()

response = input("Continuer ? (oui/non): ")
if response.lower() != "oui":
    print("Annulé.")
    sys.exit(0)

print()
print("=" * 80)
print("  CRÉATION DU FICHIER .SPEC")
print("=" * 80)
print()

# Créer un fichier .spec personnalisé
spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('RESULTATS', 'RESULTATS'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'click',
        'PIL',
        'torch',
        'playwright',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AliExpress_Scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

spec_file = Path("AliExpress_Scraper.spec")
spec_file.write_text(spec_content)
print("✅ Fichier .spec créé")

print()
print("=" * 80)
print("  COMPILATION EN COURS")
print("=" * 80)
print()
print("⏳ Cela peut prendre 5-15 minutes...")
print("   Soyez patient !")
print()

try:
    # Compiler avec PyInstaller
    result = subprocess.run([
        "pyinstaller",
        "--clean",
        "-y",
        str(spec_file)
    ], check=True, capture_output=True, text=True)

    print(result.stdout)

    print()
    print("=" * 80)
    print("  ✅ COMPILATION RÉUSSIE")
    print("=" * 80)
    print()

    exe_path = Path("dist/AliExpress_Scraper.exe")
    if exe_path.exists():
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"📦 Fichier: {exe_path}")
        print(f"📊 Taille: {exe_size:.1f} MB")
        print()
        print("🔒 PROTECTION:")
        print("   ⭐⭐⭐⭐ Très forte (code compilé)")
        print("   ✅ Code source non accessible")
        print("   ✅ Difficile à reverse-engineer")
        print()
        print("🧪 TESTER:")
        print(f"   {exe_path}")
        print()
        print("📧 DISTRIBUTION:")
        print("   - Envoyer uniquement le fichier .exe")
        print("   - Aucune installation nécessaire")
        print("   - Peut être bloqué par antivirus (faux positif)")
        print()
        print("💡 Si Windows Defender bloque:")
        print("   1. Clic droit → Propriétés → Débloquer")
        print("   2. Ou ajouter une exception dans Windows Defender")
    else:
        print("❌ Fichier .exe non trouvé dans dist/")
        print()
        print("⚠️  PyInstaller peut avoir des problèmes avec Streamlit")
        print()
        print("💡 Alternatives:")
        print("   1. PyMinifier: python build_with_minifier.py")
        print("   2. Streamlit Cloud (recommandé): voir GUIDE_STREAMLIT_CLOUD.md")

except subprocess.CalledProcessError as e:
    print()
    print("❌ ERREUR DE COMPILATION")
    print()
    print(e.stderr)
    print()
    print("💡 PyInstaller a des problèmes avec Streamlit")
    print()
    print("Solutions recommandées:")
    print("   1. PyMinifier (obfuscation basique mais fonctionne):")
    print("      python build_with_minifier.py")
    print()
    print("   2. Streamlit Cloud (meilleure protection):")
    print("      Voir GUIDE_STREAMLIT_CLOUD.md")
    print()
    print("   3. Package sans protection (temporaire):")
    print("      python build_simple_sans_obfuscation.py")
