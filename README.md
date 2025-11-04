# Web Scraper avec Recherche d'Images

Application de web scraping avec interface Streamlit, utilisant Crawlee pour le scraping et recherche par similarité d'images.

## Fonctionnalités

- **Web Scraping** : Extraction automatique de produits et images depuis n'importe quel site web
- **Scraping avec Crawlee** : Utilisation de Crawlee avec Playwright pour un scraping robuste
- **Recherche par image** : Recherche d'images similaires utilisant le hashing perceptuel
- **Interface Streamlit** : Interface web intuitive et facile à utiliser
- **Export JSON** : Export des résultats dans deux formats JSON distincts
- **Détection de doublons** : Identification automatique des images en double

## Structure du Projet

```
Web-Scrapping/
├── src/
│   ├── scraper/          # Module de scraping avec Crawlee
│   ├── image_search/     # Module de recherche par image
│   ├── models/           # Modèles de données
│   └── ui/               # Composants UI (extensible)
├── output/               # Résultats du scraping
│   ├── images/           # Images téléchargées
│   ├── image_metadata.json
│   └── product_data.json
├── app.py                # Application Streamlit principale
├── requirements.txt      # Dépendances Python
└── README.md             # Ce fichier
```

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip

### Étapes d'installation

1. Cloner le repository :
```bash
git clone <url-du-repo>
cd Web-Scrapping
```

2. Créer un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Installer les navigateurs Playwright :
```bash
playwright install
```

## Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Fonctionnalités de l'interface

#### 1. Onglet Scraping

- Entrez l'URL du site à scraper
- Configurez le nombre maximum de requêtes
- Lancez le scraping
- Visualisez un aperçu des résultats

#### 2. Onglet Recherche d'Images

- Téléchargez une image de référence
- Ajustez le seuil de similarité
- Recherchez des images similaires dans la base
- Détectez les doublons

#### 3. Onglet Résultats

- Visualisez les fichiers JSON générés
- Téléchargez les résultats
- Parcourez la galerie d'images

## Formats de sortie

### 1. image_metadata.json

Contient les métadonnées basiques des images :

```json
[
  {
    "src": "https://example.com/image.jpg",
    "link": "https://example.com/product"
  }
]
```

### 2. product_data.json

Contient les données complètes des produits :

```json
[
  {
    "item_url": "https://example.com/product",
    "collection_date": "2024-01-01T12:00:00",
    "src_image": "https://example.com/main-image.jpg",
    "title": "Product Title",
    "description": "Product description...",
    "price": "$99.99",
    "screenshot_path": "output/images/screenshot_product_1.png",
    "product_image_paths": [
      "output/images/image_0001.jpg",
      "output/images/image_0002.jpg"
    ]
  }
]
```

## Personnalisation

### Adapter le scraper pour un site spécifique

Le scraper est conçu de manière générique pour fonctionner avec la plupart des sites web. Pour l'adapter à un site spécifique, modifiez la méthode `_extract_product_data` dans `src/scraper/web_scraper.py`.

### Changer le modèle de similarité

Le module actuel utilise le hashing perceptuel. Pour utiliser votre propre modèle de similarité :

1. Créez une nouvelle classe dans `src/image_search/`
2. Implémentez les méthodes `add_image` et `search_similar`
3. Remplacez `ImageSimilaritySearch` dans `app.py`

## Architecture

### Module Scraper

- Utilise **Crawlee** avec Playwright pour naviguer et extraire les données
- Télécharge automatiquement les images
- Prend des captures d'écran
- Gère les URLs relatives et absolues

### Module Image Search

- Utilise plusieurs algorithmes de hashing (ahash, phash, dhash, whash)
- Compare les images par similarité perceptuelle
- Détecte les doublons
- Recherche rapide dans de grandes collections

### Modèles de Données

- `ImageMetadata` : Métadonnées simples des images
- `ProductData` : Données complètes des produits
- `DataManager` : Gestion de la sérialisation/désérialisation JSON

## Technologies Utilisées

- **Crawlee** : Framework de web scraping
- **Playwright** : Automatisation de navigateur
- **Streamlit** : Interface web
- **PIL/Pillow** : Traitement d'images
- **ImageHash** : Hashing perceptuel d'images

## Limitations et Notes

- Le scraping peut être lent pour de grandes collections
- Certains sites peuvent bloquer le scraping (respectez les robots.txt)
- La recherche par image utilise le hashing perceptuel (adapté pour les doublons et images similaires)
- Pour une similarité sémantique plus avancée, envisagez d'utiliser des modèles de deep learning

## Développement Futur

- [ ] Intégration de modèles de deep learning pour la similarité d'images
- [ ] Support de la parallélisation du scraping
- [ ] Cache des résultats de scraping
- [ ] Export vers d'autres formats (CSV, Excel)
- [ ] API REST pour l'automatisation

## Licence

MIT

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
