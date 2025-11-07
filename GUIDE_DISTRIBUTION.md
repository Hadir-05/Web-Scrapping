# 📦 Guide de Distribution - AliExpress Scraper

## 🎯 Objectif

Créer un package simple à distribuer au client, qui n'aura qu'à :
1. Extraire un dossier
2. Double-cliquer sur un fichier
3. Utiliser l'application

---

## 📋 Ce Que le Client Recevra

Un fichier ZIP contenant :
```
AliExpress_Scraper/
├── Lancer_Application.bat        ⭐ Double-clic pour lancer (Windows)
├── Lancer_Application.sh          ⭐ Pour macOS/Linux
├── LISEZ-MOI.txt                  📄 Guide rapide (3 étapes)
├── GUIDE_INSTALLATION_CLIENT.md   📖 Guide complet
├── app.py                         🐍 Application principale
├── requirements.txt               📦 Dépendances Python
├── src/                           📁 Code source
│   ├── aliexpress_scraper.py
│   ├── image_search/
│   └── ...
└── README_CLIENT.txt              📄 Documentation utilisateur
```

---

## 🚀 Étapes de Distribution

### Méthode 1 : ZIP Simple (Recommandée)

#### Étape 1 : Préparer le Dossier

```bash
# 1. Aller dans votre projet
cd Web-Scrapping

# 2. Nettoyer les fichiers inutiles
rm -rf __pycache__ .pytest_cache .mypy_cache
rm -rf output_recherche* storage
rm -rf .git build dist *.egg-info
rm -rf node_modules venv env

# 3. Vérifier que les fichiers essentiels sont présents
ls -la
```

**Fichiers essentiels à garder :**
- ✅ `Lancer_Application.bat`
- ✅ `Lancer_Application.sh`
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `src/` (dossier complet)
- ✅ `LISEZ-MOI.txt`
- ✅ `GUIDE_INSTALLATION_CLIENT.md`
- ✅ `README_CLIENT.txt`

**Fichiers à SUPPRIMER avant distribution :**
- ❌ `.git/` (historique Git)
- ❌ `__pycache__/` (cache Python)
- ❌ `output_recherche*/` (résultats de vos tests)
- ❌ `storage/` (cache Crawlee)
- ❌ `venv/`, `env/` (environnements virtuels)
- ❌ `.env` (secrets)
- ❌ Fichiers de développement (`.spec`, `build/`, `dist/`)

#### Étape 2 : Créer le ZIP

**Windows (PowerShell) :**
```powershell
# Aller dans le dossier parent
cd ..

# Créer le ZIP
Compress-Archive -Path "Web-Scrapping" -DestinationPath "AliExpress_Scraper_v1.0.zip" -Force

# Le fichier AliExpress_Scraper_v1.0.zip est créé
```

**macOS / Linux :**
```bash
# Aller dans le dossier parent
cd ..

# Créer le ZIP
zip -r AliExpress_Scraper_v1.0.zip Web-Scrapping/ \
  -x "*.git*" \
  -x "*__pycache__*" \
  -x "*output_recherche*" \
  -x "*.pyc" \
  -x "*venv*" \
  -x "*.env"

# Le fichier AliExpress_Scraper_v1.0.zip est créé
```

#### Étape 3 : Vérifier le ZIP

1. Extraire le ZIP dans un dossier temporaire
2. Vérifier que tous les fichiers sont présents
3. Tester le lancement :
   - Windows : Double-clic sur `Lancer_Application.bat`
   - macOS/Linux : `./Lancer_Application.sh`
4. Vérifier qu'une recherche fonctionne

#### Étape 4 : Distribuer

**Option A : Email**
```
Objet : Application AliExpress Scraper - Livraison

Bonjour [Nom du client],

Veuillez trouver ci-joint l'application AliExpress Scraper.

📥 INSTALLATION RAPIDE (3 étapes) :

1. Vérifier que Python 3.10+ est installé
   → https://www.python.org/downloads/
   ⚠️ Cocher "Add Python to PATH"

2. Extraire le fichier ZIP joint

3. Double-cliquer sur "Lancer_Application.bat"
   → L'application s'ouvre dans votre navigateur

📖 Le fichier LISEZ-MOI.txt dans le dossier contient
   toutes les instructions.

📧 Pour toute question : [votre-email]
📞 Support : [votre-numéro]

Cordialement,
[Votre Nom]
```

**Option B : WeTransfer / Google Drive / Dropbox**

1. Upload le fichier ZIP (si > 25 MB pour email)
2. Générer un lien de partage
3. Envoyer le lien + instructions par email

**Option C : Clé USB**

