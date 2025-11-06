# 🏗️ Guide de Compilation - PyInstaller

Guide pour compiler l'application en exécutable distributable

---

## 📋 Prérequis

### 1. Python et Dépendances

```bash
# Python 3.10 ou 3.11 recommandé
python --version

# Installer toutes les dépendances
pip install -r requirements.txt

# Installer PyInstaller
pip install pyinstaller
```

### 2. Espace Disque

- **Minimum:** 5GB d'espace libre
- **Recommandé:** 10GB d'espace libre

### 3. RAM

- **Minimum:** 8GB RAM
- **Recommandé:** 16GB RAM (compilation plus rapide)

---

## 🚀 Méthode 1: Script Automatique (RECOMMANDÉ)

### Étape 1: Lancer le Build

```bash
python build_executable.py
```

### Étape 2: Attendre

- ⏱️ **Durée:** 10-30 minutes selon votre machine
- 📊 **Progression:** Affichée dans le terminal
- ☕ **Conseil:** Prenez un café!

### Étape 3: Résultat

```
✅ SUCCÈS! L'exécutable a été créé!

📁 Dossier de sortie:
   dist/AliExpress_Scraper/
   └── AliExpress_Scraper.exe
```

---

## 🔧 Méthode 2: Fichier .spec (Contrôle Avancé)

### Pour Plus de Contrôle

```bash
# Éditer AliExpress_Scraper.spec selon vos besoins
# Puis compiler avec:
pyinstaller AliExpress_Scraper.spec
```

### Options dans le .spec

**Mode --onedir (Recommandé - Plus Rapide):**
```python
# Dans le .spec, ligne ~75
exclude_binaries=True,  # Dossier avec dépendances
```

**Mode --onefile (Un Seul Fichier):**
```python
# Commenter la section COLLECT
# Décommenter la section EXE alternative
```

⚠️ **Attention:** `--onefile` crée un seul fichier mais le démarrage sera très lent (5-10 min)!

---

## 📦 Distribution à l'Utilisateur Final

### Étape 1: Préparer le Package

```bash
# Si --onedir (recommandé):
cd dist/
zip -r AliExpress_Scraper.zip AliExpress_Scraper/

# Ou sur Windows:
# Clic droit sur dist/AliExpress_Scraper → Envoyer vers → Dossier compressé
```

### Étape 2: Créer le Package Complet

**Contenu du ZIP à donner au client:**

```
AliExpress_Scraper.zip
├── AliExpress_Scraper.exe  ← L'exécutable
├── _internal/              ← Dépendances (important!)
├── README_UTILISATEUR.md   ← Guide pour le client
└── ...
```

### Étape 3: Donner au Client

1. **Donnez:** Le fichier `AliExpress_Scraper.zip`
2. **Plus:** Le fichier `README_UTILISATEUR.md`
3. **Instructions:**
   - Décompresser le ZIP
   - Double-cliquer sur AliExpress_Scraper.exe
   - Lire le README pour l'utilisation

---

## 🧪 Testing

### Test sur Machine Propre (IMPORTANT!)

**Avant de distribuer, testez sur une machine qui n'a PAS:**
- Python installé
- Aucune des dépendances du projet
- Idéalement: une VM Windows/Mac propre

### Checklist de Test

- [ ] L'exe se lance sans erreur
- [ ] Le navigateur s'ouvre automatiquement
- [ ] On peut uploader une image
- [ ] La recherche fonctionne
- [ ] Les résultats s'affichent
- [ ] L'export Excel fonctionne
- [ ] Les images se téléchargent
- [ ] Aucune erreur dans les logs

### Créer une VM pour Tests

**Virtualbox (Gratuit):**
```bash
# Télécharger depuis virtualbox.org
# Créer une VM Windows 10/11
# Installer l'exe dedans
# Tester complètement
```

---

## ⚠️ Problèmes Courants et Solutions

### 1. "Module not found" pendant la compilation

**Solution:**
```bash
# Ajouter dans hiddenimports du .spec:
hiddenimports=[
    'nom_du_module_manquant',
    ...
]

# Ou dans build_executable.py:
'--hidden-import=nom_du_module_manquant',
```

### 2. Le fichier est ÉNORME (>2GB)

**C'est normal!** PyTorch + Playwright = très gros.

**Pour réduire:**
```bash
# Dans le .spec, exclure plus de packages:
excludes=[
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'pandas',  # Si non utilisé
    'numpy.random',  # Parties inutilisées
]
```

### 3. L'exe démarre mais plante immédiatement

**Solution:**
```bash
# Compiler en mode console pour voir les erreurs:
python build_executable.py

# Éditer le script et changer:
'--console',  # Au lieu de --windowed
```

### 4. "Failed to execute script" au lancement

