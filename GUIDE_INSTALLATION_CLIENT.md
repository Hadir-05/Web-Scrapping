# 🚀 Guide d'Installation - AliExpress Scraper

## 📋 Pour le Client

Ce guide explique comment installer et utiliser l'application AliExpress Scraper sur votre ordinateur.

---

## ✅ Prérequis

### Windows

**Python 3.10 ou supérieur**

1. Télécharger Python depuis : https://www.python.org/downloads/
2. Lancer l'installateur
3. ⚠️ **IMPORTANT** : Cocher **"Add Python to PATH"**
4. Cliquer sur "Install Now"
5. Attendre la fin de l'installation

**Comment vérifier que Python est installé :**
```bash
# Ouvrir PowerShell ou CMD et taper :
python --version
```

Vous devriez voir : `Python 3.10.x` ou supérieur

---

### macOS

**Python 3.10 ou supérieur**

```bash
# Installer Homebrew (si pas déjà installé)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Python
brew install python3

# Vérifier
python3 --version
```

---

### Linux (Ubuntu/Debian)

```bash
# Mettre à jour les packages
sudo apt update

# Installer Python 3 et pip
sudo apt install python3 python3-pip

# Vérifier
python3 --version
```

---

## 📦 Installation de l'Application

### Étape 1 : Extraire le Fichier ZIP

1. Télécharger le fichier `AliExpress_Scraper.zip`
2. Clic droit sur le fichier → **"Extraire tout..."**
3. Choisir un emplacement (ex: Bureau, Documents)
4. Cliquer sur **"Extraire"**

### Étape 2 : Ouvrir le Dossier

Ouvrir le dossier extrait. Vous devriez voir :

```
AliExpress_Scraper/
├── Lancer_Application.bat        ⭐ Pour Windows
├── Lancer_Application.sh          ⭐ Pour macOS/Linux
├── app.py
├── requirements.txt
├── src/
├── GUIDE_INSTALLATION_CLIENT.md   (ce fichier)
└── ...
```

---

## 🚀 Lancement de l'Application

### Sur Windows

**Méthode 1 : Double-clic (Recommandé)**

1. **Double-cliquer** sur `Lancer_Application.bat`
2. Une fenêtre noire (terminal) s'ouvre
3. L'installation des dépendances démarre automatiquement (première fois seulement)
4. Après quelques secondes, **votre navigateur s'ouvre automatiquement**
5. L'application est prête ! ✅

**Méthode 2 : Manuelle**

```bash
# Ouvrir PowerShell dans le dossier
# Clic droit dans le dossier → "Ouvrir dans le terminal"

# Installer les dépendances (première fois seulement)
pip install -r requirements.txt
playwright install chromium

# Lancer l'application
streamlit run app.py
```

---

### Sur macOS / Linux

**Méthode 1 : Script (Recommandé)**

```bash
# Ouvrir le terminal dans le dossier
cd /chemin/vers/AliExpress_Scraper

# Lancer le script
./Lancer_Application.sh
```

**Méthode 2 : Manuelle**

```bash
# Installer les dépendances (première fois seulement)
pip3 install -r requirements.txt
playwright install chromium

# Lancer l'application
streamlit run app.py
```

---

## 🎯 Utilisation de l'Application

### 1. Accès à l'Interface

Après le lancement :
- **Automatique** : Le navigateur s'ouvre sur http://localhost:8501
- **Manuel** : Ouvrir votre navigateur et aller sur http://localhost:8501

### 2. Rechercher des Produits

**Onglet "Recherche" :**

1. **Uploader une image** :
   - Cliquer sur "Browse files"
   - Choisir une image de votre ordinateur
   - Formats acceptés : JPG, PNG, WEBP

2. **Configurer la recherche** :
   - Nombre de résultats : 10-50 (recommandé : 20)
   - Catégorie (optionnel) : laisser vide

3. **Lancer la recherche** :
   - Cliquer sur **"Rechercher sur AliExpress"**
   - Attendre 1-3 minutes
   - Les résultats s'affichent automatiquement

### 3. Voir les Résultats

**Onglet "Résultats Détaillés" :**

- Voir tous les produits trouvés
- Images, prix, titres
- Scores de similarité (calculés par IA)
- Liens vers AliExpress

**Onglet "Exporter" :**

- Sélectionner les produits voulus
- Télécharger en CSV ou JSON
- Les fichiers sont sauvegardés dans le dossier de l'application

---

## 🛑 Arrêter l'Application

### Windows

- **Fermer la fenêtre noire (terminal)** qui s'est ouverte au lancement
- Ou faire **Ctrl+C** dans la fenêtre

