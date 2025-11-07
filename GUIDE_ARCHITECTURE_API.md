# 🏆 Architecture API (Hybride) - Maximum Sécurité

## 📋 Concept

Au lieu de donner tout le code au client, vous séparez l'application en **2 parties** :

```
┌─────────────────────────────────────────────────────────┐
│                    ARCHITECTURE                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CLIENT (chez le client)          SERVEUR (chez vous)   │
│  ┌──────────────────┐              ┌──────────────────┐ │
│  │  Interface UI    │              │  Logique Métier  │ │
│  │  - Formulaires   │◄────API─────►│  - Scraping      │ │
│  │  - Affichage     │   (HTTPS)    │  - CLIP          │ │
│  │  - Boutons       │              │  - Traitement    │ │
│  └──────────────────┘              └──────────────────┘ │
│                                                          │
│  PAS de code sensible              Code PROTÉGÉ         │
│  Juste l'interface                 sur VOTRE serveur    │
└─────────────────────────────────────────────────────────┘
```

**Avantages** :
- ✅ Le client n'a JAMAIS accès au code de scraping
- ✅ Vous contrôlez l'utilisation (quotas, licences)
- ✅ Mises à jour faciles (juste le serveur)
- ✅ Vous pouvez facturer à l'usage
- ✅ Le client ne peut pas revendre votre code

---

## 🏗️ Architecture Détaillée

### Structure du Projet

```
projet/
├── backend/                    # SERVEUR (chez vous)
│   ├── app.py                 # API Flask/FastAPI
│   ├── src/
│   │   ├── aliexpress_scraper.py
│   │   └── image_similarity.py
│   ├── requirements.txt
│   └── .env                   # Clés API, secrets
│
├── frontend/                   # CLIENT (chez le client)
│   ├── app.py                 # Interface Streamlit simple
│   ├── api_client.py          # Appels vers votre API
│   └── requirements.txt       # Juste streamlit, requests
│
└── docs/
    ├── API_DOCUMENTATION.md
    └── CLIENT_GUIDE.md
```

---

## 🔧 Implémentation Étape par Étape

### Partie 1 : Backend (Serveur API) - CHEZ VOUS

#### 1.1 - Créer l'API avec FastAPI

**Fichier : `backend/app.py`**

```python
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import hashlib
import datetime
from src.aliexpress_scraper import AliExpressScraper
from src.image_similarity import ImageSimilarity

app = FastAPI(title="AliExpress Scraper API", version="1.0.0")

# CORS pour permettre les requêtes du client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: liste d'IPs autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de données simple (en production: PostgreSQL/MySQL)
LICENSES = {
    "lic_abc123": {
        "client": "Entreprise XYZ",
        "expiry": "2025-12-31",
        "quota_monthly": 1000,
        "used_this_month": 0
    }
}

# ============================================
# AUTHENTIFICATION
# ============================================

def verify_license(license_key: str = Header(..., alias="X-License-Key")):
    """Vérifier la licence du client"""
    if license_key not in LICENSES:
        raise HTTPException(status_code=401, detail="Licence invalide")

    license_data = LICENSES[license_key]

    # Vérifier expiration
    expiry = datetime.datetime.strptime(license_data["expiry"], "%Y-%m-%d")
    if datetime.datetime.now() > expiry:
        raise HTTPException(status_code=401, detail="Licence expirée")

    # Vérifier quota
    if license_data["used_this_month"] >= license_data["quota_monthly"]:
        raise HTTPException(status_code=429, detail="Quota mensuel dépassé")

    return license_data

# ============================================
# MODÈLES DE DONNÉES
# ============================================

class SearchRequest(BaseModel):
    search_url: str
    reference_image_url: str
    max_results: int = 20

class ProductResult(BaseModel):
    title: str
    price: str
    url: str
    image_url: str
    similarity_score: float

class SearchResponse(BaseModel):
    results: List[ProductResult]
    total_found: int
    execution_time: float

# ============================================
# ENDPOINTS API
# ============================================

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "name": "AliExpress Scraper API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    """Vérifier que l'API fonctionne"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    license_data: dict = Depends(verify_license)
):
    """
    Rechercher des produits similaires sur AliExpress

    Nécessite une clé de licence valide dans le header X-License-Key
    """
    try:
        start_time = datetime.datetime.now()

        # Initialiser le scraper
        scraper = AliExpressScraper()
        similarity = ImageSimilarity()

        # Faire le scraping
        results = await scraper.search(
            url=request.search_url,
            reference_image=request.reference_image_url,
            max_results=request.max_results
        )

        # Calculer la similarité
        scored_results = similarity.rank_by_similarity(
            results,
            request.reference_image_url
        )

        # Incrémenter le compteur d'utilisation
        license_key = request.headers.get("X-License-Key")
        LICENSES[license_key]["used_this_month"] += 1

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        return SearchResponse(
            results=scored_results,
            total_found=len(scored_results),
            execution_time=execution_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du scraping: {str(e)}")

@app.get("/api/v1/license/status")
def get_license_status(license_data: dict = Depends(verify_license)):
    """Obtenir le statut de la licence"""
    return {
        "client": license_data["client"],
        "expiry": license_data["expiry"],
        "quota_remaining": license_data["quota_monthly"] - license_data["used_this_month"],
        "quota_total": license_data["quota_monthly"]
    }

# ============================================
# GESTION DES ERREURS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 1.2 - Déployer le Backend

**Option A : Serveur Local (Pour tests)**
```bash
# Installer FastAPI
pip install fastapi uvicorn

