# Guide de Déploiement en Production

## Options de Déploiement

### 1. Docker Compose (Recommandé)
### 2. Kubernetes
### 3. Cloud Platforms (AWS, GCP, Azure)
### 4. VPS/Serveur Dédié

---

## Déploiement Docker Compose

### Prérequis

```bash
# Installer Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Configuration Production

Créer `.env.production` :

```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password

# Models
DEVICE=cpu  # ou 'cuda' si GPU
MODEL_CACHE_TTL=7200

# Security
API_KEY=your_production_api_key_here

# Logging
LOG_LEVEL=WARNING

# Frontend
REACT_APP_API_URL=https://your-domain.com
```

### Déploiement

```bash
# Build les images
docker-compose -f docker/docker-compose.yml build

# Lancer en production
docker-compose -f docker/docker-compose.yml up -d

# Vérifier le statut
docker-compose -f docker/docker-compose.yml ps

# Voir les logs
docker-compose -f docker/docker-compose.yml logs -f
```

### SSL/HTTPS avec Nginx

Créer `docker/docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-prod.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - frontend
      - backend
    networks:
      - luxury-network

  # ... autres services
```

Obtenir certificat SSL :

```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtenir certificat
sudo certbot --nginx -d your-domain.com
```

---

## Déploiement Kubernetes

### Prérequis

```bash
# Installer kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Installer Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Créer les Manifests

`k8s/deployment.yaml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: luxury-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: luxury-backend
  template:
    metadata:
      labels:
        app: luxury-backend
    spec:
      containers:
      - name: backend
        image: your-registry/luxury-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: DEVICE
          value: cpu
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

`k8s/service.yaml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: luxury-backend-service
spec:
  selector:
    app: luxury-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### Déployer

```bash
# Appliquer les configs
kubectl apply -f k8s/

# Vérifier
kubectl get pods
kubectl get services

# Scaler
kubectl scale deployment luxury-backend --replicas=5
```

---

## Déploiement AWS

### Architecture Recommandée

- **ECS (Elastic Container Service)** : Pour les conteneurs Docker
- **RDS** : Pour PostgreSQL (si vous l'utilisez)
- **ElastiCache** : Pour Redis
- **S3** : Pour les images de produits
- **CloudFront** : CDN pour le frontend
- **ALB** : Load balancer

### Terraform Configuration

`terraform/main.tf` :

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "luxury_cluster" {
  name = "luxury-ai-search"
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "luxury-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# ALB
resource "aws_lb" "main" {
  name               = "luxury-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}
```

### Déployer

```bash
# Initialiser Terraform
terraform init

# Planifier
terraform plan

# Appliquer
terraform apply

# Push images sur ECR
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-1.amazonaws.com

docker tag luxury-backend:latest <account-id>.dkr.ecr.eu-west-1.amazonaws.com/luxury-backend:latest
docker push <account-id>.dkr.ecr.eu-west-1.amazonaws.com/luxury-backend:latest
```

---

## Déploiement Google Cloud Platform

### Cloud Run (Serverless)

```bash
# Build et push
gcloud builds submit --tag gcr.io/PROJECT-ID/luxury-backend

# Deploy
gcloud run deploy luxury-backend \
  --image gcr.io/PROJECT-ID/luxury-backend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

### GKE (Kubernetes)

```bash
# Créer cluster
gcloud container clusters create luxury-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=europe-west1

# Déployer
kubectl apply -f k8s/
```

---

## Optimisation Production

### 1. Cache et Performance

**Redis Configuration :**

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

**Nginx Caching :**

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

### 2. Monitoring

**Prometheus + Grafana :**

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Instrumenter le code :**

```python
# backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Ajouter metrics
Instrumentator().instrument(app).expose(app)
```

### 3. Logging

**Configuration Centralisée :**

```python
# backend/app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler
    handler = RotatingFileHandler(
        'app.log',
        maxBytes=10_000_000,
        backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

**ELK Stack :**

```yaml
# docker-compose.elk.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
```

### 4. Sécurité

**Environment Variables :**

```bash
# Ne jamais commiter les secrets
# Utiliser AWS Secrets Manager, Google Secret Manager, ou Vault

# .env.production (exemple)
DATABASE_URL=postgresql://user:${DB_PASSWORD}@host/db
API_KEY=${SECURE_API_KEY}
REDIS_PASSWORD=${REDIS_PASSWORD}
```

**Rate Limiting :**

```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/search/keyword")
@limiter.limit("10/minute")
async def search_keyword(request: Request):
    ...
```

**HTTPS Only :**

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## CI/CD Pipeline

### GitHub Actions

`.github/workflows/deploy.yml` :

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker images
      run: |
        docker build -f docker/Dockerfile.backend -t luxury-backend .
        docker build -f docker/Dockerfile.frontend -t luxury-frontend .

    - name: Push to Registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag luxury-backend ${{ secrets.DOCKER_USERNAME }}/luxury-backend:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/luxury-backend:latest

    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /opt/luxury-ai-search
          docker-compose pull
          docker-compose up -d
```

---

## Backup et Recovery

### Backup Redis

```bash
# Script de backup
#!/bin/bash
BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec luxury-redis redis-cli BGSAVE
docker cp luxury-redis:/data/dump.rdb $BACKUP_DIR/dump_$DATE.rdb

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "dump_*.rdb" -mtime +7 -delete
```

### Backup Modèles

```bash
# Versioning des modèles
aws s3 sync models/ s3://luxury-models-backup/$(date +%Y%m%d)/
```

---

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale backend=5

# Kubernetes
kubectl scale deployment luxury-backend --replicas=10

# Auto-scaling
kubectl autoscale deployment luxury-backend --min=3 --max=10 --cpu-percent=70
```

### Load Balancing

**Nginx Load Balancer :**

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

---

## Maintenance

### Updates

```bash
# Zero-downtime deployment
docker-compose up -d --no-deps --build backend

# Rolling update Kubernetes
kubectl set image deployment/luxury-backend backend=luxury-backend:v2
kubectl rollout status deployment/luxury-backend

# Rollback si nécessaire
kubectl rollout undo deployment/luxury-backend
```

### Health Checks

```bash
# Script de monitoring
#!/bin/bash
curl -f http://localhost:8000/api/v1/health || {
    echo "Backend unhealthy!"
    # Alerting (Slack, email, etc.)
}
```

---

## Checklist Pré-Production

- [ ] Variables d'environnement configurées
- [ ] Secrets sécurisés (pas dans le code)
- [ ] HTTPS activé
- [ ] Rate limiting configuré
- [ ] Monitoring en place (Prometheus/Grafana)
- [ ] Logs centralisés
- [ ] Backup automatisé
- [ ] Health checks configurés
- [ ] CI/CD pipeline testé
- [ ] Load testing effectué
- [ ] Documentation à jour
- [ ] Plan de rollback préparé

---

## Support Production

Contact : technical-team@company.com
