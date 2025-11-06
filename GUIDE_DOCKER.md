# 🐳 Guide Docker - Pour le Développeur

Guide complet pour builder, tester et distribuer l'application avec Docker

---

## 🎯 Vue d'Ensemble

Docker offre plusieurs avantages pour ce projet:
- ✅ **Code protégé**: Le code source est caché dans l'image
- ✅ **Pas de dépendances**: Le client n'a besoin que de Docker
- ✅ **Isolation**: L'app tourne dans un environnement isolé
- ✅ **Multi-plateforme**: Fonctionne sur Windows, Mac, Linux
- ✅ **Reproductible**: Même environnement partout

---

## 📁 Fichiers Docker Créés

```
Web-Scrapping/
├── Dockerfile              ← Configuration de l'image
├── docker-compose.yml      ← Orchestration (dev)
├── .dockerignore          ← Fichiers à exclure
├── build_docker.sh         ← Script de build
├── save_docker.sh          ← Script de sauvegarde
├── run_docker.sh           ← Script client (lancement)
├── README_DOCKER.md        ← Guide client
└── GUIDE_DOCKER.md         ← Ce fichier (guide dev)
```

---

## 🏗️ Étape 1: Build de l'Image

### Méthode Simple (Recommandée)

```bash
# Rendre le script exécutable (une fois)
chmod +x build_docker.sh

# Builder l'image
./build_docker.sh
```

**Durée:** 10-30 minutes
**Résultat:** Image Docker `aliexpress-scraper:latest`

### Méthode Manuelle

```bash
# Build avec Docker directement
docker build -t aliexpress-scraper:latest .

# Ou avec docker-compose
docker-compose build
```

### Options de Build Avancées

```bash
# Build sans cache (fresh build)
docker build --no-cache -t aliexpress-scraper:latest .

# Build avec un tag spécifique
docker build -t aliexpress-scraper:v1.0.0 .

# Build multi-plateforme (ARM + x86)
docker buildx build --platform linux/amd64,linux/arm64 -t aliexpress-scraper:latest .
```

---

## 🧪 Étape 2: Tester Localement

### Option A: docker run

```bash
# Lancer le container
docker run -d \
  --name aliexpress_scraper \
  -p 8501:8501 \
  -v $(pwd)/output_recherche1:/app/output_recherche1 \
  aliexpress-scraper:latest

# Vérifier les logs
docker logs -f aliexpress_scraper

# Ouvrir dans le navigateur
open http://localhost:8501  # Mac
xdg-open http://localhost:8501  # Linux
start http://localhost:8501  # Windows
```

### Option B: docker-compose (Plus Facile)

```bash
# Lancer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### Tester une Recherche Complète

1. Ouvrir http://localhost:8501
2. Uploader une image test
3. Mettre 10 produits max
4. Lancer la recherche
5. Attendre 2-5 minutes
6. Vérifier les résultats

**Checklist de test:**
- [ ] L'app se lance sans erreur
- [ ] Upload d'image fonctionne
- [ ] Recherche complète sans crash
- [ ] Images se téléchargent
- [ ] Résultats dans output_recherche1/
- [ ] Export Excel fonctionne

---

## 💾 Étape 3: Sauvegarder pour Distribution

### Méthode Simple

```bash
./save_docker.sh
```

**Résultat:** Fichier `aliexpress-scraper-docker.tar` (~2-3GB)

### Méthode Manuelle

```bash
# Sauvegarder l'image
docker save aliexpress-scraper:latest -o aliexpress-scraper-docker.tar

# Compresser pour réduire la taille (optionnel)
gzip aliexpress-scraper-docker.tar
# Résultat: aliexpress-scraper-docker.tar.gz (~1-2GB)
```

### Vérifier l'Image Sauvegardée

```bash
# Voir la taille
ls -lh aliexpress-scraper-docker.tar