1. Copier le fichier ZIP sur une clé USB
2. Ajouter un fichier `INSTRUCTIONS.txt` sur la clé

---

### Méthode 2 : Script de Build Automatique

Créer un script qui prépare automatiquement le package :

**Fichier : `build_distribution.sh`** (Linux/Mac)

```bash
#!/bin/bash

echo "================================"
echo "  BUILD DISTRIBUTION PACKAGE"
echo "================================"

# Configuration
VERSION="1.0.0"
OUTPUT_DIR="dist_package"
ZIP_NAME="AliExpress_Scraper_v${VERSION}.zip"

# Nettoyer
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Copier les fichiers essentiels
echo "Copie des fichiers..."
cp -r src/ "$OUTPUT_DIR/"
cp app.py "$OUTPUT_DIR/"
cp requirements.txt "$OUTPUT_DIR/"
cp Lancer_Application.bat "$OUTPUT_DIR/"
cp Lancer_Application.sh "$OUTPUT_DIR/"
cp LISEZ-MOI.txt "$OUTPUT_DIR/"
cp GUIDE_INSTALLATION_CLIENT.md "$OUTPUT_DIR/"
cp README_CLIENT.txt "$OUTPUT_DIR/"

# Nettoyer le cache Python
find "$OUTPUT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$OUTPUT_DIR" -type f -name "*.pyc" -delete

# Créer le ZIP
echo "Création du ZIP..."
cd "$(dirname "$OUTPUT_DIR")"
zip -r "$ZIP_NAME" "$(basename "$OUTPUT_DIR")" -q

echo ""
echo "✅ Package créé : $ZIP_NAME"
echo "📊 Taille : $(du -h "$ZIP_NAME" | cut -f1)"
echo ""
```

**Fichier : `build_distribution.bat`** (Windows)

```batch
@echo off
echo ================================
echo   BUILD DISTRIBUTION PACKAGE
echo ================================

set VERSION=1.0.0
set OUTPUT_DIR=dist_package
set ZIP_NAME=AliExpress_Scraper_v%VERSION%.zip

:: Nettoyer
if exist %OUTPUT_DIR% rmdir /s /q %OUTPUT_DIR%
mkdir %OUTPUT_DIR%

:: Copier les fichiers essentiels
echo Copie des fichiers...
xcopy /E /I /Y src %OUTPUT_DIR%\src
copy /Y app.py %OUTPUT_DIR%\
copy /Y requirements.txt %OUTPUT_DIR%\
copy /Y Lancer_Application.bat %OUTPUT_DIR%\
copy /Y Lancer_Application.sh %OUTPUT_DIR%\
copy /Y LISEZ-MOI.txt %OUTPUT_DIR%\
copy /Y GUIDE_INSTALLATION_CLIENT.md %OUTPUT_DIR%\
copy /Y README_CLIENT.txt %OUTPUT_DIR%\

:: Nettoyer le cache Python
for /d /r %OUTPUT_DIR% %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q %OUTPUT_DIR%\*.pyc 2>nul

:: Créer le ZIP (nécessite PowerShell)
echo Creation du ZIP...
powershell Compress-Archive -Path %OUTPUT_DIR% -DestinationPath %ZIP_NAME% -Force

echo.
echo Package cree : %ZIP_NAME%
echo.
pause
```

**Usage :**
```bash
# Linux/Mac
chmod +x build_distribution.sh
./build_distribution.sh

# Windows
build_distribution.bat
```

---

## 📧 Template d'Email au Client

### Email Initial (Livraison)

```
Objet : 🚀 Livraison de l'Application AliExpress Scraper

Bonjour [Nom du client],

L'application AliExpress Scraper est prête et disponible.

📥 FICHIER :
   AliExpress_Scraper_v1.0.zip (environ [X] MB)
   [Lien WeTransfer/Drive si trop gros pour email]

⚡ INSTALLATION RAPIDE :

1️⃣ Prérequis :
   - Python 3.10 ou supérieur installé
   - Si pas installé : https://www.python.org/downloads/
   - ⚠️ IMPORTANT : Cocher "Add Python to PATH" pendant l'installation

2️⃣ Installation :
   - Extraire le fichier ZIP
   - Ouvrir le dossier extrait

3️⃣ Lancement :
   - Double-cliquer sur "Lancer_Application.bat"
   - Attendre quelques secondes
   - L'application s'ouvre automatiquement dans votre navigateur

📖 DOCUMENTATION :

Le dossier contient :
   - LISEZ-MOI.txt : Guide de démarrage rapide (3 étapes)
   - GUIDE_INSTALLATION_CLIENT.md : Guide complet avec troubleshooting
   - README_CLIENT.txt : Documentation utilisateur détaillée

🎯 UTILISATION :

1. Uploader une image (JPG, PNG)
2. Cliquer sur "Rechercher sur AliExpress"
3. Attendre 1-3 minutes
4. Voir les résultats et exporter si besoin

🆘 SUPPORT :

En cas de problème :
   - Consulter la section "Problèmes Fréquents" dans GUIDE_INSTALLATION_CLIENT.md
   - Me contacter : [votre-email] / [votre-numéro]

Disponibilité du support :
   - Lundi-Vendredi : 9h-18h
   - Email : réponse sous 24h
   - Urgent : [téléphone]

Cordialement,
[Votre Nom]
[Votre Entreprise]
```

