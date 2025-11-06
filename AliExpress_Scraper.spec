# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de configuration PyInstaller pour AliExpress Scraper
Plus de contrôle que le script Python simple
"""

import sys
from pathlib import Path

# Nom de l'application
APP_NAME = 'AliExpress_Scraper'

# Dossier source
SRC_DIR = 'src'

# Déterminer le séparateur de chemin selon l'OS
if sys.platform == 'win32':
    SEP = ';'
else:
    SEP = ':'

# Liste des fichiers de données à inclure
datas = [
    (SRC_DIR, SRC_DIR),  # Dossier src complet
]

# Hidden imports (modules cachés à inclure)
hiddenimports = [
    # Streamlit
    'streamlit',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'streamlit.runtime.legacy_caching',
    'streamlit.runtime.caching',
    'validators',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',

    # Packaging
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',

    # Crawlee & Playwright
    'crawlee',
    'crawlee.playwright_crawler',
    'crawlee.storages',
    'crawlee.sessions',
    'crawlee.fingerprint_suite',
    'playwright',
    'playwright.async_api',
    'playwright._impl',

    # PyTorch & CLIP
    'torch',
    'torch._C',
    'torchvision',
    'open_clip',
    'open_clip.model',
    'open_clip.transform',

    # PIL
    'PIL',
    'PIL._imaging',
    'PIL.Image',

    # Pydantic
    'pydantic',
    'pydantic.dataclasses',

    # JSON
    'json',
    'pathlib',
]

# Analyse du script principal
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure des packages inutiles pour réduire la taille
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # Chiffrement optionnel
    noarchive=False,
)

# Créer le PYZ (archive Python)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

# OPTION 1: --onedir (Recommandé - Plus rapide)
# Crée un dossier avec l'exe et toutes les dépendances
exe = EXE(
    pyz,
    a.scripts,
    [],  # Ne pas inclure dans l'exe (sera dans le dossier)
    exclude_binaries=True,  # Binaires séparés
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols (Linux/Mac)
    upx=True,  # Compresser avec UPX (si disponible)
    console=False,  # Pas de console (interface graphique uniquement)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Décommenter si vous avez un icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# OPTION 2: --onefile (Un seul fichier)
# Décommenter cette section et commenter OPTION 1 ci-dessus pour un seul fichier
# ATTENTION: Démarrage très lent (5-10 minutes) car décompression à chaque lancement

# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,  # Inclure dans l'exe
#     a.zipfiles,
#     a.datas,
#     [],
#     name=APP_NAME,
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=True,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=False,  # Pas de console
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     # icon='icon.ico',  # Décommenter si vous avez un icon
# )
