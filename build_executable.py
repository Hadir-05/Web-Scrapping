"""
Script pour créer un exécutable distributable de l'application AliExpress Scraper
Utilise PyInstaller pour compiler en .exe (Windows) / .app (Mac) / binaire (Linux)
"""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_executable():
    """
    Créer l'exécutable avec toutes les dépendances
    """

    app_name = "AliExpress_Scraper"

    # Déterminer l'OS
    if sys.platform == "win32":
        platform = "Windows"
        separator = ";"
    elif sys.platform == "darwin":
        platform = "macOS"
        separator = ":"
    else:
        platform = "Linux"
        separator = ":"

    print(f"🔨 Construction de l'exécutable pour {platform}...")
    print(f"⚠️  Attention: Le fichier final sera volumineux (~1-2GB) à cause de PyTorch et Playwright")
    print()

    # Configuration PyInstaller
    pyinstaller_args = [
        'app.py',  # Point d'entrée
        f'--name={app_name}',  # Nom de l'exécutable

        # Mode de packaging
        '--onedir',  # Un dossier avec dépendances (plus rapide, recommandé)
        # '--onefile',  # Décommenter pour UN SEUL fichier (plus lent, 10+ min de démarrage)

        # Interface
        '--windowed',  # Pas de console (décommenter si vous voulez voir les logs)
        # '--console',  # Décommenter pour voir les logs dans une console

        # Inclure le code source (dossier src)
        '--add-data=src' + separator + 'src',

        # Hidden imports critiques pour Streamlit
        '--hidden-import=streamlit',
        '--hidden-import=streamlit.runtime',
        '--hidden-import=streamlit.runtime.scriptrunner',
        '--hidden-import=streamlit.web.cli',
        '--hidden-import=streamlit.web.bootstrap',
        '--hidden-import=validators',
        '--hidden-import=watchdog',
        '--hidden-import=packaging',
        '--hidden-import=packaging.version',
        '--hidden-import=packaging.specifiers',
        '--hidden-import=packaging.requirements',

        # Hidden imports pour Crawlee
        '--hidden-import=crawlee',
        '--hidden-import=crawlee.playwright_crawler',
        '--hidden-import=crawlee.storages',
        '--hidden-import=crawlee.sessions',
        '--hidden-import=crawlee.fingerprint_suite',
        '--hidden-import=playwright',
        '--hidden-import=playwright.async_api',

        # Hidden imports pour CLIP et PyTorch
        '--hidden-import=torch',
        '--hidden-import=torchvision',
        '--hidden-import=open_clip',
        '--hidden-import=PIL',
        '--hidden-import=PIL._imaging',

        # Hidden imports pour les modèles de données
        '--hidden-import=pydantic',
        '--hidden-import=pydantic.dataclasses',

        # Collecter tous les fichiers de ces packages
        '--collect-all=streamlit',
        '--collect-all=altair',
        '--collect-all=plotly',

        # Exclure des packages inutiles pour réduire la taille
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        '--exclude-module=notebook',

        # Options supplémentaires
        '--noconfirm',  # Écraser sans demander
        '--clean',  # Nettoyer avant de builder

        # Optimisation
        '--strip',  # Strip binaries (Linux/Mac)
    ]

    # Ajouter un icon si disponible
    icon_path = Path("icon.ico")  # Windows
    if not icon_path.exists():
        icon_path = Path("icon.icns")  # Mac

    if icon_path.exists():
        pyinstaller_args.append(f'--icon={icon_path}')
        print(f"✅ Icon trouvé: {icon_path}")

    print("\n🚀 Lancement de PyInstaller...")
    print("   Cela peut prendre 10-30 minutes selon votre machine...")
    print()

    try:
        PyInstaller.__main__.run(pyinstaller_args)

        print("\n" + "="*80)
        print("✅ SUCCÈS! L'exécutable a été créé!")
        print("="*80)
        print()
        print("📁 Dossier de sortie:")

        if '--onedir' in pyinstaller_args:
            print(f"   dist/{app_name}/")
            print(f"   └── {app_name}.exe  (ou .app sur Mac)")
            print()
            print("📦 Pour distribuer:")
            print(f"   1. Compressez TOUT le dossier dist/{app_name}/ en ZIP")
            print(f"   2. Donnez le fichier {app_name}.zip au client")
            print(f"   3. Le client décompresse et double-clique sur {app_name}.exe")
        else:
            print(f"   dist/{app_name}.exe  (ou .app sur Mac)")
            print()
            print("📦 Pour distribuer:")
            print(f"   1. Donnez le fichier dist/{app_name}.exe au client")
            print(f"   2. Le client double-clique pour lancer")
            print()
            print("   ⚠️ ATTENTION: Avec --onefile, le démarrage peut prendre 5-10 minutes!")
            print("      À chaque lancement, l'exe doit décompresser toutes les dépendances.")

        print()
        print("🔒 Sécurité:")
        print("   ✅ Le code source est compilé et non lisible")
        print("   ✅ Les fichiers .py ne sont pas accessibles")
        print("   ⚠️  Mais un expert PEUT décompiler avec effort")
        print()
        print("💡 Conseil: Testez l'exécutable sur une machine propre (sans Python)")

    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERREUR lors de la compilation!")
        print("="*80)
        print(f"Erreur: {e}")
        print()
        print("💡 Solutions possibles:")
        print("   1. Assurez-vous que toutes les dépendances sont installées:")
        print("      pip install -r requirements.txt")
        print("   2. Installez PyInstaller:")
        print("      pip install pyinstaller")
        print("   3. Essayez avec --console au lieu de --windowed pour voir les logs")
        print("   4. Vérifiez qu'il n'y a pas d'erreurs dans app.py")
        sys.exit(1)


if __name__ == "__main__":
    print("="*80)
    print("🏗️  BUILD EXECUTABLE - AliExpress Scraper")
    print("="*80)
    print()

    # Vérifications préalables
    if not Path("app.py").exists():
        print("❌ Erreur: app.py non trouvé!")
        print("   Lancez ce script depuis le dossier racine du projet")
        sys.exit(1)

    if not Path("src").exists():
        print("❌ Erreur: Dossier src/ non trouvé!")
        print("   Assurez-vous que la structure du projet est intacte")
        sys.exit(1)

    # Demander confirmation
    print("⚠️  AVERTISSEMENT:")
    print("   - La compilation peut prendre 10-30 minutes")
    print("   - Le fichier final sera ~1-2GB (à cause de PyTorch)")
    print("   - Votre disque doit avoir au moins 5GB d'espace libre")
    print()

    response = input("Continuer? (oui/non): ").strip().lower()

    if response in ['oui', 'o', 'yes', 'y']:
        build_executable()
    else:
        print("\n❌ Compilation annulée")
        sys.exit(0)
