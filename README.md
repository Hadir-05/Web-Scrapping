# Luxury AI Search & Anti-Counterfeit Detection Platform

Plateforme complète alimentée par l'IA pour la recherche de produits de luxe et la détection automatique de contrefaçons.

## 🎯 Vue d'Ensemble

Ce projet propose **TROIS solutions principales** :

### 🛡️ **NOUVEAU : Système de Détection de Contrefaçons**
**Le système le plus important et le plus avancé !**
- **Web Scraping** automatique des sites e-commerce (AliExpress, DHgate, Wish, Temu...)
- **Détection AI** multi-critères des contrefaçons
- **Dashboard de monitoring** en temps réel
- **Alertes automatiques** et rapports
- **Base de données** complète des détections
- 📖 **[Documentation complète](counterfeit_detection/README.md)**

---

## 🏗️ Architecture

Le projet propose **trois systèmes** :

### 1. **🛡️ Système Anti-Contrefaçon** (Principal - NOUVEAU!)
- **Scraping multi-sites** : AliExpress, DHgate, Wish, Temu, etc.
- **Détection IA** : Similarité d'images + matching mots-clés + analyse de prix
- **Dashboard Streamlit** avancé avec analytics
- **Base de données SQLite** pour stocker les détections
- **Alertes en temps réel** (email, webhooks)
- **Rapports automatisés** et exports
- 📂 Dossier: `counterfeit_detection/`

### 2. **Streamlit MVP** (Recherche de Produits)
- Interface tout-en-un pour validation rapide
- Cache natif des modèles PyTorch
- Parfait pour présentation client
- 📂 Dossier: `streamlit_app/`

### 3. **FastAPI + React** (Recherche Production)
- Backend API scalable avec Redis
- Frontend moderne et élégant
- Architecture microservices
- 📂 Dossiers: `backend/` + `frontend/`

---

## 📁 Structure du Projet

```
Web-Scrapping/
├── counterfeit_detection/  # 🛡️ SYSTÈME ANTI-CONTREFAÇON (PRINCIPAL)
│   ├── database/
│   │   ├── models.py           # Schéma BDD (SQLAlchemy)
│   │   └── counterfeit_detection.db  # Base de données
│   ├── scrapers/
│   │   ├── base_scraper.py     # Classe de base
│   │   ├── aliexpress_scraper.py
│   │   └── dhgate_scraper.py
│   ├── detectors/
│   │   └── counterfeit_detector.py  # Moteur de détection AI
│   ├── dashboard.py            # Dashboard Streamlit avancé
│   ├── demo.py                 # Script de démonstration
│   ├── requirements.txt
│   └── README.md               # Documentation complète
│
├── streamlit_app/          # Application Streamlit MVP (Recherche)
│   ├── app.py             # Interface principale
│   ├── app_demo.py        # Version démo sans PyTorch
│   ├── models/            # Gestionnaire de modèles
│   └── utils/             # Utilitaires
│
├── backend/               # API FastAPI (Recherche)
│   ├── app/
│   │   ├── main.py       # Point d'entrée FastAPI
│   │   ├── models/       # Gestion modèles PyTorch
│   │   ├── api/          # Routes API
│   │   ├── core/         # Configuration
│   │   └── schemas/      # Modèles Pydantic
│   └── requirements.txt
│
├── frontend/              # Application React (Recherche)
│   ├── src/
│   │   ├── components/   # Composants React
│   │   ├── pages/        # Pages
│   │   ├── services/     # API clients
│   │   └── styles/       # TailwindCSS
│   └── package.json
│
├── models/                # Modèles PyTorch (.pth)
│   ├── keyword_search.pth
│   └── image_similarity.pth
│
├── docker/                # Configurations Docker
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.streamlit
│
└── docs/                  # Documentation
```

---

## 🚀 Quick Start

### 🛡️ Option 1: Système Anti-Contrefaçon (RECOMMANDÉ)

