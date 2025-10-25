# 🛡️ Anti-Counterfeit Detection System

Système complet de détection automatique de contrefaçons de produits de luxe sur les sites e-commerce.

---

## 🎯 Vue d'Ensemble

Ce système permet de :
- **Scraper** automatiquement les sites e-commerce (AliExpress, DHgate, Wish, etc.)
- **Détecter** les contrefaçons en utilisant l'IA (similarité d'images + matching de mots-clés)
- **Analyser** les prix suspects
- **Alerter** en temps réel sur les détections
- **Visualiser** les données dans un dashboard interactif

---

## 📁 Architecture

```
counterfeit_detection/
├── database/
│   ├── models.py                 # Schéma BDD (SQLAlchemy)
│   └── counterfeit_detection.db  # Base de données SQLite
│
├── scrapers/
│   ├── base_scraper.py          # Classe de base
│   ├── aliexpress_scraper.py    # Scraper AliExpress
│   └── dhgate_scraper.py        # Scraper DHgate
│
├── detectors/
│   └── counterfeit_detector.py  # Moteur de détection AI
│
├── alerts/
│   └── alert_manager.py         # Système d'alertes
│
├── dashboard.py                  # Dashboard Streamlit
├── requirements.txt              # Dépendances
└── README.md                     # Ce fichier
```

---

## 🚀 Installation

### 1. Installer les Dépendances

```bash
cd counterfeit_detection
pip install -r requirements.txt
```

### 2. Initialiser la Base de Données

La base de données est créée automatiquement au premier lancement.

```python
from database.models import DatabaseManager

db = DatabaseManager()
```

### 3. (Optionnel) Ajouter vos Modèles PyTorch

Si vous avez des modèles .pth pour la similarité d'images :

```bash
# Copier vos modèles
cp your_image_model.pth ../models/image_similarity.pth
```

---

## 📊 Utilisation du Dashboard

### Lancer le Dashboard

```bash
cd counterfeit_detection
streamlit run dashboard.py
```

Accès : **http://localhost:8501**

### Fonctionnalités du Dashboard

#### 1. **📊 Dashboard** (Page d'accueil)
- Vue d'ensemble des statistiques
- Graphiques de détections par site
- Distribution des risques
- Détections récentes à haut risque

#### 2. **🔍 New Scan** (Nouveau Scan)
- Sélectionner un site (AliExpress, DHgate, etc.)
- Entrer une requête de recherche (ex: "Louis Vuitton bag")
- Définir le nombre de pages à scraper
- Lancer le scan automatique

**Exemple de recherche :**
```
Site: AliExpress
Query: Gucci handbag
Max Pages: 3
```

Le système va :
1. Scraper AliExpress
2. Analyser chaque produit trouvé
3. Détecter les marques de luxe
4. Calculer les scores de risque
5. Sauvegarder les contrefaçons potentielles

#### 3. **📋 Detections List** (Liste des Détections)
- Voir toutes les contrefaçons détectées
- Filtrer par site, risque, statut
- Exporter les données
- Marquer comme confirmé/faux positif

#### 4. **⚙️ Configuration**
- Gérer les marques à surveiller
- Configurer les scrapers
- Paramétrer les alertes (email, webhook)

#### 5. **📈 Analytics** (Analyses)
- Timeline des détections
- Marques les plus ciblées
- Distribution des prix
- Rapports personnalisés

---

## 🔍 Utilisation Programmatique

### Exemple : Scanner AliExpress

```python
from scrapers.aliexpress_scraper import AliExpressScraper
from detectors.counterfeit_detector import CounterfeitDetector
from database.models import DatabaseManager

# Initialiser
scraper = AliExpressScraper()
detector = CounterfeitDetector()
db = DatabaseManager()

# Scraper
products = scraper.search("Louis Vuitton bag", max_pages=3)
print(f"Found {len(products)} products")

# Détecter les contrefaçons
for product in products:
    result = detector.detect_counterfeit(product, authentic_products=[])

    if result['overall_risk_score'] > 0.7:
        print(f"⚠️ Counterfeit detected!")
        print(f"  Title: {product['title']}")
        print(f"  Risk: {result['overall_risk_score']:.1%}")
        print(f"  Brands: {result['detected_brands']}")

        # Sauvegarder
        db.add_counterfeit(
            detection_id=f"AliExpress_{hash(product['url'])}",
            source_site="AliExpress",
            source_url=product['url'],
            title=product['title'],
            price=product.get('price'),
            image_urls=product.get('image_urls', []),
            overall_risk_score=result['overall_risk_score'],
            detected_brands=result['detected_brands'],
            confidence_level=result['confidence_level']
        )
```

### Exemple : Recherche Multi-Sites

```python
from scrapers.aliexpress_scraper import AliExpressScraper
from scrapers.dhgate_scraper import DHgateScraper

query = "Rolex watch"

scrapers = {
    'AliExpress': AliExpressScraper(),
    'DHgate': DHgateScraper()
}

all_products = []

for site_name, scraper in scrapers.items():
    print(f"Scanning {site_name}...")
    products = scraper.search(query, max_pages=2)
    all_products.extend(products)

print(f"Total products found: {len(all_products)}")
```

---

## 🤖 Système de Détection

### Critères de Détection

Le système utilise **4 critères principaux** :

#### 1. **Détection de Marques** (30%)
- Détecte les marques de luxe dans le titre/description
- Gère les variantes et fautes d'orthographe
- Exemple : "LV", "L.V", "Louis V" → "Louis Vuitton"

#### 2. **Similarité d'Images** (30%)
- Compare avec les images des produits authentiques
- Utilise le modèle PyTorch fourni
- Score de 0 (différent) à 1 (identique)

