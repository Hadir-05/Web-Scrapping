# 🖥️ Guide PyWebView - Application Desktop Native

## 🎯 Qu'est-ce que PyWebView ?

PyWebView est une solution **légère** pour créer des applications desktop à partir d'applications web (comme Streamlit). C'est une **meilleure alternative à PyInstaller classique** pour les apps Streamlit car :

- ✅ Plus fiable (moins de bugs de compilation)
- ✅ Fenêtre native (vraie application desktop)
- ✅ Plus léger qu'Electron
- ✅ Meilleure intégration système
- ✅ Fonctionne mieux avec Streamlit

---

## 📋 Prérequis

### Pour le Développeur (Vous)

```bash
# 1. Python 3.11 installé
python --version

# 2. Installer les dépendances
pip install -r requirements.txt

# Ou manuellement :
pip install pywebview pyinstaller streamlit crawlee[playwright]
```

### Pour le Client

**Rien !** Le client reçoit juste un fichier .exe et double-clique dessus.

---

## 🚀 Utilisation Rapide

### Option 1 : Test en Mode Développement

```bash
# Lancer l'application sans compiler
python launcher_pywebview.py
```

Ceci va :
1. Démarrer Streamlit en arrière-plan
2. Ouvrir une fenêtre native
3. Afficher l'interface Streamlit dedans

### Option 2 : Compiler en .exe (Pour Distribution)

```bash
# Compiler l'application
python build_pywebview.py
```

Ceci va :
1. Vérifier les dépendances
2. Nettoyer les builds précédents
3. Créer un fichier .spec optimisé
4. Compiler avec PyInstaller (5-15 minutes)
5. Créer un dossier `dist/AliExpress_Scraper/` avec tout le nécessaire

---

## 📦 Structure Après Compilation

```
dist/
└── AliExpress_Scraper/
    ├── AliExpress_Scraper.exe    ⭐ L'exécutable principal
    ├── app.py                     📄 Votre application Streamlit
    ├── src/                       📁 Code source
    │   ├── aliexpress_scraper.py
    │   └── image_similarity.py
    ├── _internal/                 📁 Librairies Python (auto-généré)
    │   ├── streamlit/
    │   ├── torch/
    │   ├── playwright/
    │   └── ... (beaucoup de fichiers)
    └── README.txt                 📄 Instructions pour le client
```

**⚠️ Important** : Le dossier **COMPLET** doit être distribué, pas juste le .exe !

---

## 📤 Distribution au Client

### Étape 1 : Compiler

```bash
python build_pywebview.py
```

Attendez la fin (5-15 minutes). Vous verrez :
```
✅ BUILD RÉUSSI!

📁 Emplacement:
   dist/AliExpress_Scraper
```

### Étape 2 : Compresser

**Sur Windows :**
```bash
# Aller dans dist/
cd dist

# Compresser le dossier
# Clic droit sur AliExpress_Scraper > Envoyer vers > Dossier compressé
```

**Ou avec PowerShell :**
```powershell
Compress-Archive -Path "dist/AliExpress_Scraper" -DestinationPath "AliExpress_Scraper_v1.0.zip"
```

**Sur Linux/Mac :**
```bash
cd dist
zip -r AliExpress_Scraper_v1.0.zip AliExpress_Scraper/
```

### Étape 3 : Envoyer au Client

**Par email :**
```
Bonjour,

Veuillez trouver ci-joint l'application AliExpress Scraper.

📥 Installation :
1. Extraire le fichier .zip
2. Ouvrir le dossier extrait
3. Double-cliquer sur AliExpress_Scraper.exe
4. L'application s'ouvre dans une fenêtre

⚠️ Important :
- Tous les fichiers du dossier sont nécessaires
- Windows Defender peut afficher un avertissement au premier lancement (c'est normal)
- Cliquer sur "Informations complémentaires" puis "Exécuter quand même"

📖 Documentation complète dans le fichier README.txt

Cordialement,
```

**Par WeTransfer / Google Drive / Dropbox :**
1. Upload le fichier .zip
2. Envoyer le lien de téléchargement
3. Ajouter les instructions ci-dessus

---

## 🛠️ Utilisation Côté Client

### Installation (Client)

1. **Télécharger** le fichier `AliExpress_Scraper_v1.0.zip`

2. **Extraire** le .zip :
   - Clic droit sur le fichier
   - "Extraire tout..."
   - Choisir un emplacement (ex: Bureau, Documents)

3. **Ouvrir** le dossier extrait

4. **Double-cliquer** sur `AliExpress_Scraper.exe`