### macOS / Linux

- **Ctrl+C** dans le terminal
- Ou fermer le terminal

---

## ⚠️ Problèmes Fréquents

### Problème 1 : "Python n'est pas reconnu..."

**Cause** : Python n'est pas dans le PATH

**Solution** :
1. Réinstaller Python
2. ⚠️ Cocher **"Add Python to PATH"**
3. Redémarrer l'ordinateur
4. Réessayer

---

### Problème 2 : L'application ne démarre pas

**Solution** :

```bash
# Ouvrir PowerShell/Terminal dans le dossier

# Installer les dépendances manuellement
pip install -r requirements.txt

# Installer Playwright
playwright install chromium

# Réessayer
streamlit run app.py
```

---

### Problème 3 : "Le port 8501 est déjà utilisé"

**Cause** : Une instance de l'application tourne déjà

**Solution Windows** :

```bash
# Ouvrir PowerShell (Administrateur)
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```

**Solution macOS/Linux** :

```bash
# Tuer le processus
pkill -f streamlit
```

---

### Problème 4 : La recherche ne retourne rien

**Vérifications** :

1. ✅ Connexion Internet active
2. ✅ Image uploadée est valide (JPG/PNG)
3. ✅ AliExpress est accessible depuis votre pays
4. ✅ Playwright est installé : `playwright install chromium`

**Solution** :

```bash
# Réinstaller Playwright
pip install playwright
playwright install chromium
```

---

### Problème 5 : "ModuleNotFoundError: No module named 'xxx'"

**Cause** : Une dépendance manquante

**Solution** :

```bash
# Réinstaller toutes les dépendances
pip install -r requirements.txt --upgrade
```

---

## 📊 Fichiers Générés

L'application crée des dossiers pour chaque recherche :

```
AliExpress_Scraper/
├── output_recherche1/
│   ├── images/              (images téléchargées)
│   ├── image_metadata.json  (métadonnées)
│   └── product_data.json    (données produits)
├── output_recherche2/
├── output_recherche3/
└── ...
```

Ces dossiers contiennent :
- ✅ Les images téléchargées
- ✅ Les données des produits (JSON)
- ✅ Les exports (CSV)

---

## 🆘 Support

### Informations à Fournir en Cas de Problème

1. **Système d'exploitation** : Windows 10/11, macOS, Linux
2. **Version de Python** : `python --version`
3. **Message d'erreur complet** : copier/coller le texte
4. **Capture d'écran** de l'erreur

### Contact

📧 Email : [votre-email@example.com]
📞 Téléphone : [votre-numéro]
💬 Support : [lien vers support]

---

## 💡 Conseils d'Utilisation

### Pour de Meilleurs Résultats

✅ **Utilisez des images de bonne qualité** (au moins 500x500 pixels)
✅ **Images claires** avec fond uni si possible
✅ **Patience** : Les recherches prennent 1-3 minutes
✅ **Connexion stable** : Ne pas interrompre pendant la recherche

### Limites

⚠️ **Quota AliExpress** : Éviter trop de recherches rapides (limite anti-bot)
⚠️ **Taille des images** : Max 10 MB par image
⚠️ **Formats supportés** : JPG, PNG, WEBP principalement

---

## 🔒 Confidentialité

- ✅ Aucune donnée n'est envoyée à des serveurs tiers
- ✅ Les recherches sont faites directement sur AliExpress
- ✅ Les images restent sur votre ordinateur
- ✅ Aucun tracking, aucune collecte de données

---

## 📝 Notes de Version

**Version 1.0.0** (Novembre 2025)
- Recherche par image sur AliExpress
- Calcul de similarité avec IA (CLIP)
- Export CSV et JSON
- Interface graphique intuitive
- Support Windows, macOS, Linux

---

## ✅ Checklist de Première Utilisation

- [ ] Python 3.10+ installé (avec PATH sur Windows)
- [ ] Fichier ZIP extrait dans un dossier accessible
- [ ] Double-clic sur `Lancer_Application.bat` (Windows)
- [ ] Navigateur ouvert automatiquement
- [ ] Image uploadée (JPG/PNG)
- [ ] Recherche lancée
- [ ] Résultats obtenus (1-3 minutes)
- [ ] Export CSV/JSON fonctionnel

---

## 🎉 C'est Prêt !

Vous êtes maintenant prêt à utiliser AliExpress Scraper !

**Bon scraping !** 🚀

---

**Date de création** : 2025-11-06
**Version** : 1.0.0
**Documentation complète** : Voir les autres fichiers `.md` du projet
