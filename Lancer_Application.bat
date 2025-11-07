@echo off
chcp 65001 >nul
:: ====================================================================
::              ALIEXPRESS SCRAPER - LANCEUR AUTOMATIQUE
:: ====================================================================
::
:: Ce script démarre automatiquement l'application AliExpress Scraper
:: et ouvre votre navigateur par défaut.
::
:: Double-cliquez simplement sur ce fichier pour démarrer l'application.
:: ====================================================================

title AliExpress Scraper - Démarrage
color 0A

echo.
echo ============================================================
echo           ALIEXPRESS SCRAPER - DEMARRAGE
echo ============================================================
echo.

:: Vérifier que Python est installé
echo [1/4] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.10 ou superieur depuis :
    echo https://www.python.org/downloads/
    echo.
    echo Assurez-vous de cocher "Add Python to PATH" pendant l'installation
    echo.
    pause
    exit /b 1
)
echo [OK] Python est installe
python --version

:: Vérifier que Streamlit est installé
echo.
echo [2/4] Verification de Streamlit...
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo.
    echo [ATTENTION] Streamlit n'est pas installe
    echo Installation automatique en cours...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo.
        echo [ERREUR] Impossible d'installer les dependances
        echo Veuillez executer manuellement : pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)
echo [OK] Streamlit est installe

:: Vérifier que Playwright est installé
echo.
echo [3/4] Verification de Playwright...
python -c "from playwright.sync_api import sync_playwright" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo.
    echo [ATTENTION] Playwright n'est pas configure
    echo Installation automatique en cours...
    echo.
    pip install playwright
    playwright install chromium
    if errorlevel 1 (
        color 0C
        echo.
        echo [ERREUR] Impossible d'installer Playwright
        echo.
        pause
        exit /b 1
    )
)
echo [OK] Playwright est configure

:: Démarrer Streamlit
echo.
echo [4/4] Demarrage de l'application...
echo.
echo ============================================================
echo.
echo L'application va s'ouvrir dans votre navigateur par defaut
echo dans quelques secondes...
echo.
echo IMPORTANT :
echo - Ne fermez PAS cette fenetre tant que vous utilisez l'app
echo - Pour arreter l'application, fermez cette fenetre
echo - L'application sera accessible sur : http://localhost:8501
echo.
echo ============================================================
echo.

:: Attendre 3 secondes puis ouvrir le navigateur
start "" timeout /t 3 /nobreak >nul && start http://localhost:8501

:: Lancer Streamlit (bloquant - garde la fenêtre ouverte)
python -m streamlit run app.py --server.port=8501 --server.headless=true

:: Si Streamlit s'arrête, afficher un message
echo.
echo.
echo ============================================================
echo           APPLICATION ARRETEE
echo ============================================================
echo.
echo L'application a ete fermee.
echo.
pause