5. **Autoriser** si Windows Defender demande :
   - Cliquer sur "Informations complémentaires"
   - Cliquer sur "Exécuter quand même"

6. **L'application s'ouvre** dans une fenêtre ✅

### Première Utilisation

Quand l'application démarre :

```
🚀 Démarrage de Streamlit sur le port 8501...
📁 Application: C:\...\app.py
✅ Streamlit démarré
⏳ Attente du démarrage de Streamlit...
✅ Streamlit est prêt sur le port 8501
🎨 Ouverture de l'interface...
```

Après 5-10 secondes, la fenêtre de l'application s'ouvre.

---

## 🔧 Résolution de Problèmes

### Problème 1 : "Windows a protégé votre ordinateur"

**Cause** : Windows Defender ne reconnaît pas l'application (normal pour les nouvelles apps)

**Solution** :
1. Cliquer sur **"Informations complémentaires"**
2. Cliquer sur **"Exécuter quand même"**

**Ou** : Ajouter une exception dans Windows Defender :
- Paramètres Windows > Mise à jour et sécurité > Sécurité Windows
- Protection contre les virus et menaces > Gérer les paramètres
- Exclusions > Ajouter une exclusion
- Choisir le dossier `AliExpress_Scraper`

---

### Problème 2 : L'application ne démarre pas (aucune fenêtre)

**Diagnostic** :

1. **Vérifier que TOUS les fichiers sont présents** :
   - Le client a-t-il extrait le .zip ?
   - Le dossier `_internal/` existe-t-il ?
   - Le fichier `app.py` est-il présent ?

2. **Vérifier les antivirus** :
   - Désactiver temporairement l'antivirus
   - Tester si l'app démarre

3. **Lancer en mode console** (pour voir les erreurs) :
   - Ouvrir PowerShell dans le dossier
   - Exécuter : `.\AliExpress_Scraper.exe`
   - Lire les messages d'erreur

---

### Problème 3 : "Le port 8501 est déjà utilisé"

**Cause** : Une instance de Streamlit tourne déjà

**Solution** :

**Option A** : Fermer l'instance existante
```powershell
# Windows PowerShell (Administrateur)
Get-Process | Where-Object {$_.Path -like "*streamlit*"} | Stop-Process -Force
```

**Option B** : Le launcher détecte automatiquement un port libre
- Le launcher cherche automatiquement un port disponible (8501, 8502, 8503...)
- Normalement cela ne devrait pas arriver

---

### Problème 4 : "Impossible de démarrer Streamlit"

**Causes possibles** :
- Fichier `app.py` manquant
- Dossier `src/` manquant
- Dépendances manquantes

**Solution** :
1. Vérifier que le dossier est complet
2. Recompiler avec `python build_pywebview.py`
3. Vérifier que toutes les dépendances sont dans requirements.txt

---

### Problème 5 : Erreur "ModuleNotFoundError"

**Cause** : Une librairie Python n'a pas été incluse dans le build

**Solution** :
1. Identifier la librairie manquante (ex: `ModuleNotFoundError: No module named 'xyz'`)

2. Modifier `build_pywebview.py` et ajouter dans `hiddenimports` :
```python
hiddenimports=[
    'streamlit',
    'pywebview',
    'xyz',  # ← Ajouter ici
    # ...
]
```

3. Recompiler :
```bash
python build_pywebview.py
```

---

## ⚙️ Configuration Avancée

### Personnaliser la Fenêtre

Modifier `launcher_pywebview.py` :

```python
# Configuration
APP_TITLE = "Votre Nom d'App"     # Titre de la fenêtre
WINDOW_WIDTH = 1400                # Largeur en pixels
WINDOW_HEIGHT = 900                # Hauteur en pixels
STREAMLIT_PORT = 8501              # Port Streamlit
```

### Ajouter une Icône

1. **Créer ou obtenir une icône** (.ico pour Windows, .icns pour Mac)

2. **Placer** le fichier `icon.ico` dans le dossier du projet

3. **Le build script** le détecte automatiquement

4. **Recompiler** :
```bash
python build_pywebview.py
```

### Changer le Nom de l'Application

Modifier `build_pywebview.py` :

```python
# Configuration
APP_NAME = "VotreNomApp"  # Sans espaces
```

---

## 📊 Comparaison : PyWebView vs PyInstaller Classique

