# 🚀 Guide de Déploiement et Sécurisation

## Options de Déploiement Sécurisé

---

## 🌐 Option 1: Déploiement Web (RECOMMANDÉ - Plus Simple)

### A) Streamlit Cloud (Gratuit/Payant)

**Avantages:**
- ✅ Code reste sur serveur (pas accessible aux utilisateurs)
- ✅ Accès via navigateur web uniquement
- ✅ Mise à jour centralisée
- ✅ Pas d'installation pour l'utilisateur
- ✅ Contrôle d'accès avec authentification

**Comment faire:**

1. **Créer compte Streamlit Cloud:**
```bash
# Sur https://share.streamlit.io
```

2. **Déployer l'app:**
```bash
# Connecter votre repo GitHub (privé!)
# L'app sera accessible via: https://votre-app.streamlit.app
```

3. **Authentification (protection):**
```python
# Ajouter dans app.py
import streamlit_authenticator as stauth

# Configuration d'authentification
authenticator = stauth.Authenticate(
    credentials={
        'usernames': {
            'client1': {
                'name': 'Client Nom',
                'password': 'hashed_password_here'  # Hash bcrypt
            }
        }
    },
    cookie_name='aliexpress_scraper',
    key='random_signature_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Afficher l'app normale
    main_app()
elif authentication_status == False:
    st.error('Username/password incorrect')
elif authentication_status == None:
    st.warning('Please enter username and password')
```

4. **Installation authenticator:**
```bash
pip install streamlit-authenticator
```

**Coût:** Gratuit (public) ou 20$/mois (privé avec auth)

---

### B) Heroku / Railway / Render

**Similaire à Streamlit Cloud mais plus de contrôle**

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT"
```

**Coût:** 5-15$/mois

---

## 💻 Option 2: Application Desktop Exécutable (Code Protégé)

### A) PyInstaller - Créer .exe/.app

**Avantages:**
- ✅ Code compilé (non lisible)
- ✅ Un seul fichier à distribuer
- ✅ Pas besoin de Python installé
- ❌ Mais fichier très gros (500MB+)

**Comment faire:**

1. **Installer PyInstaller:**
```bash
pip install pyinstaller
```

2. **Créer un fichier `build_exe.py`:**
```python
"""
Script pour créer l'exécutable sécurisé
"""
import PyInstaller.__main__
import sys

# Configuration
app_name = "AliExpress_Scraper"
icon_path = "icon.ico"  # Optionnel

PyInstaller.__main__.run([
    'app.py',
    '--name=%s' % app_name,
    '--onefile',  # Un seul fichier
    '--windowed',  # Pas de console
    '--add-data=src:src',  # Inclure dossier src
    '--hidden-import=streamlit',
    '--hidden-import=crawlee',
    '--hidden-import=playwright',
    '--hidden-import=open_clip',
    '--hidden-import=torch',
    '--collect-all=streamlit',
    '--collect-all=crawlee',
    '--collect-all=playwright',
    '--collect-all=open_clip',
    # '--icon=%s' % icon_path,  # Si vous avez un icon
    '--noconfirm',  # Écraser sans demander
])
```

3. **Créer l'exécutable:**
```bash
python build_exe.py
```

4. **Résultat:**
```
dist/AliExpress_Scraper.exe  (Windows)
dist/AliExpress_Scraper.app  (Mac)
dist/AliExpress_Scraper      (Linux)
```

5. **Distribuer:**
- Donnez SEULEMENT le fichier dans `dist/`
- Le code source reste protégé
- L'utilisateur double-clique pour lancer

**Problème:** Fichier très gros (500MB-1GB) à cause de PyTorch et Playwright

---

### B) PyOxidizer (Alternatif - Plus Rapide)

**Plus performant que PyInstaller**

```toml
# pyoxidizer.toml
[[python_distribution]]
version = "3.11"

[[python_run]]
code = "import streamlit.cli; streamlit.cli.main(['run', 'app.py'])"
```

---

## 🐳 Option 3: Docker Container (Professionnel)

**Avantages:**
- ✅ Code caché dans l'image
- ✅ Environnement isolé
- ✅ Facile à déployer sur serveur
- ✅ Multi-plateforme

**Comment faire:**

1. **Créer `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Installer Playwright browsers
RUN pip install playwright && playwright install chromium

# Copier requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code (sera caché dans l'image)
COPY . .

# Exposer port Streamlit
EXPOSE 8501

# Lancer l'app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build l'image:**
```bash
docker build -t aliexpress-scraper:1.0 .
```

3. **Créer un script de lancement pour le client:**
```bash
# run_app.sh (pour le client)
#!/bin/bash
docker run -p 8501:8501 aliexpress-scraper:1.0
```

