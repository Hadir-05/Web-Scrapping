# Recherche de Produits AliExpress par Image

Application de recherche de produits sur AliExpress par image, avec interface Streamlit et comparaison de similarité.

## 🎯 Fonctionnalités

- **Upload d'Image** : Uploadez une image de produit depuis votre appareil
- **Recherche sur AliExpress** : Recherche automatique de produits similaires sur AliExpress
- **Scraping Intelligent** : Utilise Crawlee avec Playwright pour un scraping robuste
- **Comparaison de Similarité** : Compare votre image avec les produits trouvés en utilisant le hashing perceptuel
- **Tri par Pertinence** : Les résultats sont automatiquement triés par score de similarité
- **Export JSON** : Export des résultats dans deux formats JSON distincts
- **Interface Intuitive** : Interface web Streamlit facile à utiliser

## 📋 Workflow

1. **Uploadez une image** de produit depuis votre ordinateur
2. **Cliquez sur "Rechercher sur AliExpress"**
3. L'application va :
   - Se connecter à AliExpress
   - Rechercher des produits (via recherche par image ou recherche générale)
   - Télécharger les images et informations des produits
   - Comparer chaque produit avec votre image uploadée
   - Calculer un score de similarité pour chaque produit
4. **Visualisez les résultats** triés par similarité
5. **Téléchargez les données** en JSON

## 🏗️ Structure du Projet

```
Web-Scrapping/
├── src/
│   ├── scraper/
│   │   ├── aliexpress_scraper.py    # Scraper spécialisé pour AliExpress
│   │   └── web_scraper.py           # Scraper générique (optionnel)
│   ├── image_search/
│   │   └── image_similarity.py      # Recherche par similarité d'images
│   ├── models/
│   │   └── data_models.py           # Modèles de données
│   └── ui/
├── output/                           # Résultats
│   ├── images/                       # Images téléchargées
│   ├── image_metadata.json
│   └── product_data.json
├── app.py                            # Application Streamlit principale
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### Prérequis

- Python 3.8 ou supérieur
- pip
- Connexion internet

### Installation Complète

#### Sur Windows :

```bash
# 1. Cloner le repository
git clone https://github.com/Hadir-05/Web-Scrapping.git
cd Web-Scrapping
git checkout claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Installer les navigateurs Playwright
playwright install chromium
```

#### Sur Linux/Mac :

```bash
# 1. Cloner le repository
git clone https://github.com/Hadir-05/Web-Scrapping.git
cd Web-Scrapping
git checkout claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Installer les navigateurs Playwright
playwright install chromium
```

## 🚀 Utilisation

### Lancer l'Application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

### Guide d'Utilisation

#### 1. Onglet "Recherche par Image"

- Cliquez sur "Browse files" pour uploader une image
- L'image s'affichera à gauche
- Cliquez sur "Rechercher sur AliExpress"
- Attendez que la recherche se termine (peut prendre quelques minutes)
- Les 6 meilleurs résultats s'affichent automatiquement

#### 2. Onglet "Résultats Détaillés"

- Voir tous les produits trouvés
- Chaque produit affiche :
  - Image du produit
  - Titre
  - Prix
  - Score de similarité avec votre image
  - Lien vers AliExpress
  - Date de collecte

#### 3. Onglet "Export"

- Télécharger les fichiers JSON
- Visualiser la galerie d'images
- Voir un aperçu des données

## 📦 Formats de Sortie

### 1. image_metadata.json

Contient les métadonnées basiques des images trouvées :

```json
[
  {
    "src": "https://ae01.alicdn.com/kf/example.jpg",
    "link": "https://www.aliexpress.com/item/12345.html"
  }
]
```

### 2. product_data.json

Contient les données complètes des produits :

```json
[
  {
    "item_url": "https://www.aliexpress.com/item/12345.html",
    "collection_date": "2024-01-15T14:30:00",
    "src_image": "https://ae01.alicdn.com/kf/example.jpg",
    "title": "Product Name",
    "description": "Product description...",
    "price": "$19.99",
    "screenshot_path": "output/images/screenshot_product_1.png",
    "product_image_paths": [
      "output/images/image_0001.jpg",
      "output/images/image_0002.jpg"
    ]
  }
]
```

## 🔧 Configuration

### Paramètres Ajustables (Sidebar)

- **Répertoire de sortie** : Où sauvegarder les résultats (défaut: `output`)
- **Nombre max de produits** : Combien de produits rechercher (5-50, défaut: 20)

### Personnalisation Avancée

Pour personnaliser le scraper AliExpress, modifiez :
- `src/scraper/aliexpress_scraper.py` : Logique de scraping
- `src/image_search/image_similarity.py` : Algorithme de similarité

## 🔍 Comment Fonctionne la Recherche par Similarité

L'application utilise le **hashing perceptuel** pour comparer les images :

1. **Calcul des Hashes** : Pour chaque image (la vôtre et celles trouvées), 4 types de hash sont calculés :
   - Average Hash (ahash)
   - Perceptual Hash (phash) - le plus fiable
   - Difference Hash (dhash)
   - Wavelet Hash (whash)

2. **Comparaison** : Les hashes de votre image sont comparés avec ceux des produits

3. **Score de Similarité** : Un score de 0% à 100% est calculé :
   - 100% = Images identiques
   - 80-100% = Très similaires
   - 60-80% = Similaires
   - <60% = Peu similaires

4. **Tri** : Les produits sont triés du plus similaire au moins similaire

## 🛠️ Technologies Utilisées

- **Python 3.8+**
- **Streamlit** : Interface web
- **Crawlee** : Framework de web scraping
- **Playwright** : Automatisation de navigateur
- **PIL/Pillow** : Traitement d'images
- **ImageHash** : Hashing perceptuel d'images
- **Pydantic** : Validation de données

## ⚠️ Limitations et Notes

- **Temps de recherche** : La recherche peut prendre 2-5 minutes selon le nombre de produits
- **Respect des ToS** : Utilisez l'application de manière responsable et respectez les conditions d'utilisation d'AliExpress
- **Qualité de l'image** : Pour de meilleurs résultats, utilisez des images claires et nettes
- **Connexion** : Une connexion internet stable est requise
- **Headless Mode** : Par défaut, le navigateur s'exécute en arrière-plan (headless=True)

## 🔮 Développement Futur

- [ ] Support de multiples plateformes (Amazon, eBay, etc.)
- [ ] Intégration de modèles de deep learning (ResNet, EfficientNet)
- [ ] Cache des résultats
- [ ] Comparaison de prix entre plateformes
- [ ] API REST
- [ ] Mode batch pour traiter plusieurs images

## 🤝 Personnalisation avec Votre Modèle

Pour remplacer le système de similarité actuel par votre propre modèle :

1. Créez une nouvelle classe dans `src/image_search/`
2. Implémentez les méthodes :
   ```python
   def add_image(self, image_path, metadata)
   def search_similar(self, query_image_path, top_k, threshold)
   ```
3. Remplacez `ImageSimilaritySearch` dans `app.py:62` par votre classe

## 📝 Licence

MIT

## 🐛 Problèmes Connus

Si vous rencontrez des erreurs :

1. **Erreur d'import Crawlee** :
   ```bash
   pip uninstall crawlee -y
   pip install crawlee[playwright]==1.0.4
   ```

2. **Playwright non installé** :
   ```bash
   playwright install chromium --with-deps
   ```

3. **Permissions** : Sur Linux, vous pourriez avoir besoin de :
   ```bash
   sudo playwright install-deps
   ```

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