**Causes possibles:**
- Chemin avec des espaces ou caractères spéciaux
- Antivirus qui bloque
- Fichiers manquants dans dist/

**Solution:**
```bash
# Recompiler avec --clean:
pyinstaller --clean AliExpress_Scraper.spec
```

### 5. Playwright browsers manquants

**Solution:**
```bash
# Après compilation, installer browsers manuellement:
cd dist/AliExpress_Scraper/_internal/
playwright install chromium
```

Ou inclure dans le .spec:
```python
# Copier les browsers Playwright
import playwright
playwright_path = Path(playwright.__file__).parent
datas += [(str(playwright_path / 'driver'), 'playwright/driver')]
```

---

## 🔒 Sécurité du Code

### Niveau de Protection

**PyInstaller offre:**
- ✅ Code bytecode compilé (non lisible directement)
- ✅ Fichiers .py non accessibles
- ⚠️ MAIS un expert PEUT décompiler avec effort

### Pour Plus de Sécurité

**Option 1: PyArmor (Obfuscation)**
```bash
pip install pyarmor
pyarmor gen app.py src/
# Puis compiler le code obfusqué
```

**Option 2: Cython (Compilation C)**
```bash
pip install cython
cythonize -i src/scraper/*.py
# Compile en .so/.pyd (binaire natif)
```

**Option 3: Licensing**
```python
# Ajouter vérification de licence dans app.py
# Voir DEPLOIEMENT_SECURISATION.md pour le code
```

---

## 📊 Optimisations

### Compilation Plus Rapide

```bash
# Utiliser UPX pour compresser les binaires:
# Télécharger UPX depuis upx.github.io
# Mettre upx.exe dans PATH
# PyInstaller l'utilisera automatiquement

# Dans le .spec:
upx=True,
```

### Taille Plus Petite

```bash
# Exclure des packages lourds non utilisés:
# Dans excludes=[...] du .spec

# Compiler en mode optimisé:
PYTHONOPTIMIZE=2 pyinstaller AliExpress_Scraper.spec
```

### Démarrage Plus Rapide

- ✅ Utiliser `--onedir` (pas `--onefile`)
- ✅ Désactiver UPX si trop lent
- ✅ Mettre l'exe sur un SSD

---

## 🎨 Personnalisation

### Ajouter un Icon

```bash
# Créer/télécharger un icon.ico (Windows) ou icon.icns (Mac)
# Mettre dans le dossier racine

# Dans le .spec:
icon='icon.ico',
```

### Changer le Nom

```python
# Dans build_executable.py ou .spec:
APP_NAME = 'MonNomPersonnalisé'
```

### Ajouter des Fichiers

```python
# Dans le .spec, section datas:
datas = [
    ('README.pdf', '.'),  # Ajouter un PDF
    ('config.ini', '.'),  # Fichier de config
    ('images/', 'images'),  # Dossier d'images
]
```

---

## 📝 Checklist de Distribution

Avant de donner l'exe au client:

- [ ] Testé sur machine propre (sans Python)
- [ ] README_UTILISATEUR.md inclus
- [ ] Version testée de A à Z
- [ ] Aucune donnée sensible dans l'exe
- [ ] Taille du fichier acceptable (<2GB)
- [ ] Antivirus ne le détecte pas comme virus
- [ ] Démarrage en moins de 1 minute
- [ ] Instructions claires pour le client
- [ ] Support prévu pour les questions

---

## 🔄 Mises à Jour

### Distribuer une Nouvelle Version

1. **Modifier le code:**
   ```bash
   git pull  # Récupérer les derniers changements
   ```

2. **Incrémenter la version:**
   ```python
   # Dans app.py, ajouter en haut:
   __version__ = "1.1.0"
   ```

3. **Recompiler:**
   ```bash
   python build_executable.py
   ```

4. **Tester complètement**

5. **Distribuer:**
   - Nouveau ZIP
   - Notes de version (changelog)

---

## 💡 Astuces Pro

### Build Automatique (CI/CD)

```yaml
# GitHub Actions example (.github/workflows/build.yml)
name: Build Executable
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: python build_executable.py
      - uses: actions/upload-artifact@v2
        with:
          name: executable
          path: dist/
```

### Signature de Code (Windows)

```bash
# Pour éviter les avertissements Windows
# Acheter un certificat de signature de code
# Puis signer l'exe:
signtool sign /f certificate.pfx /p password AliExpress_Scraper.exe
```

### Logging pour Debug

```python
# Ajouter dans app.py pour debug:
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 📞 Ressources

- **PyInstaller Docs:** https://pyinstaller.org/en/stable/
- **Common Issues:** https://github.com/pyinstaller/pyinstaller/wiki
- **Stack Overflow:** Tag `pyinstaller`

---

**Bonne compilation! 🚀**