# Lancer le serveur
uvicorn app:app --host 0.0.0.0 --port 8000

# API accessible sur : http://localhost:8000
# Documentation auto : http://localhost:8000/docs
```

**Option B : Serveur Cloud (Production)**

**Sur Heroku :**
```bash
# Fichier: Procfile
web: uvicorn app:app --host 0.0.0.0 --port $PORT

# Fichier: runtime.txt
python-3.11.0

# Déployer
heroku create aliexpress-scraper-api
git push heroku main
```

**Sur AWS EC2 / DigitalOcean / VPS :**
```bash
# SSH vers votre serveur
ssh user@votre-serveur.com

# Installer les dépendances
sudo apt update
sudo apt install python3-pip nginx

# Cloner votre code
git clone <votre-repo>
cd backend

# Installer
pip install -r requirements.txt

# Lancer avec Supervisor (reste actif)
sudo apt install supervisor

# Fichier: /etc/supervisor/conf.d/api.conf
[program:api]
command=/usr/bin/uvicorn app:app --host 0.0.0.0 --port 8000
directory=/home/user/backend
autostart=true
autorestart=true

# Redémarrer
sudo supervisorctl reread
sudo supervisorctl update
```

---

### Partie 2 : Frontend (Client) - CHEZ LE CLIENT

#### 2.1 - Client Streamlit Simple

**Fichier : `frontend/app.py`**

```python
import streamlit as st
import requests
from typing import List, Dict
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================

# URL de votre API (donner cette URL au client)
API_URL = "https://votre-api.herokuapp.com"  # OU votre IP

# Clé de licence (unique par client)
LICENSE_KEY = "lic_abc123"  # Vous la donnez au client

