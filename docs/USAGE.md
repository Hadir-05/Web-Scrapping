# Guide d'Utilisation

## Streamlit MVP

### Lancement

```bash
cd streamlit_app
streamlit run app.py
```

### Utilisation

#### Recherche par Mots-Clés

1. Sélectionner "🔤 Recherche par Mots-Clés" dans la sidebar
2. Entrer votre requête (ex: "sac à main en cuir noir")
3. Cliquer sur "🔍 Rechercher"
4. Les résultats s'affichent avec :
   - Image du produit
   - Nom et description
   - Score de pertinence
   - Prix

#### Recherche par Image

1. Sélectionner "🖼️ Recherche par Image" dans la sidebar
2. Uploader une image ou fournir une URL
3. Cliquer sur "🔍 Rechercher des produits similaires"
4. Les résultats similaires s'affichent avec scores de similarité

#### Paramètres

Dans la sidebar :
- **Nombre de résultats** : Ajuster le slider (5-20)
- **Statistiques** : Voir l'état des modèles et du device

---

## Frontend React

### Lancement

```bash
cd frontend
npm start
```

### Interface

#### Page d'Accueil - Recherche Texte

1. Naviguer vers http://localhost:3000
2. Utiliser la barre de recherche en haut
3. Entrer votre requête
4. Cliquer sur "Rechercher"
5. Les résultats s'affichent en grille élégante

**Exemple de requêtes :**
- "montre suisse automatique"
- "sac à main Hermès"
- "parfum floral féminin"
- "bijoux en or 18 carats"

#### Recherche par Image

1. Cliquer sur "Recherche Image" dans la navbar
2. Deux options :
   - **Drag & Drop** : Glisser-déposer une image
   - **Cliquer** : Ouvrir le sélecteur de fichier
3. L'image est analysée automatiquement
4. Les produits similaires s'affichent

**Formats supportés :**
- JPG / JPEG
- PNG
- Max 10 MB

---

## API Backend

### Accéder à la Documentation

Une fois le backend lancé :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints Principaux

#### 1. Health Check

```bash
GET /api/v1/health
```

Réponse :
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "redis_connected": true
}
```

#### 2. Recherche par Mots-Clés

```bash
POST /api/v1/search/keyword
Content-Type: application/json

{
  "query": "sac à main en cuir",
  "top_k": 10
}
```

Réponse :
```json
{
  "success": true,
  "results": [
    {
      "product_id": "LUX-001",
      "name": "Sac Classique",
      "description": "Sac en cuir italien",
      "price": 2500.0,
      "image_url": "https://...",
      "score": 0.95
    }
  ],
  "total_results": 10,
  "search_type": "keyword"
}
```

#### 3. Recherche par Image (Upload)

```bash
POST /api/v1/search/image/upload?top_k=10
Content-Type: multipart/form-data

file: [image file]
```

#### 4. Recherche par Image (URL)

```bash
POST /api/v1/search/image/url
Content-Type: application/json

{
  "image_url": "https://example.com/product.jpg",
  "top_k": 10
}
```

### Exemples avec cURL

```bash
# Recherche keyword
curl -X POST http://localhost:8000/api/v1/search/keyword \
  -H "Content-Type: application/json" \
  -d '{
    "query": "montre suisse",
    "top_k": 5
  }'

# Upload d'image
curl -X POST http://localhost:8000/api/v1/search/image/upload?top_k=5 \
  -F "file=@/path/to/image.jpg"

# Recherche par URL
curl -X POST http://localhost:8000/api/v1/search/image/url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/product.jpg",
    "top_k": 5
  }'
```

### Exemples avec Python

```python
import requests

# Recherche keyword
response = requests.post(
    "http://localhost:8000/api/v1/search/keyword",
    json={"query": "sac à main", "top_k": 10}
)
results = response.json()

# Upload d'image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/search/image/upload?top_k=10",
        files={"file": f}
    )
results = response.json()
```

---

## Performance et Cache

### Cache des Modèles

**Streamlit :**
- Modèles chargés avec `@st.cache_resource`
- Restent en mémoire pendant toute la session
- Premier appel : ~2-3 secondes
- Appels suivants : <100ms

**FastAPI + Redis :**
- Modèles stockés dans Redis
- Persistants entre redémarrages
- TTL configurable (défaut : 1h)
- Fallback sur cache local si Redis indisponible

### Monitoring

```bash
# Voir les logs Streamlit
streamlit run app.py --logger.level debug

# Voir les logs FastAPI
uvicorn main:app --log-level debug

# Voir l'utilisation Redis
docker exec -it luxury-redis redis-cli
> INFO memory
> KEYS *
```

---

## Personnalisation

### Modifier le Nombre de Résultats

**Streamlit :** Utiliser le slider dans la sidebar

**React :** Les requêtes sont limitées à 12 par défaut, modifiable dans le code

**API :** Paramètre `top_k` dans les requêtes

### Modifier le Design

**Streamlit :** Éditer `streamlit_app/utils/helpers.py` - fonction `apply_custom_css()`

**React :** Éditer `frontend/tailwind.config.js` et les composants

### Ajouter des Filtres

Vous pouvez étendre les schémas Pydantic dans `backend/app/schemas/search.py` pour ajouter :
- Filtres de prix
- Filtres de catégorie
- Tri personnalisé

---

## Cas d'Usage Recommandés

### Pour Démo Client
→ Utiliser **Streamlit MVP**
- Rapide à lancer
- Interface complète
- Pas de configuration complexe

### Pour Développement/Test
→ Utiliser **FastAPI + React en mode dev**
- Hot reload
- Debugging facile
- Tests API avec Swagger

### Pour Production
→ Utiliser **Docker Compose**
- Tous les services orchestrés
- Scalable
- Health checks automatiques

---

## Support

Pour toute question :
1. Vérifier les logs
2. Consulter [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Contacter l'équipe technique