| Critère | PyInstaller Classique | **PyWebView** |
|---------|----------------------|--------------|
| Compilation Streamlit | ⭐⭐ Problèmes fréquents | ⭐⭐⭐⭐⭐ Fiable |
| Taille de l'exe | 500MB - 2GB | 500MB - 2GB |
| Fenêtre native | ❌ Console ou windowed basique | ✅ Vraie fenêtre native |
| Démarrage | ⭐⭐ Lent (30-60s) | ⭐⭐⭐⭐ Rapide (5-10s) |
| Bugs | ⭐⭐ Fréquents avec Streamlit | ⭐⭐⭐⭐ Rares |
| Facilité de debug | ❌ Difficile | ✅ Messages clairs |
| Compatible Streamlit | ⚠️ Partiellement | ✅ Totalement |

---

## 🎯 Workflow Recommandé

### Phase 1 : Développement

```bash
# Développer normalement avec Streamlit
streamlit run app.py

# Tester avec PyWebView
python launcher_pywebview.py
```

### Phase 2 : Test de Compilation

```bash
# Compiler une première fois
python build_pywebview.py

# Tester l'exe
cd dist/AliExpress_Scraper
./AliExpress_Scraper.exe

# Vérifier que tout fonctionne
```

### Phase 3 : Distribution

```bash
# Build final
python build_pywebview.py

# Compresser
Compress-Archive -Path "dist/AliExpress_Scraper" -DestinationPath "AliExpress_Scraper_v1.0.zip"

# Envoyer au client
```

---

## 💡 Astuces

### Astuce 1 : Réduire la Taille de l'Exe

Dans `build_pywebview.py`, ajouter plus d'exclusions :

```python
excludes=[
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'tkinter',
    'unittest',  # ← Ajouter
    'xml',       # ← Ajouter
    'pydoc',     # ← Ajouter
]
```

### Astuce 2 : Build Plus Rapide (Développement)

```bash
# Ne pas nettoyer les builds précédents
# Modifier build_pywebview.py : commenter clean_previous_builds()
```

### Astuce 3 : Mode Debug

Modifier `launcher_pywebview.py` :

```python
# Activer le mode debug
webview.start(debug=True)  # ← Affiche la console JS

# Activer la console Streamlit
console=True,  # ← Dans create_window()
```

### Astuce 4 : Versionning

Créer des builds versionnés :

```bash
# Modifier APP_NAME dans build_pywebview.py
APP_NAME = "AliExpress_Scraper_v1.0.0"
```

---

## 🔐 Sécurité et Protection du Code

### Ce qui est protégé :
- ✅ Le code Python est compilé en bytecode (.pyc)
- ✅ Le code est dans l'archive PyInstaller (difficile d'accès)
- ✅ Les fichiers sont empaquetés

### Ce qui n'est PAS protégé :
- ⚠️ Le bytecode peut être décompilé (difficile mais possible)
- ⚠️ Les strings et constantes sont lisibles

### Pour Plus de Sécurité :

**Option 1** : Obfuscation avant compilation
```bash
pip install pyarmor
pyarmor pack launcher_pywebview.py
```

**Option 2** : Architecture API (voir GUIDE_ARCHITECTURE_API.md)
- Le code sensible reste sur VOTRE serveur
- Le client a juste l'interface

---

## 📚 Ressources

- **PyWebView Documentation** : https://pywebview.flowrl.com/
- **PyInstaller Manual** : https://pyinstaller.org/en/stable/
- **Streamlit Docs** : https://docs.streamlit.io/

---

## ✅ Checklist de Distribution

Avant d'envoyer au client :

- [ ] L'application compile sans erreur
- [ ] L'exe a été testé sur une machine propre (sans Python)
- [ ] Tous les fichiers sont dans dist/AliExpress_Scraper/
- [ ] Le README.txt est présent et à jour
- [ ] Le .zip a été créé
- [ ] Le .zip a été testé (extraire et lancer)
- [ ] Les instructions d'installation sont claires
- [ ] Un canal de support est disponible (email, téléphone)

---

## 🎉 Résumé

**Pour VOUS (Développeur) :**
```bash
# 1. Développer
streamlit run app.py

# 2. Tester
python launcher_pywebview.py

# 3. Compiler
python build_pywebview.py

# 4. Distribuer
Compress-Archive dist/AliExpress_Scraper AliExpress_Scraper.zip
```

**Pour le CLIENT :**
```
1. Télécharger le .zip
2. Extraire
3. Double-cliquer sur l'exe
4. Utiliser l'application
```

**Simple, efficace, et ça marche ! ✅**

---

**Date de création** : 2025-11-06
**Version** : 1.0.0
**Auteur** : AliExpress Scraper Team
