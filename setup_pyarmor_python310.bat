@echo off
REM ============================================================================
REM   SETUP PYARMOR AVEC PYTHON 3.10
REM ============================================================================

echo.
echo ================================================================================
echo   CONFIGURATION DE L'ENVIRONNEMENT PYARMOR
echo ================================================================================
echo.

REM Vérifier si Python 3.10 est installé
echo 1. Verification de Python 3.10...
echo.

if not exist "C:\Python310\python.exe" (
    echo ERREUR: Python 3.10 n'est pas installe dans C:\Python310\
    echo.
    echo Veuillez installer Python 3.10.11 depuis:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    echo IMPORTANT lors de l'installation:
    echo   1. Cocher "Add python.exe to PATH"
    echo   2. Cliquer sur "Customize installation"
    echo   3. Changer le chemin vers: C:\Python310
    echo.
    pause
    exit /b 1
)

echo    OK: Python 3.10 trouve
C:\Python310\python.exe --version
echo.

REM Créer un environnement virtuel
echo 2. Creation de l'environnement virtuel...
echo.

if exist "venv_py310" (
    echo    Suppression de l'ancien environnement...
    rmdir /s /q venv_py310
)

C:\Python310\python.exe -m venv venv_py310
echo    OK: Environnement cree
echo.

REM Activer l'environnement
echo 3. Activation de l'environnement...
call venv_py310\Scripts\activate.bat
echo    OK: Environnement active
echo.

REM Mettre à jour pip
echo 4. Mise a jour de pip...
python -m pip install --upgrade pip --quiet
echo    OK: pip mis a jour
echo.

REM Installer les dépendances
echo 5. Installation des dependances...
echo.

if exist "requirements.txt" (
    echo    Installation depuis requirements.txt...
    pip install -r requirements.txt --quiet
    echo    OK: Dependances installees
) else (
    echo    ATTENTION: requirements.txt non trouve
    echo    Installation des packages essentiels...
    pip install streamlit playwright httpx pillow torch open-clip-torch pandas openpyxl --quiet
)

echo.

REM Installer PyArmor 7.7.4
echo 6. Installation de PyArmor 7.7.4...
pip install pyarmor==7.7.4 --quiet
echo    OK: PyArmor 7.7.4 installe
echo.

REM Vérifier PyArmor
echo 7. Verification de PyArmor...
echo.
pyarmor --version
echo.

REM Test de PyArmor
echo 8. Test de PyArmor...
echo.

echo print('Test PyArmor OK') > test_pyarmor_check.py
pyarmor obfuscate test_pyarmor_check.py >nul 2>&1

if exist "dist\test_pyarmor_check.py" (
    echo    OK: PyArmor fonctionne correctement!
    del test_pyarmor_check.py
    rmdir /s /q dist
    echo.
    echo ================================================================================
    echo   SUCCES: ENVIRONNEMENT PRET
    echo ================================================================================
    echo.
    echo Vous pouvez maintenant utiliser PyArmor:
    echo.
    echo    python build_pyarmor_final.py
    echo.
    echo L'environnement Python 3.10 est active dans ce terminal.
    echo.
) else (
    echo    ERREUR: PyArmor ne fonctionne pas
    echo.
    echo Verifiez les messages d'erreur ci-dessus.
    del test_pyarmor_check.py
)

echo ================================================================================
echo.
