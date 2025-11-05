# Recherche de Produits AliExpress par Image

Application de recherche de produits sur AliExpress par image, avec interface Streamlit et comparaison de similarité.

## 🎯 Fonctionnalités

- **Upload d'Image** : Uploadez une image de produit depuis votre appareil
- **Recherche Hybride** : Catégorie + Image pour des résultats ultra-pertinents
- **Résultats Pertinents** : Obtient des produits réellement similaires (fini les shampoings quand vous cherchez un sac!)
- **Scraping Intelligent** : Recherche par texte avec catégorie spécifiée
- **Comparaison de Similarité** : Compare votre image avec les produits trouvés en utilisant le hashing perceptuel
- **Tri par Pertinence** : Les résultats sont automatiquement triés par score de similarité
- **Export JSON** : Export des résultats dans deux formats JSON distincts
- **Interface Intuitive** : Interface web Streamlit facile à utiliser

## 📋 Workflow

1. **Uploadez une image** de produit depuis votre ordinateur (ex: un sac Chanel, des chaussures, etc.)
2. **Entrez la catégorie** du produit (ex: bag, ring, shoes, dress)
3. **Cliquez sur "Rechercher sur AliExpress"**
4. L'application va :
   - Se connecter à AliExpress
   - **Rechercher des produits dans la catégorie spécifiée**
   - Télécharger les images et informations des produits
   - Comparer chaque produit avec votre image uploadée
   - Calculer un score de similarité pour chaque produit
5. **Visualisez les résultats** triés par similarité (les plus similaires en premier)
6. **Téléchargez les données** en JSON

## 💡 Exemples de Catégories

- **Sacs** : `bag`, `handbag`, `backpack`, `clutch`
- **Bijoux** : `ring`, `necklace`, `earring`, `bracelet`
- **Vêtements** : `dress`, `shirt`, `jeans`, `jacket`
- **Chaussures** : `shoes`, `sneakers`, `boots`, `heels`
- **Montres** : `watch`, `smartwatch`
- **Accessoires** : `sunglasses`, `belt`, `hat`, `scarf`

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

## 🎯 Comment Fonctionne la Recherche par Image sur AliExpress

L'application utilise la fonctionnalité native de recherche par image d'AliExpress :

### Processus de Recherche

1. **Navigation** : L'application ouvre AliExpress.com
2. **Détection du Bouton** : Recherche l'icône caméra dans la barre de recherche (multiple sélecteurs pour robustesse)
3. **Upload de l'Image** : Upload votre image via le formulaire d'AliExpress
4. **Traitement par AliExpress** : AliExpress analyse l'image et trouve des produits similaires
5. **Extraction des Résultats** : L'application récupère les produits pertinents de la page de résultats

### Stratégies de Fallback

Si la méthode principale échoue :
- Tentative sur `aliexpress.com/wholesale`
- Tentative sur `aliexpress.us/wholesale`
- Multiple sélecteurs CSS pour s'adapter aux changements d'interface

### Avantages

✅ **Pertinence** : Les résultats viennent directement d'AliExpress, garantissant une haute pertinence
✅ **Catégorie Correcte** : Cherchez un sac Chanel → obtenez des sacs, pas des shampoings
✅ **Robustesse** : Multiple stratégies de détection pour s'adapter aux mises à jour d'AliExpress
✅ **Contrôle** : Vous choisissez le nombre exact de résultats (5-50)

## 🔍 Comment Fonctionne la Comparaison de Similarité

L'application utilise **CLIP (Contrastive Language-Image Pre-training)** pour une similarité d'images de haute qualité :

### Technologie CLIP

1. **Modèle Utilisé** : ViT-L-14 pré-entraîné sur Laion2B (2 milliards d'images)
2. **Embeddings** : Chaque image est convertie en vecteur de 768 dimensions
3. **Similarité Cosinus** : Comparaison vectorielle pour un score de 0 à 1
4. **Avantages** :
   - ✅ Comprend le contenu sémantique (pas seulement les pixels)
   - ✅ Robuste aux variations de couleur, rotation, échelle
   - ✅ Scores plus précis que le hashing perceptuel

### Interprétation des Scores CLIP

- **0.8 - 1.0** : Extrêmement similaire (même produit ou variante)
- **0.6 - 0.8** : Très similaire (même catégorie, design proche)
- **0.4 - 0.6** : Modérément similaire (même catégorie générale)
- **0.2 - 0.4** : Faiblement similaire (quelques caractéristiques communes)
- **0.0 - 0.2** : Très différent

### Fallback: Hashing Perceptuel

Si CLIP n'est pas disponible, le système utilise le hashing perceptuel (ahash, phash, dhash, whash) comme fallback

## 🛠️ Technologies Utilisées

- **Python 3.8+**
- **Streamlit** : Interface web
- **Crawlee** : Framework de web scraping
- **Playwright** : Automatisation de navigateur
- **CLIP (OpenCLIP)** : Similarité d'images par deep learning
- **PyTorch** : Backend pour CLIP
- **PIL/Pillow** : Traitement d'images
- **ImageHash** : Hashing perceptuel d'images (fallback)
- **Pydantic** : Validation de données
- **scikit-learn** : Calcul de similarité cosinus

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

## 🔧 Dépannage et Diagnostic

### Outils de Diagnostic Intégrés

Si vous rencontrez des problèmes (ex: score CLIP = 0%, prix manquants, images non affichées), utilisez nos outils de diagnostic:

#### 1. Test CLIP Complet

```bash
python test_clip.py
```

Ce script vérifie:
- ✅ Installation de CLIP et PyTorch
- ✅ Chargement du modèle ViT-L-14
- ✅ Calcul d'embeddings
- ✅ Calcul de similarité
- ✅ Vos modules personnalisés

**Si ce test échoue**, réinstallez CLIP:
```bash
pip install --upgrade open-clip-torch torch torchvision
```

#### 2. Inspection du Dossier Output

```bash
python inspect_output.py
```

Ce script analyse:
- 📦 `product_data.json` (nombre de produits, prix, images)
- 🖼️ `image_metadata.json` (présence de `local_path`, mappings)
- 📁 Structure du dossier `images/` (organisation par produit)
- ✅ Correspondance fichiers/métadonnées

**Détecte automatiquement:**
- Champs manquants dans les JSON
- Images non téléchargées
- Chemins incorrects
- Structure de dossiers obsolète

#### 3. Logs Détaillés de l'Application

Lancez l'app et regardez le terminal:
```bash
streamlit run app.py
```

Les logs afficheront:
- Nombre d'images indexées dans CLIP
- Scores de similarité pour chaque image
- Problèmes de téléchargement
- Erreurs de parsing

### Documentation Complète de Dépannage

Pour un guide détaillé, consultez **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** qui couvre:
- Score CLIP = 0% (causes et solutions)
- Prix non affichés
- Images manquantes
- Organisation des images
- Checklist de vérification complète

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

4. **CLIP Score = 0%** :
   ```bash
   python test_clip.py  # Test diagnostic
   python inspect_output.py  # Vérifier les données
   ```
   Consultez [TROUBLESHOOTING.md](TROUBLESHOOTING.md) pour plus de détails

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