### Email de Suivi (J+1)

```
Objet : ✅ Suivi - Application AliExpress Scraper

Bonjour [Nom du client],

Je fais un suivi concernant l'application AliExpress Scraper livrée hier.

❓ L'installation s'est-elle bien passée ?
❓ Avez-vous pu lancer l'application ?
❓ Avez-vous des questions ou rencontré des difficultés ?

Je reste à votre disposition pour toute assistance.

📞 N'hésitez pas à me contacter si besoin.

Cordialement,
[Votre Nom]
```

---

## 🧪 Checklist de Test Avant Distribution

Avant d'envoyer au client, tester sur une **machine propre** (sans Python déjà installé si possible) :

- [ ] **Extraction du ZIP** : Tous les fichiers sont présents
- [ ] **Python non installé** : Le script affiche un message clair
- [ ] **Python installé** : Le script démarre correctement
- [ ] **Dépendances** : Installation automatique fonctionne
- [ ] **Playwright** : Installation automatique fonctionne
- [ ] **Lancement** : Le navigateur s'ouvre automatiquement
- [ ] **Interface** : L'application charge correctement
- [ ] **Upload d'image** : Fonctionne
- [ ] **Recherche** : Retourne des résultats
- [ ] **Export** : CSV/JSON se téléchargent
- [ ] **Arrêt** : L'application s'arrête proprement (fermer le terminal)
- [ ] **Relancement** : Peut être relancée sans problème

---

## 🔧 Maintenance et Mises à Jour

### Versionning

Utiliser la convention **Semantic Versioning** : `MAJOR.MINOR.PATCH`

- `1.0.0` : Version initiale
- `1.0.1` : Correction de bug mineur
- `1.1.0` : Nouvelle fonctionnalité (compatible)
- `2.0.0` : Changement majeur (potentiellement incompatible)

### Distribuer une Mise à Jour

1. **Modifier le code**
2. **Tester complètement**
3. **Mettre à jour la version** dans les fichiers de documentation
4. **Créer un nouveau ZIP** : `AliExpress_Scraper_v1.1.0.zip`
5. **Envoyer au client** avec les notes de version

**Email de mise à jour :**

```
Objet : 🔄 Mise à jour disponible - AliExpress Scraper v1.1.0

Bonjour [Nom du client],

Une nouvelle version de l'application est disponible.

📦 VERSION : 1.1.0 (précédente : 1.0.0)

✨ NOUVEAUTÉS :
   - [Liste des améliorations]
   - [Corrections de bugs]
   - [Nouvelles fonctionnalités]

📥 INSTALLATION :
   1. Télécharger le nouveau ZIP ci-joint
   2. Extraire dans un nouveau dossier
   3. Vos anciennes recherches dans output_recherche*/
      peuvent être copiées si besoin

💡 Vous pouvez garder l'ancienne version en parallèle
   si vous le souhaitez.

Cordialement,
[Votre Nom]
```

---

## 📊 Taille du Package

**Estimation de la taille** :

- Code source (~5-10 MB)
- Documentation (~1 MB)
- Total ZIP : **~10-15 MB**

⚠️ **Les dépendances Python ne sont PAS incluses** dans le ZIP (installées automatiquement par le script)

Si incluses, le package ferait ~500 MB - 2 GB, ce qui est trop lourd pour email.

---

## 🎯 Résumé

**Pour Distribuer au Client :**

1. ✅ Nettoyer le projet (supprimer cache, venv, .git)
2. ✅ Créer le ZIP
3. ✅ Tester sur machine propre
4. ✅ Envoyer par email/WeTransfer/Drive
5. ✅ Fournir support J+1

**Le Client Doit Faire :**

1. ✅ Installer Python 3.10+ (si pas déjà fait)
2. ✅ Extraire le ZIP
3. ✅ Double-cliquer sur `Lancer_Application.bat`
4. ✅ Utiliser l'application

**C'est tout ! Simple et efficace.** ✅

---

**Date de création** : 2025-11-06
**Version du guide** : 1.0.0
