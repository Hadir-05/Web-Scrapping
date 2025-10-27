# 🔍 Guide: Moteur de Recherche par Image

## Description

Le moteur de recherche par image vous permet de:
1. ✅ Prendre une photo d'un produit authentique
2. ✅ Scraper automatiquement AliExpress/DHgate
3. ✅ Comparer votre image avec TOUTES les annonces trouvées
4. ✅ Obtenir le TOP 3/5/10 des annonces les plus similaires
5. ✅ Détecter les contrefaçons potentielles

## Installation

```bash
cd ~/Web-Scrapping/counterfeit_detection
pip install -r requirements.txt
```

## Utilisation

### Syntaxe de base

```bash
python search_by_image.py <image_reference> "<recherche>" --site <aliexpress|dhgate> --top <N>
```

### Exemples

**1. Recherche simple (TOP 5 sur AliExpress)**

```bash
python search_by_image.py ~/Downloads/hermes_birkin.jpg "Hermès Birkin"
```

**2. Recherche approfondie (TOP 10 parmi 50 annonces)**

```bash
python search_by_image.py ~/Downloads/rolex.jpg "Rolex Submariner" --max 50 --top 10
```

**3. Recherche sur DHgate**

```bash
python search_by_image.py ~/Downloads/louis_vuitton.jpg "Louis Vuitton bag" --site dhgate --top 5
```

**4. Recherche rapide (10 annonces seulement)**

```bash
python search_by_image.py ~/Downloads/product.jpg "luxury handbag" --max 10 --top 3
```

## Paramètres

| Paramètre | Description | Par défaut |
|-----------|-------------|------------|
| `image` | Chemin vers votre image de référence | **Requis** |
| `query` | Terme de recherche (entre guillemets) | **Requis** |
| `--site` | Site à scraper (`aliexpress` ou `dhgate`) | `aliexpress` |
| `--max` | Nombre d'annonces à scraper | `20` |
| `--top` | Nombre de résultats à afficher | `5` |
| `--device` | Device AI (`cpu` ou `cuda`) | `cpu` |

## Interprétation des résultats

Le script affiche le TOP N des annonces avec:

### Score de similarité

- 🔴 **≥85%** - TRÈS SUSPECT (copie quasi-identique)
- 🟠 **70-85%** - SUSPECT (forte ressemblance)
- 🟡 **55-70%** - MODÉRÉMENT SUSPECT (quelques similitudes)
- 🟢 **<55%** - PEU SUSPECT (peu de ressemblance)

### Informations affichées

Pour chaque annonce dans le TOP N:
- Score de similarité (%)
- Titre de l'annonce
- Prix
- URL
- Image
- Vendeur
- Note

### Statistiques globales

- Similarité moyenne
- Similarité maximale
- Similarité minimale
- Nombre d'annonces à haut risque

## Workflow complet

```bash
# 1. Préparez votre image de référence
# Téléchargez une photo du produit authentique

# 2. Lancez la recherche
python search_by_image.py ~/Downloads/authentic_product.jpg "luxury brand product" --max 30 --top 5

# 3. Attendez les résultats
# Le script va:
#   - Charger le modèle AI ResNet50 (~100MB première fois)
#   - Scraper le site
#   - Calculer la similarité pour chaque annonce
#   - Afficher le TOP 5

# 4. Analysez les résultats
# Vérifiez les annonces avec score >85% (très suspectes)
```

## Exemple de sortie

