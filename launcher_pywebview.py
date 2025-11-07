#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWebView Launcher for AliExpress Scraper
==========================================

This launcher creates a native desktop window for the Streamlit application.
It's a better alternative to PyInstaller for Streamlit apps.

Usage:
    python launcher_pywebview.py

Build to .exe:
    pyinstaller --onefile --windowed --name="AliExpress_Scraper" launcher_pywebview.py
"""

import webview
import subprocess
import sys
import time
import threading
import os
import socket
from pathlib import Path

# Configuration
APP_TITLE = "AliExpress Scraper"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
STREAMLIT_PORT = 8501

def is_port_in_use(port: int) -> bool:
    """Vérifier si un port est déjà utilisé"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int = 8501) -> int:
    """Trouver un port disponible"""
    port = start_port
    while is_port_in_use(port) and port < start_port + 100:
        port += 1
    return port

def get_streamlit_path():
    """Obtenir le chemin vers l'exécutable Streamlit"""
    # Quand compilé avec PyInstaller, sys.executable pointe vers l'exe
    # Sinon, on utilise le Python en cours d'exécution
    if getattr(sys, 'frozen', False):
        # Application compilée
        application_path = os.path.dirname(sys.executable)
    else:
        # Développement
        application_path = os.path.dirname(__file__)

    return application_path

def start_streamlit(port: int):
    """Démarrer le serveur Streamlit en arrière-plan"""

    # Obtenir le chemin du fichier app.py
    app_path = get_streamlit_path()
    app_file = os.path.join(app_path, "app.py")

    # Vérifier que app.py existe
    if not os.path.exists(app_file):
        print(f"❌ Erreur: app.py introuvable dans {app_path}")
        return None

    print(f"🚀 Démarrage de Streamlit sur le port {port}...")
    print(f"📁 Application: {app_file}")

    # Démarrer Streamlit
    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run",
                app_file,
                f"--server.port={port}",
                "--server.headless=true",
                "--browser.gatherUsageStats=false",
                "--server.address=localhost",
                "--global.developmentMode=false"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        print(f"✅ Streamlit démarré (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de Streamlit: {e}")
        return None

def wait_for_streamlit(port: int, timeout: int = 30) -> bool:
    """Attendre que Streamlit soit prêt"""
    print(f"⏳ Attente du démarrage de Streamlit (timeout: {timeout}s)...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            print(f"✅ Streamlit est prêt sur le port {port}")
            return True
        time.sleep(0.5)

    print(f"❌ Timeout: Streamlit n'a pas démarré dans les {timeout}s")
    return False

def create_window(port: int):
    """Créer la fenêtre native avec PyWebView"""

    url = f"http://localhost:{port}"
    print(f"🖼️  Création de la fenêtre: {url}")

    # Créer la fenêtre avec configuration étendue pour Streamlit
    window = webview.create_window(
        title=APP_TITLE,
        url=url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        background_color='#FFFFFF',
        text_select=True,
        # Activer JavaScript (nécessaire pour Streamlit)
        js_api=None,
        # Permettre l'accès aux ressources locales
        allow_downloads=True,
    )

    return window

def on_closing():
    """Callback appelé quand la fenêtre est fermée"""
    print("👋 Fermeture de l'application...")

def main():
    """Point d'entrée principal"""

    print("=" * 60)
    print(f"  {APP_TITLE}")
    print("=" * 60)
    print()

    # Trouver un port disponible
    port = find_available_port(STREAMLIT_PORT)
    if port != STREAMLIT_PORT:
        print(f"⚠️  Port {STREAMLIT_PORT} occupé, utilisation du port {port}")

    # Démarrer Streamlit dans un thread séparé
    streamlit_process = None

    def start_streamlit_thread():
        nonlocal streamlit_process
        streamlit_process = start_streamlit(port)

    threading.Thread(target=start_streamlit_thread, daemon=True).start()

    # Attendre que Streamlit soit prêt
    if not wait_for_streamlit(port, timeout=60):
        print("❌ Impossible de démarrer Streamlit")
        print("⚠️  Vérifiez que toutes les dépendances sont installées:")
        print("    pip install -r requirements.txt")
        input("\nAppuyez sur Entrée pour quitter...")
        return 1

    # Petite pause supplémentaire pour s'assurer que Streamlit est vraiment prêt
    time.sleep(2)

    # Créer la fenêtre
    try:
        print("🎨 Ouverture de l'interface...")
        create_window(port)

        # Démarrer PyWebView (bloquant jusqu'à fermeture de la fenêtre)
        # Mode debug activé pour voir les erreurs JavaScript de Streamlit
        webview.start(debug=True, http_server=False)

        print("✅ Fenêtre fermée")

    except Exception as e:
        print(f"❌ Erreur lors de la création de la fenêtre: {e}")
        return 1

    finally:
        # Tuer le processus Streamlit si il existe
        if streamlit_process and streamlit_process.poll() is None:
            print("🛑 Arrêt de Streamlit...")
            streamlit_process.terminate()
            try:
                streamlit_process.wait(timeout=5)
                print("✅ Streamlit arrêté proprement")
            except subprocess.TimeoutExpired:
                print("⚠️  Streamlit n'a pas répondu, arrêt forcé...")
                streamlit_process.kill()

    print()
    print("=" * 60)
    print("  Merci d'avoir utilisé AliExpress Scraper!")
    print("=" * 60)

    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Interruption utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