```bash
# Installer les dépendances
cd counterfeit_detection
pip install -r requirements.txt

# Lancer le dashboard
streamlit run dashboard.py

# Ou tester la démo
python demo.py
```

**Accès:** http://localhost:8501

**Fonctionnalités:**
1. **Nouveau Scan** : Rechercher des contrefaçons sur AliExpress, DHgate, etc.
2. **Dashboard** : Visualiser les détections en temps réel
3. **Analytics** : Rapports et tendances
4. **Configuration** : Gérer les marques surveillées

📖 **Documentation complète:** [counterfeit_detection/README.md](counterfeit_detection/README.md)

---

### Option 2: Streamlit MVP (Recherche)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Placer vos modèles .pth dans models/
cp your_keyword_model.pth models/keyword_search.pth
cp your_image_model.pth models/image_similarity.pth

# Lancer Streamlit
cd streamlit_app
streamlit run app.py
```

### Option 3: FastAPI + React (Production)

```bash
# Avec Docker (Recommandé)
docker-compose up -d

# Ou manuellement:

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start

# Redis
docker run -d -p 6379:6379 redis:alpine
```

---

## 🎯 Fonctionnalités

### Recherche par Mots-Clés
- Recherche sémantique basée sur l'IA
- Correspondance intelligente de produits
- Résultats classés par pertinence

### Recherche par Image
- Upload d'image ou URL
- Recherche de produits similaires
- Scoring de similarité

### Cache Intelligent
- **Streamlit**: `@st.cache_resource` pour modèles
- **FastAPI**: Redis pour cache persistant
- Modèles chargés une seule fois

---

## 🛠️ Configuration

### Variables d'Environnement

Créer `.env` à la racine :

```env
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Models
KEYWORD_MODEL_PATH=./models/keyword_search.pth
IMAGE_MODEL_PATH=./models/image_similarity.pth

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

---

## 📦 Modèles PyTorch (.pth)

### Format Attendu

Vos modèles doivent être compatibles avec :

```python
# Chargement
model = torch.load('model.pth', map_location=device)
model.eval()

# Ou avec state_dict
model = YourModelClass()
model.load_state_dict(torch.load('model.pth'))
```

### Placement
```
models/
├── keyword_search.pth      # Modèle de recherche textuelle
└── image_similarity.pth    # Modèle de similarité d'images
```

---

## 🎨 Design Luxe

Le frontend React utilise :
- **TailwindCSS** pour design épuré
- **Palette élégante** : Or, noir, blanc
- **Animations fluides**
- **Responsive design**

---

## 📊 Performance

### Cache des Modèles
- **Streamlit**: Modèles gardés en mémoire session
- **FastAPI**: Modèles en Redis, persistants
- **Temps de chargement**: ~2-3s au premier appel, <100ms ensuite

### Scalabilité
- FastAPI supporte async/await
- Peut gérer 1000+ requêtes/seconde
- Horizontal scaling avec Kubernetes

---

## 🔒 Sécurité

- Validation des uploads (images uniquement)
- Rate limiting sur API
- CORS configuré
- Variables sensibles dans .env

---

## 📝 API Documentation

Une fois le backend lancé, accéder à :
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🐳 Déploiement Docker

```bash
# Build et lancer tous les services
docker-compose up -d --build

# Services disponibles:
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:8000
# - React: http://localhost:3000
# - Redis: localhost:6379
```

---

## 🧪 Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

---

## 📚 Technologies Utilisées

### Backend
- FastAPI 0.109+
- PyTorch 2.1+
- Redis
- Uvicorn

### Frontend
- React 18
- TypeScript
- TailwindCSS
- Axios

### MVP
- Streamlit 1.31+

---

## 🤝 Contribution

Ce projet est développé pour une entreprise de luxe. Contactez l'équipe pour toute modification.

---

## 📄 License

Propriétaire - Tous droits réservés

---

## 👥 Support

Pour toute question, contacter l'équipe technique.