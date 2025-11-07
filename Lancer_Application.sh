#!/bin/bash
# ====================================================================
#              ALIEXPRESS SCRAPER - LANCEUR AUTOMATIQUE
# ====================================================================
#
# Ce script démarre automatiquement l'application AliExpress Scraper
# et ouvre votre navigateur par défaut.
#
# Usage: ./Lancer_Application.sh
# ====================================================================

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "           ALIEXPRESS SCRAPER - DEMARRAGE"
echo "============================================================"
echo ""

# Vérifier que Python est installé
echo -e "${YELLOW}[1/4]${NC} Verification de Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Python 3 n'est pas installe"
    echo ""
    echo "Veuillez installer Python 3.10 ou superieur :"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - macOS: brew install python3"
    echo ""
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Python est installe"
python3 --version

# Vérifier que Streamlit est installé
echo ""
echo -e "${YELLOW}[2/4]${NC} Verification de Streamlit..."
if ! python3 -m streamlit --version &> /dev/null; then
    echo -e "${YELLOW}[ATTENTION]${NC} Streamlit n'est pas installe"
    echo "Installation automatique en cours..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERREUR]${NC} Impossible d'installer les dependances"
        echo "Veuillez executer manuellement : pip3 install -r requirements.txt"
        echo ""
        exit 1
    fi
fi
echo -e "${GREEN}[OK]${NC} Streamlit est installe"

# Vérifier que Playwright est installé
echo ""
echo -e "${YELLOW}[3/4]${NC} Verification de Playwright..."
if ! python3 -c "from playwright.sync_api import sync_playwright" &> /dev/null; then
    echo -e "${YELLOW}[ATTENTION]${NC} Playwright n'est pas configure"
    echo "Installation automatique en cours..."
    echo ""
    pip3 install playwright
    playwright install chromium
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERREUR]${NC} Impossible d'installer Playwright"
        echo ""
        exit 1
    fi
fi
echo -e "${GREEN}[OK]${NC} Playwright est configure"

# Démarrer Streamlit
echo ""
echo -e "${YELLOW}[4/4]${NC} Demarrage de l'application..."
echo ""
echo "============================================================"
echo ""
echo "L'application va s'ouvrir dans votre navigateur par defaut"
echo "dans quelques secondes..."
echo ""
echo "IMPORTANT :"
echo "- Ne fermez PAS ce terminal tant que vous utilisez l'app"
echo "- Pour arreter l'application, faites Ctrl+C dans ce terminal"
echo "- L'application sera accessible sur : http://localhost:8501"
echo ""
echo "============================================================"
echo ""

# Fonction pour ouvrir le navigateur selon l'OS
open_browser() {
    sleep 3
    if command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:8501
    elif command -v open &> /dev/null; then
        # macOS
        open http://localhost:8501
    else
        echo "Ouvrez manuellement : http://localhost:8501"
    fi
}

# Ouvrir le navigateur en arrière-plan
open_browser &

# Lancer Streamlit
python3 -m streamlit run app.py --server.port=8501 --server.headless=true

# Si Streamlit s'arrête
echo ""
echo ""
echo "============================================================"
echo "           APPLICATION ARRETEE"
echo "============================================================"
echo ""
echo "L'application a ete fermee."
echo ""