# ============================================
# FONCTION D'APPEL API
# ============================================

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Appeler votre API"""
    headers = {
        "X-License-Key": LICENSE_KEY,
        "Content-Type": "application/json"
    }

    url = f"{API_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("❌ Licence invalide ou expirée")
        elif e.response.status_code == 429:
            st.error("❌ Quota mensuel dépassé")
        else:
            st.error(f"❌ Erreur: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Erreur de connexion: {str(e)}")
        return None

# ============================================
# INTERFACE STREAMLIT
# ============================================

st.set_page_config(page_title="AliExpress Scraper", page_icon="🔍", layout="wide")

st.title("🔍 AliExpress Product Finder")
st.markdown("---")

# Sidebar: Statut de la licence
with st.sidebar:
    st.header("📊 Statut")

    if st.button("🔄 Vérifier ma licence"):
        status = call_api("/api/v1/license/status")
        if status:
            st.success(f"✅ Client: {status['client']}")
            st.info(f"📅 Expire le: {status['expiry']}")
            st.metric("Quota restant", f"{status['quota_remaining']}/{status['quota_total']}")

# Main: Formulaire de recherche
col1, col2 = st.columns(2)

with col1:
    search_url = st.text_input(
        "🔗 URL de recherche AliExpress",
        placeholder="https://www.aliexpress.com/w/wholesale-..."
    )

with col2:
    reference_image = st.text_input(
        "🖼️ URL de l'image de référence",
        placeholder="https://example.com/image.jpg"
    )

max_results = st.slider("📊 Nombre de résultats max", 5, 50, 20)

if st.button("🚀 Lancer la recherche", type="primary"):
    if not search_url or not reference_image:
        st.warning("⚠️ Veuillez remplir tous les champs")
    else:
        with st.spinner("🔄 Recherche en cours..."):
            # Appeler l'API
            data = {
                "search_url": search_url,
                "reference_image_url": reference_image,
                "max_results": max_results
            }

            response = call_api("/api/v1/search", method="POST", data=data)

            if response:
                results = response["results"]

                st.success(f"✅ {response['total_found']} produits trouvés en {response['execution_time']:.2f}s")

                # Afficher les résultats
                for i, product in enumerate(results, 1):
                    with st.expander(f"#{i} - {product['title']} (Score: {product['similarity_score']:.2%})"):
                        col_img, col_info = st.columns([1, 2])

                        with col_img:
                            st.image(product['image_url'], width=200)

                        with col_info:
                            st.markdown(f"**Prix:** {product['price']}")
                            st.markdown(f"**Similarité:** {product['similarity_score']:.2%}")
                            st.markdown(f"[🔗 Voir sur AliExpress]({product['url']})")

                # Export CSV
                df = pd.DataFrame(results)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Télécharger CSV",
                    csv,
                    "resultats.csv",
                    "text/csv"
                )
```

#### 2.2 - Fichier de Configuration Client

**Fichier : `frontend/requirements.txt`**
```txt
streamlit==1.28.0
requests==2.31.0
pandas==2.1.0
```

#### 2.3 - Distribuer au Client

**Ce que vous donnez au client :**

1. **Fichier exécutable (avec PyInstaller)** :
```bash
# Vous créez un .exe du frontend
pyinstaller --onefile --windowed frontend/app.py
```

2. **Fichier de configuration** :
```json
{
  "api_url": "https://votre-api.herokuapp.com",
  "license_key": "lic_client_unique_123"
}
```

3. **Documentation** : `CLIENT_GUIDE.md`

---

## 🔐 Sécurité Avancée

### 1. Système de Licence Robuste

**Fichier : `backend/license_manager.py`**

```python
import hashlib
import hmac
import datetime
import json
from cryptography.fernet import Fernet

class LicenseManager:
    def __init__(self, secret_key: str):
        self.secret = secret_key.encode()
        self.cipher = Fernet(Fernet.generate_key())

    def generate_license(self, client_name: str, expiry_days: int = 365) -> str:
        """Générer une clé de licence unique"""
        expiry = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

        data = {
            "client": client_name,
            "expiry": expiry.isoformat(),
            "created": datetime.datetime.now().isoformat()
        }

        # Chiffrer les données
        encrypted = self.cipher.encrypt(json.dumps(data).encode())

        # Générer la signature HMAC
        signature = hmac.new(self.secret, encrypted, hashlib.sha256).hexdigest()

        # Licence = données_chiffrées + signature
        license_key = f"{encrypted.hex()}:{signature}"

        return license_key

    def validate_license(self, license_key: str) -> tuple[bool, dict]:
        """Valider une licence"""
        try:
            # Séparer données et signature
            encrypted_hex, signature = license_key.split(":")
            encrypted = bytes.fromhex(encrypted_hex)

            # Vérifier la signature
            expected_sig = hmac.new(self.secret, encrypted, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_sig):
                return False, {"error": "Signature invalide"}

            # Déchiffrer
            decrypted = self.cipher.decrypt(encrypted)
            data = json.loads(decrypted.decode())

            # Vérifier expiration
            expiry = datetime.datetime.fromisoformat(data["expiry"])
            if datetime.datetime.now() > expiry:
                return False, {"error": "Licence expirée"}

            return True, data

        except Exception as e:
            return False, {"error": str(e)}

# Utilisation
manager = LicenseManager("votre_secret_super_securise")
license = manager.generate_license("Entreprise XYZ", expiry_days=365)
print(f"Licence générée: {license}")
```

### 2. Rate Limiting (Limiter les Abus)

```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/search")
@limiter.limit("10/minute")  # Max 10 requêtes par minute
async def search_products(request: Request, ...):
    # ...
    pass
```

### 3. Logging et Surveillance

```python
import logging
from datetime import datetime

logging.basicConfig(
    filename='api_access.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.post("/api/v1/search")
async def search_products(...):
    # Logger chaque utilisation
    logging.info(f"""
        License: {license_key}
        Client: {license_data['client']}
        URL: {request.search_url}
        Time: {datetime.now()}
        IP: {request.client.host}
    """)
    # ...
```

---

## 💰 Modèles de Facturation

### Option 1 : Par Recherche
```python
PRICING = {
    "per_search": 0.10  # 0.10€ par recherche
}

# Déduire du crédit
license_data["credit"] -= PRICING["per_search"]
```

### Option 2 : Par Quota Mensuel
```python
PLANS = {
    "basic": {"quota": 100, "price": 49},
    "pro": {"quota": 500, "price": 199},
    "enterprise": {"quota": 2000, "price": 699}
}
```

### Option 3 : Par Nombre de Résultats
```python
cost = len(results) * 0.02  # 0.02€ par produit trouvé
```

---

## 📊 Tableau Comparatif

| Critère | PyInstaller | Docker | **API (Hybride)** |
|---------|-------------|--------|-------------------|
| Sécurité | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Contrôle | ❌ | ❌ | ✅ Total |
| Mises à jour | Difficile | Moyen | ✅ Facile |
| Facturation | Licence fixe | Licence fixe | ✅ À l'usage |
| Coût initial | Faible | Moyen | **Élevé** |
| Revenus long terme | Faible | Moyen | **Élevé** |

---

## 🚀 Déploiement Complet

### Étape 1 : Déployer le Backend

```bash
# Sur Heroku (gratuit pour commencer)
heroku create mon-api-scraper
heroku config:set SECRET_KEY="votre_secret"
git push heroku main

# URL de votre API : https://mon-api-scraper.herokuapp.com
```

### Étape 2 : Tester l'API

```bash
# Test avec curl
curl -X POST https://mon-api-scraper.herokuapp.com/api/v1/search \
  -H "X-License-Key: lic_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "search_url": "https://aliexpress.com/...",
    "reference_image_url": "https://example.com/image.jpg",
    "max_results": 10
  }'
```

### Étape 3 : Créer le Client pour le Client

```bash
# Compiler le frontend en .exe
cd frontend
pyinstaller --onefile --windowed app.py

# Donner au client :
# - dist/app.exe
# - config.json (avec license_key unique)
# - CLIENT_GUIDE.md
```

### Étape 4 : Générer des Licences

```python
# Script: generate_license.py
from license_manager import LicenseManager

manager = LicenseManager("votre_secret")

clients = [
    ("Entreprise A", 365),
    ("Entreprise B", 180),
    ("Entreprise C", 90),
]

for client_name, days in clients:
    license = manager.generate_license(client_name, days)
    print(f"{client_name}: {license}")
```

---

## 🎯 Résumé

**Ce que le client reçoit :**
- ✅ Une interface simple (fichier .exe)
- ✅ Une clé de licence unique
- ✅ Accès à votre API

**Ce que VOUS gardez :**
- ✅ Tout le code de scraping
- ✅ Contrôle total de l'utilisation
- ✅ Possibilité de désactiver un client
- ✅ Statistiques d'utilisation
- ✅ Revenus récurrents

**Vous pouvez :**
- Facturer à l'usage
- Désactiver les licences expirées
- Faire des mises à jour sans toucher les clients
- Voir qui utilise combien
- Éviter la revente de votre code

---

## 📚 Prochaines Étapes

1. **Tester en local** : Lancer backend + frontend localement
2. **Déployer le backend** : Heroku/AWS/DigitalOcean
3. **Créer les licences** : Générer des clés uniques
4. **Compiler le frontend** : PyInstaller
5. **Distribuer** : Envoyer .exe + licence au client

---

Voulez-vous que je vous aide à implémenter cette architecture ? 🚀
