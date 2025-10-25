# Guide d'Installation

## Prérequis

### Logiciels Requis
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optionnel)
- Redis (pour production)

### Modèles PyTorch
Vous devez avoir vos modèles `.pth` prêts :
- Modèle de recherche par mots-clés
- Modèle de recherche par image

---

## Installation Locale

### 1. Cloner le Projet

```bash
git clone <repository-url>
cd Web-Scrapping
```

### 2. Placer les Modèles

```bash
# Créer le dossier models s'il n'existe pas
mkdir -p models

# Copier vos modèles
cp /path/to/your/keyword_model.pth models/keyword_search.pth
cp /path/to/your/image_model.pth models/image_similarity.pth
```

### 3. Configuration Environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos paramètres
nano .env
```

---

## Option 1 : Streamlit MVP (Démo Rapide)

### Installation

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
cd streamlit_app
streamlit run app.py
```

L'application sera accessible sur : http://localhost:8501

---

## Option 2 : FastAPI + React (Production)

### Backend FastAPI

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
cd backend
pip install -r requirements.txt

# Lancer Redis (dans un autre terminal)
docker run -d -p 6379:6379 redis:alpine

# Lancer le backend
cd app
uvicorn main:app --reload --port 8000
```

Backend accessible sur : http://localhost:8000
Documentation API : http://localhost:8000/docs

### Frontend React

```bash
# Installer les dépendances
cd frontend
npm install

# Lancer le dev server
npm start
```

Frontend accessible sur : http://localhost:3000

---

## Option 3 : Docker (Recommandé pour Production)

### Lancement Complet

```bash
# Depuis la racine du projet
docker-compose -f docker/docker-compose.yml up -d --build
```

### Services Disponibles

- **Streamlit MVP** : http://localhost:8501
- **Backend API** : http://localhost:8000
- **Frontend React** : http://localhost:3000
- **Redis** : localhost:6379

### Commandes Docker Utiles

```bash
# Voir les logs
docker-compose -f docker/docker-compose.yml logs -f

# Arrêter les services
docker-compose -f docker/docker-compose.yml down

# Redémarrer un service
docker-compose -f docker/docker-compose.yml restart backend

# Voir le statut
docker-compose -f docker/docker-compose.yml ps
```

---

## Vérification de l'Installation

### Test Backend

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test recherche keyword
curl -X POST http://localhost:8000/api/v1/search/keyword \
  -H "Content-Type: application/json" \
  -d '{"query": "sac à main", "top_k": 5}'
```

### Test Frontend

Ouvrir http://localhost:3000 dans le navigateur et tester :
1. Recherche par mots-clés
2. Upload d'image pour recherche

### Test Streamlit

Ouvrir http://localhost:8501 et vérifier que les modèles se chargent correctement.

---

## Résolution de Problèmes

### Modèles Non Trouvés

```bash
# Vérifier que les modèles existent
ls -lh models/

# Permissions
chmod 644 models/*.pth
```

### Redis Non Disponible

Le backend fonctionnera sans Redis (cache local uniquement).

Pour installer Redis localement :

```bash
# Linux
sudo apt-get install redis-server
sudo systemctl start redis

# Mac
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### Port Déjà Utilisé

Modifier les ports dans `.env` ou `docker-compose.yml`

```bash
# Vérifier les ports utilisés
lsof -i :8000
lsof -i :3000
lsof -i :8501
```

---

## Configuration GPU (Optionnel)

Si vous avez un GPU NVIDIA :

```bash
# Modifier .env
DEVICE=cuda

# Pour Docker, utiliser nvidia-docker
# Modifier docker-compose.yml pour ajouter :
# services:
#   backend:
#     runtime: nvidia
#     environment:
#       - DEVICE=cuda
```

---

## Prochaines Étapes

Une fois installé :
1. Consultez [USAGE.md](./USAGE.md) pour utiliser l'application
2. Consultez [API.md](./API.md) pour l'API documentation
3. Consultez [MODELS.md](./MODELS.md) pour adapter vos modèles
