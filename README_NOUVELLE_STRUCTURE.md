# 🔍 Application Multi-Plateformes - AliExpress & MercadoLibre

## ✅ Intégration Terminée

L'application a été restructurée avec succès pour supporter deux plateformes de scraping avec analyse CLIP.

---

## 📁 Nouvelle Structure

```
Web-Scrapping/
├── app.py                              # 🏠 Page d'accueil (choix de plateforme)
├── pages/
│   ├── 1_🛒_AliExpress.py             # Page AliExpress (code existant)
│   └── 2_🌍_MercadoLibre.py           # Page MercadoLibre (nouveau)
├── src/
│   ├── scraper/
│   │   └── aliexpress_scraper.py      # Scraper AliExpress existant
│   ├── image_search/
│   │   ├── image_similarity.py        # CLIP pour AliExpress
│   │   └── clip_similarity.py
│   ├── models/
│   │   └── data_models.py
│   └── mercadolibre_helpers.py        # 🆕 Fonctions CLIP/CLIPSeg/U-Net pour MercadoLibre
├── RESULTATS/
│   ├── aliexpress/                     # Résultats AliExpress
│   │   └── recherche_YYYY-MM-DD_HH-MM-SS/
│   └── mercadolibre/                   # Résultats MercadoLibre
│       └── recherche_YYYY-MM-DD_HH-MM-SS/
└── requirements.txt
```

---

## 🚀 Lancement de l'Application

```bash
streamlit run app.py
```

L'application s'ouvrira sur une page d'accueil vous permettant de choisir entre:
- **🛒 AliExpress** : Recherche par image native + CLIP ViT-L-14
- **🌍 MercadoLibre** : Scraping BeautifulSoup + CLIP avancé (CLIPSeg + U-Net)

---

## 🌍 MercadoLibre - Fonctionnalités

### ✅ Déjà Implémenté

1. **Scraping BeautifulSoup**
   - Multi-pays (México, Argentina, Brasil, Chile, Colombia)
   - Pagination automatique
   - Téléchargement des images produits
   - Sauvegarde dans `RESULTATS/mercadolibre/`

2. **Interface Streamlit**
   - Upload d'image de référence
   - Sélection du pays
   - Configuration du nombre de résultats
   - Affichage des produits trouvés
   - Export Excel

3. **Dictionnaires Multilingues**
   - Mots-clés en français, anglais, espagnol, portugais
   - Support de 12 types de produits (255, Timeless, Chanel 22, Slingback, etc.)

### 🚧 En Développement (TODO)

L'intégration CLIP/CLIPSeg/U-Net complète est prête dans `src/mercadolibre_helpers.py` avec:

- **CLIP** : Embeddings d'images pour similarité
- **CLIPSeg** : Segmentation sémantique (détection de zones spécifiques)
- **U-Net** : Détection de détails (fermoirs, logos, etc.)
- **Vision Transformer** : Classification par catégories

**Fonctions disponibles:**
```python
# Dans src/mercadolibre_helpers.py

# Chargement et traitement d'images
load_image(path_or_url)
load_vit_model_chanelcategories(model_path, num_classes, device)
verify_image_category(model, image, user_choice, device)

# Segmentation avec CLIPSeg
get_crop_clip_seg(pil_image, prompt, clipseg_model, clipseg_processor, ...)

# Détection de détails (fermoirs, etc.)
get_crop_fermoir(cand_image, mask_sac, clipseg_model, ...)

# Construction de bases de données d'embeddings
build_reference_from_image(ref_image, product_name, PRODUCT_PROMPTS, ...)
build_candidates_db_from_urls(listings, product_name, PRODUCT_PROMPTS, ...)

# Comparaison et scoring
compare_candidates_to_reference(ref_meta, cand_meta, sim_threshold, ...)
```

**Pour intégrer:**
1. Importer les fonctions dans `pages/2_🌍_MercadoLibre.py`
2. Charger les modèles CLIP/CLIPSeg/U-Net
3. Appeler les fonctions après le scraping pour analyser les images
4. Trier les résultats par score de similarité

---

## 🛒 AliExpress - Fonctionnalités

### ✅ Fonctionnalités Existantes (Conservées)