# Tester le chargement
docker load < aliexpress-scraper-docker.tar
```

---

## 📦 Étape 4: Distribuer au Client

### Package à Donner

**Donnez ces 3 fichiers au client:**

1. ✅ `aliexpress-scraper-docker.tar` (ou .tar.gz) - L'image Docker
2. ✅ `run_docker.sh` - Script de lancement
3. ✅ `README_DOCKER.md` - Guide d'utilisation

### Instructions pour le Client

```bash
# 1. Installer Docker Desktop (une fois)
https://www.docker.com/products/docker-desktop

# 2. Charger l'image
docker load < aliexpress-scraper-docker.tar

# Ou si compressé:
gunzip aliexpress-scraper-docker.tar.gz
docker load < aliexpress-scraper-docker.tar

# 3. Lancer l'app
./run_docker.sh

# 4. Ouvrir le navigateur
http://localhost:8501
```

---

## 🔧 Configuration Avancée

### Personnaliser le Dockerfile

#### Changer la Version Python

```dockerfile
# Ligne 1 et ligne 19
FROM python:3.10-slim  # Au lieu de 3.11
```

#### Ajouter des Dépendances Système

```dockerfile
# Dans la section RUN apt-get install
RUN apt-get update && apt-get install -y \
    wget \
    curl \  # Ajouter ici
    git \   # Ajouter ici
    && rm -rf /var/lib/apt/lists/*
```

#### Optimiser la Taille de l'Image

```dockerfile
# Utiliser alpine au lieu de slim (plus petit)
FROM python:3.11-alpine

# Attention: Alpine nécessite des ajustements pour Playwright
```

### Personnaliser docker-compose.yml

#### Changer le Port

```yaml
ports:
  - "8502:8501"  # Port hôte:port container
```

#### Ajouter des Variables d'Environnement

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - MY_CUSTOM_VAR=value
```

#### Limiter les Ressources

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
```

---

## 🐛 Troubleshooting

### L'Image est Très Grosse (>3GB)

**C'est normal!** PyTorch + Playwright = ~2-3GB

**Pour réduire:**
1. Exclure des modules non utilisés
2. Utiliser multi-stage build (déjà fait)
3. Compresser le .tar avec gzip (-30%)

### Build Échoue sur "playwright install"

```dockerfile
# Dans le Dockerfile, ajouter plus de mémoire au build:
docker build --memory=8g -t aliexpress-scraper:latest .
```

### Container Plante au Démarrage

```bash
# Voir les logs détaillés
docker logs aliexpress_scraper

# Lancer en mode interactif pour debug
docker run -it --rm aliexpress-scraper:latest /bin/bash
```

### Port 8501 Déjà Utilisé

```bash
# Voir ce qui utilise le port
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# Utiliser un autre port
docker run -p 8502:8501 aliexpress-scraper:latest
```

### Volumes Ne Persistent Pas

```bash
# Utiliser chemin absolu
docker run -v /absolute/path/output_recherche1:/app/output_recherche1 ...

# Ou $(pwd) pour chemin relatif
docker run -v $(pwd)/output_recherche1:/app/output_recherche1 ...
```

---

## 🔒 Sécurité

### Code Source Protégé

**Le client NE PEUT PAS:**
- ❌ Voir les fichiers .py
- ❌ Extraire le code source facilement
- ❌ Modifier l'application

**Le client PEUT (avec effort):**
- ⚠️ Entrer dans le container et copier les fichiers
- ⚠️ Extraire les layers de l'image

**Pour plus de sécurité:**

```dockerfile
# 1. Chiffrer les fichiers sensibles
# 2. Ajouter obfuscation PyArmor AVANT le build Docker
# 3. Utiliser licensing avec vérification serveur
```

### Meilleures Pratiques

```dockerfile
# 1. Utiliser utilisateur non-root (déjà fait)
USER appuser

# 2. Scanner l'image pour vulnérabilités
# docker scan aliexpress-scraper:latest

# 3. Signer l'image (Docker Content Trust)
# export DOCKER_CONTENT_TRUST=1
```

---

## 📊 Monitoring et Maintenance

### Voir les Ressources Utilisées

```bash
# Stats en temps réel
docker stats aliexpress_scraper

# Utilisation disque
docker system df
```

### Nettoyer Docker

```bash
# Supprimer images non utilisées
docker image prune -a

# Supprimer containers arrêtés
docker container prune

# Nettoyer TOUT (libère beaucoup d'espace)
docker system prune -a --volumes
```

### Logs et Debug

```bash
# Voir les logs
docker logs aliexpress_scraper

# Suivre les logs en temps réel
docker logs -f --tail 100 aliexpress_scraper

# Entrer dans le container (debug)
docker exec -it aliexpress_scraper /bin/bash
```

---

## 🚀 Déploiement Cloud (Bonus)

### Sur un Serveur VPS

```bash
# 1. Installer Docker sur le serveur
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Copier l'image vers le serveur
scp aliexpress-scraper-docker.tar user@server:/home/user/

# 3. Sur le serveur, charger et lancer
docker load < aliexpress-scraper-docker.tar
docker run -d -p 80:8501 --restart always aliexpress-scraper:latest

# 4. Accéder depuis internet
http://votre-serveur.com
```

### Avec Docker Registry

```bash
# 1. Tag pour registry privé
docker tag aliexpress-scraper:latest registry.example.com/aliexpress-scraper:latest

# 2. Push vers registry
docker push registry.example.com/aliexpress-scraper:latest

# 3. Le client pull depuis registry
docker pull registry.example.com/aliexpress-scraper:latest
```

---

## 📝 Checklist de Distribution

Avant de donner l'image au client:

- [ ] Image buildée avec succès
- [ ] Testée localement de A à Z
- [ ] Aucune donnée sensible dans l'image
- [ ] Taille de l'image acceptable (<4GB)
- [ ] Image sauvegardée en .tar
- [ ] Script run_docker.sh testé
- [ ] README_DOCKER.md à jour
- [ ] Instructions claires pour le client
- [ ] Support prévu pour questions

---

## 🎓 Astuces Pro

### Build Cache

```bash
# Utiliser le cache pour builds plus rapides
docker build -t aliexpress-scraper:latest .

# Forcer rebuild sans cache
docker build --no-cache -t aliexpress-scraper:latest .
```

### Multi-Stage Build

```dockerfile
# Déjà implémenté! Réduit la taille de l'image finale
FROM python:3.11-slim as builder  # Stage build
FROM python:3.11-slim  # Stage final (plus léger)
```

### Layer Caching

```dockerfile
# Copier requirements.txt AVANT le code
# Si requirements ne change pas, layer est en cache
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # Code après
```

### Healthcheck

```dockerfile
# Déjà implémenté! Docker vérifie que l'app est vivante
HEALTHCHECK --interval=30s CMD wget --spider http://localhost:8501/_stcore/health
```

---

## 📞 Comparaison: Docker vs PyInstaller

| Aspect | Docker | PyInstaller |
|--------|--------|-------------|
| **Taille** | ~2-3GB | ~1-2GB |
| **Sécurité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Setup client** | Installer Docker | Aucun |
| **Multi-plateforme** | ✅ Même image | ❌ Build par OS |
| **Mise à jour** | ✅ Facile | ⚠️ Redistribuer .exe |
| **Isolation** | ✅ Complet | ❌ Aucune |
| **Code protégé** | ✅ Très bien | ✅ Bien |

**Recommandation:**
- **Client technique**: Docker (meilleur)
- **Client non-tech**: PyInstaller (plus simple)

---

## 🎉 Résumé des Commandes

```bash
# DÉVELOPPEUR

# 1. Build
./build_docker.sh
# ou
docker build -t aliexpress-scraper:latest .

# 2. Test local
docker-compose up -d
# Tester sur http://localhost:8501

# 3. Sauvegarder
./save_docker.sh
# ou
docker save aliexpress-scraper:latest -o aliexpress-scraper-docker.tar

# 4. Distribuer
# Donner: .tar + run_docker.sh + README_DOCKER.md

# ========================================

# CLIENT

# 1. Charger
docker load < aliexpress-scraper-docker.tar

# 2. Lancer
./run_docker.sh

# 3. Utiliser
http://localhost:8501
```

---

**Bon déploiement avec Docker! 🐳🚀**