#### 3. **Analyse de Prix** (25%)
- Détecte les prix anormalement bas
- Exemple : Sac LV à $50 au lieu de $2000 → Score élevé

#### 4. **Mots Suspects** (15%)
- Détecte : "replica", "copy", "AAA", "1:1", "mirror", etc.

### Niveaux de Risque

| Score | Niveau | Action |
|-------|--------|--------|
| 0.85 - 1.0 | 🔴 CRITICAL | Alerte immédiate |
| 0.70 - 0.84 | 🟠 HIGH | Revue prioritaire |
| 0.50 - 0.69 | 🟡 MEDIUM | Revue standard |
| 0.0 - 0.49 | 🟢 LOW | Monitoring |

---

## 📧 Système d'Alertes

### Configurer les Alertes Email

```python
from alerts.alert_manager import AlertManager

alert_mgr = AlertManager(
    email_enabled=True,
    email_recipients=['security@company.com'],
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    smtp_username='alerts@company.com',
    smtp_password='your_password'
)

# Envoyer une alerte
alert_mgr.send_alert(
    counterfeit_data={
        'title': 'Fake Louis Vuitton Bag',
        'risk_score': 0.95,
        'url': 'https://...'
    },
    alert_level='CRITICAL'
)
```

### Webhooks

```python
alert_mgr = AlertManager(
    webhook_enabled=True,
    webhook_url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
)
```

---

## 📅 Planification Automatique

### Scans Automatiques Quotidiens

Créer un script `scheduled_scan.py` :

```python
import schedule
import time
from scrapers.aliexpress_scraper import AliExpressScraper
from detectors.counterfeit_detector import CounterfeitDetector

def daily_scan():
    """Scan quotidien"""
    brands = ["Louis Vuitton", "Gucci", "Rolex", "Hermès"]

    scraper = AliExpressScraper()
    detector = CounterfeitDetector()

    for brand in brands:
        print(f"Scanning for {brand}...")
        products = scraper.search(brand, max_pages=5)

        # Détection...
        # (code de détection)

    print("Daily scan complete!")

# Planifier tous les jours à 2h du matin
schedule.every().day.at("02:00").do(daily_scan)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Lancer en arrière-plan :

```bash
nohup python scheduled_scan.py &
```

---

## 🔧 Personnalisation

### Ajouter un Nouveau Scraper

Créer `scrapers/wish_scraper.py` :

```python
from scrapers.base_scraper import BaseScraper

class WishScraper(BaseScraper):
    @property
    def base_url(self):
        return "https://www.wish.com"

    @property
    def site_name(self):
        return "Wish"

    def search(self, query, max_pages=5):
        # Implémenter la logique de scraping
        pass

    def get_product_details(self, product_url):
        # Implémenter la récupération de détails
        pass
```

### Ajouter des Marques

```python
detector = CounterfeitDetector()

# Ajouter de nouvelles marques
detector.luxury_brands.extend([
    "Omega",
    "Tag Heuer",
    "Patek Philippe"
])

# Ajouter des variantes
detector.brand_variants["Patek Philippe"] = [
    "Patek",
    "PP",
    "Patek P"
]
```

---

## 📊 Base de Données

### Structure des Tables

#### `authentic_products`
Produits authentiques de référence

#### `counterfeit_products`
Contrefaçons détectées

#### `counterfeit_actions`
Actions prises (alertes, takedowns, etc.)

#### `scraping_jobs`
Historique des scans

#### `brand_keywords`
Mots-clés de marques

### Requêtes Utiles

```python
from database.models import DatabaseManager

db = DatabaseManager()

# Statistiques
stats = db.get_statistics()
print(f"Total counterfeits: {stats['total_counterfeits']}")

# Récupérer les contrefaçons à haut risque
high_risk = db.get_counterfeits(filters={'min_risk': 0.85}, limit=50)

# Par site
aliexpress_counterfeits = db.get_counterfeits(filters={'site': 'AliExpress'})
```

---

## 🚨 Limites et Considérations

### Légales
- ⚠️ **Respectez les ToS** des sites scrapés
- ⚠️ **Rate limiting** : Ne pas surcharger les serveurs
- ⚠️ **RGPD** : Gestion des données personnelles

### Techniques
- Les sélecteurs CSS peuvent changer (sites dynamiques)
- Certains sites utilisent du JavaScript (considérer Selenium)
- Captchas peuvent bloquer le scraping
- Proxies recommandés pour gros volumes

### Recommandations
1. **Utiliser des proxies** pour éviter les bans IP
2. **Respecter les délais** entre requêtes (1-3 secondes)
3. **Sauvegarder régulièrement** la base de données
4. **Monitorer les logs** pour détecter les erreurs
5. **Mettre à jour** les scrapers régulièrement

---

## 📈 Métriques de Performance

### KPIs à Suivre
- **Taux de détection** : % de contrefaçons détectées vs total de produits
- **Précision** : % de vrais positifs
- **Faux positifs** : Produits légitimes détectés comme contrefaçons
- **Temps de scan** : Durée moyenne par page
- **Couverture** : Nombre de sites/pages scannés

---

## 🛠️ Maintenance

### Logs

Les logs sont dans `logs/counterfeit_detection.log`

```bash
tail -f logs/counterfeit_detection.log
```

### Backup Base de Données

```bash
# Backup
cp database/counterfeit_detection.db backups/db_$(date +%Y%m%d).db

# Restauration
cp backups/db_20240101.db database/counterfeit_detection.db
```

---

## 📞 Support

Pour toute question :
- Email : security@company.com
- Documentation : Voir `/docs`

---

## 📄 License

Propriétaire - Tous droits réservés