- Recherche par image native AliExpress
- Calcul de similarité CLIP ViT-L-14 (Laion2B)
- Téléchargement automatique des images
- Tri par score de similarité
- Export Excel personnalisable
- Sauvegarde dans `RESULTATS/aliexpress/`

### 🔧 Modifications Apportées

- **Organisation des résultats** : `RESULTATS/` → `RESULTATS/aliexpress/`
- **Aucune modification fonctionnelle** : Le code reste identique

---

## 🧹 Nettoyage Effectué

Les fichiers de déploiement obsolètes ont été supprimés:

### ❌ Fichiers Supprimés

- `build_*.py` (13 fichiers PyArmor, PyInstaller, Nuitka, etc.)
- `Dockerfile`, `docker-compose.yml`
- `*.spec` (PyInstaller)
- `build_docker.sh`, `save_docker.sh`, `run_docker.sh`
- `setup_pyarmor_python310.bat`
- `GUIDE_PYTHON310_PYARMOR.md`, `README_DOCKER.md`, `GUIDE_DOCKER.md`

### ✅ Fichiers Conservés

- `requirements.txt`
- `Lancer_Application.bat` / `.sh`
- `README_CLIENT.txt`
- Tous les fichiers source (`src/`, `app.py`, etc.)

---

## 📊 Organisation des Résultats

Chaque recherche crée automatiquement un dossier horodaté:

### AliExpress
```
RESULTATS/aliexpress/recherche_2025-11-13_19-45-23/
├── images/                    # Images téléchargées
├── image_metadata.json        # Métadonnées d'images
└── product_data.json          # Données de produits
```

### MercadoLibre
```
RESULTATS/mercadolibre/recherche_2025-11-13_19-50-15/
├── images/                    # Images téléchargées
│   ├── product_0000.jpg
│   ├── product_0001.jpg
│   └── ...
└── listings.json              # Données de scraping
```

---

## 🎯 Prochaines Étapes (Optionnel)

### Pour MercadoLibre

1. **Intégrer l'analyse CLIP complète**
   - Charger les modèles dans la page Streamlit
   - Calculer les embeddings pour chaque image scrapée
   - Comparer avec l'image de référence
   - Trier par score de similarité

2. **Ajouter la segmentation avancée**
   - CLIPSeg pour extraire les zones pertinentes
   - U-Net pour détecter les détails spécifiques (fermoirs, logos)
   - Vision Transformer pour vérifier les catégories

3. **Améliorer le scraping**
   - Récupérer TOUTES les images de chaque annonce (pas seulement la première)
   - Ajouter plus de métadonnées (vendeur, localisation, etc.)

### Pour AliExpress

- Ajouter la segmentation CLIPSeg (optionnel, si besoin d'analyses plus fines)

---

## 📝 Notes Techniques

### Technologies Utilisées

- **Streamlit** : Interface web multi-pages
- **BeautifulSoup** : Scraping HTML pour MercadoLibre
- **CLIP (OpenAI)** : Vision-Language Model pour similarité
- **CLIPSeg** : Segmentation sémantique guidée par texte
- **U-Net** : Segmentation de détails spécifiques
- **Vision Transformer (ViT)** : Classification de catégories
- **Pandas + openpyxl** : Export Excel

### Dépendances Principales

```txt
streamlit
requests
beautifulsoup4
Pillow
torch
open-clip-torch
transformers
scikit-image
scipy
opencv-python
segmentation-models-pytorch
timm
pandas
openpyxl
```

---

## 🐛 Dépannage

### Problème : "No module named 'src'"

**Solution:** Assurez-vous d'exécuter l'application depuis le dossier racine:
```bash
cd /chemin/vers/Web-Scrapping
streamlit run app.py
```

### Problème : Erreur lors du scraping MercadoLibre

**Solution:** Vérifiez votre connexion Internet et que le pays sélectionné est accessible.

### Problème : CLIP/CLIPSeg non disponible

**Solution:** Les modèles CLIP avancés nécessitent des dépendances supplémentaires.
Installez-les avec:
```bash
pip install torch open-clip-torch transformers segmentation-models-pytorch timm
```

---

## 📧 Contact & Support

Pour toute question ou amélioration, référez-vous à la documentation Streamlit :
https://docs.streamlit.io/

---

**Version:** 1.0
**Date:** 2025-11-13
**Auteur:** Claude Code Integration

✅ **Prêt pour utilisation et développement!**