4. **Distribuer:**
- Donnez l'image Docker: `aliexpress-scraper.tar`
- Le client fait: `docker load < aliexpress-scraper.tar`
- Lance avec: `./run_app.sh`
- Accède via: `http://localhost:8501`

**Le code est caché dans l'image Docker (non extractible facilement)**

---

## 🔐 Option 4: Obfuscation Python (Protection Code Source)

**Si vous devez donner les fichiers .py**

### A) PyArmor (Recommandé)

```bash
# Installer PyArmor
pip install pyarmor

# Obfusquer le code
pyarmor gen app.py src/

# Résultat: Dossier dist/ avec code obfusqué
# dist/
#   app.py  (obfusqué - illisible)
#   src/    (obfusqué)
```

**Code obfusqué ressemble à:**
```python
from pyarmor_runtime import __pyarmor__
__pyarmor__(__name__, __file__, b'PYZ-encrypted-bytecode-here')
```

### B) Cython - Compiler en .so/.pyd

```bash
# Compiler en binaire
pip install cython
cythonize -i app.py

# Génère app.so (Linux) ou app.pyd (Windows)
# Code source non récupérable
```

---

## 🔑 Option 5: Système de Licensing (Contrôle d'Usage)

**Ajouter un système de clés de licence**

### Créer `license_manager.py`:
```python
"""
Système simple de licence
"""
import hashlib
import datetime
from cryptography.fernet import Fernet

class LicenseManager:
    def __init__(self):
        # Clé secrète (à garder PRIVÉE)
        self.secret_key = b'VOTRE_CLE_SECRETE_ICI'
        self.cipher = Fernet(self.secret_key)

    def generate_license(self, client_name: str, expiry_days: int = 365):
        """Générer une clé de licence"""
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

        license_data = {
            'client': client_name,
            'expiry': expiry_date.isoformat(),
            'features': ['scraping', 'export']
        }

        # Encoder et chiffrer
        import json
        license_str = json.dumps(license_data)
        encrypted = self.cipher.encrypt(license_str.encode())

        return encrypted.hex()

    def validate_license(self, license_key: str) -> tuple[bool, str]:
        """Valider une clé de licence"""
        try:
            # Déchiffrer
            encrypted_bytes = bytes.fromhex(license_key)
            decrypted = self.cipher.decrypt(encrypted_bytes)

            import json
            license_data = json.loads(decrypted.decode())

            # Vérifier expiration
            expiry = datetime.datetime.fromisoformat(license_data['expiry'])
            if datetime.datetime.now() > expiry:
                return False, "License expired"

            return True, f"Licensed to: {license_data['client']}"

        except Exception as e:
            return False, f"Invalid license: {str(e)}"


# Intégration dans app.py
def check_license():
    """Vérifier la licence au démarrage"""
    import streamlit as st
    from pathlib import Path

    license_file = Path(".license")

    if not license_file.exists():
        st.error("❌ No license file found (.license)")
        st.info("Please contact support for a license key")
        st.stop()

    license_key = license_file.read_text().strip()

    lm = LicenseManager()
    is_valid, message = lm.validate_license(license_key)

    if not is_valid:
        st.error(f"❌ License error: {message}")
        st.stop()

    st.sidebar.success(f"✅ {message}")

# Dans app.py, ajouter au début:
check_license()
```

### Utilisation:

```python
# Vous (développeur) générez une licence:
lm = LicenseManager()
client_license = lm.generate_license("Client XYZ", expiry_days=365)
print(client_license)  # Donner cette clé au client

# Le client crée le fichier .license avec la clé
# L'app vérifie la licence au démarrage
```

---

## 📊 Comparaison des Options

| Option | Sécurité Code | Facilité | Coût | Maintenance |
|--------|---------------|----------|------|-------------|
| **Streamlit Cloud** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 0-20$/mois | ⭐⭐⭐⭐⭐ |
| **PyInstaller** | ⭐⭐⭐⭐ | ⭐⭐⭐ | Gratuit | ⭐⭐ |
| **Docker** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 5-15$/mois | ⭐⭐⭐⭐ |
| **PyArmor** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 50-200$ | ⭐⭐⭐ |
| **Licensing** | ⭐⭐⭐ | ⭐⭐⭐ | Gratuit | ⭐⭐⭐⭐ |

---

## 🎯 Recommandations par Cas d'Usage

### 1. **Client Technique (a Docker)**
```
✅ Option: Docker Container
- Build l'image
- Donnez aliexpress-scraper.tar + script de lancement
- Code totalement caché
```