```
🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️

   MOTEUR DE RECHERCHE PAR IMAGE
   Détection de contrefaçons par similarité d'images

🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️ 🛡️

📸 Image de référence: /home/user/hermes_birkin.jpg
🔍 Recherche: 'Hermès Birkin' sur ALIEXPRESS
📊 Scraping jusqu'à 20 annonces...
✅ 18 annonces trouvées
🧠 Calcul de la similarité avec l'image de référence...

   [1/18] 89.2% - Hermès Birkin Style Handbag Luxury Designer...
   [2/18] 76.5% - Classic Leather Bag Fashion Women Handbag...
   [3/18] 68.3% - Designer Inspired Tote Bag High Quality...
   ...

================================================================================
🏆 TOP 5 ANNONCES LES PLUS SIMILAIRES
================================================================================

🔴 #1 - SIMILARITÉ: 89.2% (TRÈS SUSPECT)
--------------------------------------------------------------------------------
📦 Titre: Hermès Birkin Style Handbag Luxury Designer...
💰 Prix: $299.99
🔗 URL: https://aliexpress.com/item/...
📸 Image: https://ae01.alicdn.com/...

🟠 #2 - SIMILARITÉ: 76.5% (SUSPECT)
--------------------------------------------------------------------------------
📦 Titre: Classic Leather Bag Fashion Women Handbag...
💰 Prix: $189.50
🔗 URL: https://aliexpress.com/item/...
📸 Image: https://ae01.alicdn.com/...

...

================================================================================

📊 STATISTIQUES:
   └─ Similarité moyenne: 65.4%
   └─ Similarité maximale: 89.2%
   └─ Similarité minimale: 42.1%

⚠️  ALERTE: 1 annonce(s) à TRÈS HAUTE SIMILARITÉ détectée(s)!
⚠️  2 annonce(s) à HAUTE SIMILARITÉ détectée(s)

✅ Recherche terminée!
```

## Cas d'utilisation

### 1. Surveillance de marque

```bash
# Surveiller les contrefaçons d'un produit spécifique
python search_by_image.py products/birkin30_orange.jpg "Hermès Birkin 30" --max 100 --top 20
```

### 2. Analyse concurrentielle

```bash
# Voir qui vend des produits similaires
python search_by_image.py my_product.jpg "leather handbag" --site dhgate
```

### 3. Détection rapide

```bash
# Check rapide (10 annonces)
python search_by_image.py product.jpg "luxury bag" --max 10 --top 3
```

## Performance

- **Première utilisation**: ~2-3 minutes (téléchargement du modèle ResNet50)
- **Utilisations suivantes**:
  - ~5-10 secondes pour 20 annonces
  - ~20-30 secondes pour 50 annonces
  - ~1 minute pour 100 annonces

## Limitations

1. **Scraping**: Les sites peuvent bloquer après trop de requêtes
2. **Images**: Nécessite que les annonces aient des images
3. **Performance**: CPU peut être lent pour beaucoup d'annonces (utilisez `--device cuda` si GPU disponible)
4. **Connexion**: Nécessite une connexion internet

## Troubleshooting

### Le modèle ne se charge pas

```bash
# Vérifier l'installation de PyTorch
python -c "import torch; print(torch.__version__)"

# Réinstaller si nécessaire
pip install torch==1.13.1 torchvision==0.14.1
```

### Erreur de scraping

```bash
# Tester avec moins de résultats
python search_by_image.py image.jpg "query" --max 5

# Essayer l'autre site
python search_by_image.py image.jpg "query" --site dhgate
```

### Image introuvable

```bash
# Vérifier le chemin (utiliser chemin absolu)
python search_by_image.py ~/Downloads/image.jpg "query"

# Ou chemin relatif depuis counterfeit_detection/
python search_by_image.py ../images/product.jpg "query"
```

## Prochaines étapes

Après avoir identifié les contrefaçons, vous pouvez:

1. **Sauvegarder les résultats** dans la base de données
2. **Voir le dashboard** pour visualiser: `streamlit run dashboard.py`
3. **Lancer des scans automatiques** via `demo.py`
4. **Créer des rapports** d'analyse

## Support

Pour plus d'informations:
- `python search_by_image.py --help`
- Voir `IMAGE_SIMILARITY_GUIDE.md` pour détails techniques du modèle
- Voir `README.md` pour architecture globale
