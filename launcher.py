"""
Script de lancement optimisé pour l'exécutable
Lance Streamlit et ouvre automatiquement le navigateur
"""

import sys
import os
import subprocess
import webbrowser
import time
import socket
from pathlib import Path


def find_free_port():
    """Trouver un port libre"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def wait_for_server(port, timeout=30):
    """Attendre que le serveur Streamlit démarre"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                return True
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return False


def main():
    """Lancer l'application"""
    print("=" * 60)
    print("🚀 AliExpress Scraper - Lancement")
    print("=" * 60)
    print()

    # Trouver un port libre
    port = find_free_port()
    print(f"📡 Port utilisé: {port}")

    # URL de l'application
    url = f"http://localhost:{port}"

    print("⏳ Démarrage de l'application...")
    print("   (Cela peut prendre 10-30 secondes)")
    print()

    # Construire la commande Streamlit
    app_path = Path(__file__).parent / "app.py"

    if not app_path.exists():
        print("❌ Erreur: app.py non trouvé!")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)

    cmd = [
        sys.executable,  # Python de l'environnement
        "-m", "streamlit", "run",
        str(app_path),
        f"--server.port={port}",
        "--server.address=localhost",
        "--server.headless=true",  # Mode headless (pas d'ouverture auto du navigateur par Streamlit)
        "--browser.gatherUsageStats=false",  # Pas de stats
    ]

    try:
        # Lancer Streamlit en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Attendre que le serveur démarre
        print("⏳ Attente du serveur...")

        if wait_for_server(port):
            print("✅ Serveur démarré!")
            print()
            print(f"🌐 Ouverture du navigateur sur {url}")
            print()
            print("=" * 60)
            print("📌 IMPORTANT:")
            print("   - NE FERMEZ PAS cette fenêtre!")
            print("   - Pour arrêter l'application: fermez le navigateur puis cette fenêtre")
            print("   - Ou appuyez sur Ctrl+C dans cette fenêtre")
            print("=" * 60)
            print()

            # Ouvrir le navigateur
            time.sleep(1)  # Petit délai pour s'assurer que le serveur est prêt
            webbrowser.open(url)

            # Attendre que le processus se termine
            process.wait()

        else:
            print("❌ Erreur: Le serveur n'a pas pu démarrer!")
            print()
            print("💡 Essayez de:")
            print("   1. Vérifier qu'aucune autre application n'utilise le port")
            print("   2. Relancer l'application")
            print("   3. Redémarrer votre ordinateur")

            # Afficher les logs d'erreur
            stdout, stderr = process.communicate(timeout=5)
            if stderr:
                print()
                print("📋 Logs d'erreur:")
                print(stderr)

            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt de l'application...")
        process.terminate()
        process.wait()
        print("✅ Application arrêtée")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)


if __name__ == "__main__":
    main()