### 2. **Client Non-Technique**
```
✅ Option: Streamlit Cloud + Auth
- Hébergez l'app
- Donnez juste l'URL + login/password
- Vous contrôlez tout
```

### 3. **Distribution Large (Produit Commercial)**
```
✅ Option: PyInstaller + Licensing
- .exe avec système de clés
- Contrôle par licence
- Révocation possible
```

### 4. **Maximum Sécurité + Contrôle**
```
✅ Option: Web (Heroku/Railway) + Auth + Licensing
- Code sur serveur
- Authentification par utilisateur
- Licensing par fonctionnalité
- Logs d'usage
```

---

## 🛠️ Solution Hybride Recommandée

**Combiner plusieurs protections:**

1. **Backend API (votre serveur):**
   - Code de scraping sur VOTRE serveur
   - API avec authentification
   - Rate limiting

2. **Frontend (client):**
   - Application Streamlit simplifiée
   - Appelle votre API
   - Code minimal exposé

### Architecture:

```
[Client Machine]
   └── Streamlit App (simple UI)
         │
         │ HTTPS + API Key
         ↓
   [Votre Serveur]
         ├── API (FastAPI)
         └── Scraper (code protégé)
```

### Exemple API (`api.py`):
```python
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
import hashlib

app = FastAPI()

# Vos clés API clients (hashées)
API_KEYS = {
    "hash_client1": {"name": "Client XYZ", "tier": "premium"},
    "hash_client2": {"name": "Client ABC", "tier": "basic"}
}

def verify_api_key(api_key: str):
    """Vérifier la clé API"""
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    if hashed not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[hashed]

@app.post("/scrape")
async def scrape_products(
    image_data: dict,
    api_key: str = Header(None, alias="X-API-Key")
):
    """Endpoint de scraping"""
    client = verify_api_key(api_key)

    # Votre code de scraping ici (PROTÉGÉ sur serveur)
    scraper = AliExpressImageSearchScraper()
    results = await scraper.search_by_image(...)

    return {"results": results, "client": client["name"]}
```

### Client Streamlit simplifié:
```python
import streamlit as st
import requests

API_URL = "https://votre-api.com"
API_KEY = st.secrets["api_key"]  # Clé unique par client

uploaded_file = st.file_uploader("Image")

if st.button("Rechercher"):
    response = requests.post(
        f"{API_URL}/scrape",
        headers={"X-API-Key": API_KEY},
        json={"image": image_data}
    )
    results = response.json()
    st.write(results)
```

**Avantages:**
- ✅ Code de scraping 100% protégé (sur votre serveur)
- ✅ Client ne peut pas copier votre logique
- ✅ Contrôle d'usage (rate limiting, analytics)
- ✅ Mise à jour centralisée
- ✅ Monétisation facile (API payante)

---

## 💰 Modèles de Monétisation

### 1. **Abonnement Mensuel**
```python
# Vérifier le tier dans l'API
if client["tier"] == "basic":
    max_requests = 100  # 100 scrapes/mois
elif client["tier"] == "premium":
    max_requests = 1000
```

### 2. **Pay-per-Use**
```python
# Déduire des crédits à chaque requête
if client["credits"] < cost:
    raise HTTPException(status_code=402, detail="Insufficient credits")
client["credits"] -= cost
```

### 3. **Licence Perpétuelle**
```python
# Vérifier date d'achat + activation
if not license_is_perpetual(client["license"]):
    raise HTTPException(status_code=403, detail="License required")
```

---

## 📝 Checklist de Déploiement Sécurisé

- [ ] Retirer tous les prints/debug du code
- [ ] Supprimer les credentials hardcodés
- [ ] Ajouter variables d'environnement pour secrets
- [ ] Obfusquer ou compiler le code
- [ ] Ajouter système de licensing
- [ ] Logger les usages (analytics)
- [ ] Ajouter rate limiting
- [ ] Tester sur machine propre (sans Python)
- [ ] Créer documentation utilisateur
- [ ] Préparer support client

---

## 🚨 Ce Qu'il NE FAUT PAS Faire

❌ **Donner les fichiers .py directement**
❌ **Mettre le code sur GitHub public**
❌ **Hardcoder des credentials**
❌ **Oublier les logs d'usage**
❌ **Pas de système de mise à jour**
❌ **Pas de support pour les clients**

---

## 📞 Prochaines Étapes

**Choisissez votre option préférée, et je peux vous aider à:**
1. Créer les fichiers de configuration
2. Builder l'exécutable/image
3. Mettre en place l'authentification
4. Créer le système de licensing
5. Déployer sur le cloud

**Quelle option vous intéresse le plus?**
