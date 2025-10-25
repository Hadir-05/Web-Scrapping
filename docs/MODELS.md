# Guide d'Intégration des Modèles

## Format des Modèles

Ce projet supporte les modèles PyTorch au format `.pth`.

### Placement

```
models/
├── keyword_search.pth      # Modèle de recherche textuelle
└── image_similarity.pth    # Modèle de recherche d'images
```

---

## Adapter Vos Modèles

### Structure Attendue

Les modèles peuvent être dans deux formats :

#### Format 1 : Modèle Complet

```python
import torch

# Sauvegarder
torch.save(model, 'keyword_search.pth')

# Charger (dans le code)
model = torch.load('keyword_search.pth', map_location='cpu')
model.eval()
```

#### Format 2 : State Dict

```python
# Sauvegarder
torch.save(model.state_dict(), 'keyword_search.pth')

# Charger (à adapter dans le code)
model = YourModelClass()
model.load_state_dict(torch.load('keyword_search.pth'))
model.eval()
```

---

## Modèle de Recherche par Mots-Clés

### Spécifications

**Entrée :** Texte (string)
**Sortie :** Embeddings ou liste de résultats

### Interface Attendue

Votre modèle doit implémenter (ou vous devez adapter le code) :

```python
def search_by_keyword(model, query: str, top_k: int) -> List[dict]:
    """
    Recherche par mots-clés

    Args:
        model: Modèle PyTorch chargé
        query: Requête textuelle
        top_k: Nombre de résultats

    Returns:
        List[dict]: [
            {
                "product_id": str,
                "name": str,
                "description": str,
                "price": float,
                "image_url": str,
                "score": float  # 0-1
            }
        ]
    """
    # 1. Encoder la requête
    embeddings = model.encode(query)

    # 2. Rechercher dans la base de données
    results = search_in_database(embeddings, top_k)

    # 3. Retourner les résultats formatés
    return results
```

### Fichiers à Modifier

**Streamlit :**
```python
# streamlit_app/models/model_manager.py
def search_by_keyword(_self, query: str, top_k: int = 10) -> list:
    # Remplacer le code PLACEHOLDER par votre logique
    model = _self.get_keyword_model()

    # Votre code ici
    embeddings = model.encode(query)
    results = search_database(embeddings, top_k)

    return results
```

**FastAPI :**
```python
# backend/app/api/routes.py
async def search_by_keyword(request: KeywordSearchRequest):
    model = await get_keyword_model()

    # Votre code ici
    embeddings = model.encode(request.query)
    results = search_database(embeddings, request.top_k)

    return SearchResponse(...)
```

---

## Modèle de Recherche par Image

### Spécifications

**Entrée :** Image (bytes ou PIL.Image)
**Sortie :** Features ou liste de résultats similaires

### Interface Attendue

```python
def search_by_image(model, image_data: bytes, top_k: int) -> List[dict]:
    """
    Recherche par image

    Args:
        model: Modèle PyTorch chargé
        image_data: Données de l'image
        top_k: Nombre de résultats

    Returns:
        List[dict]: [
            {
                "product_id": str,
                "name": str,
                "description": str,
                "price": float,
                "image_url": str,
                "similarity": float  # 0-1
            }
        ]
    """
    # 1. Prétraiter l'image
    image = preprocess_image(image_data)

    # 2. Extraire les features
    features = model.extract_features(image)

    # 3. Rechercher images similaires
    results = find_similar_images(features, top_k)

    return results
```

### Prétraitement d'Image

Exemple de prétraitement :

```python
from PIL import Image
import io
import torch
from torchvision import transforms

def preprocess_image(image_data: bytes) -> torch.Tensor:
    """Prétraite une image pour le modèle"""
    # Charger l'image
    image = Image.open(io.BytesIO(image_data)).convert('RGB')

    # Transformer
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return transform(image).unsqueeze(0)
```

### Fichiers à Modifier

**Streamlit :**
```python
# streamlit_app/models/model_manager.py
def search_by_image(_self, image_data: bytes, top_k: int = 10) -> list:
    model = _self.get_image_model()

    # Prétraiter
    image_tensor = preprocess_image(image_data)

    # Extraire features
    with torch.no_grad():
        features = model(image_tensor)

    # Rechercher
    results = find_similar_images(features, top_k)

    return results
```

**FastAPI :**
```python
# backend/app/api/routes.py
async def search_by_image_upload(file: UploadFile, top_k: int):
    image_data = await file.read()
    model = await get_image_model()

    # Votre logique ici
    image_tensor = preprocess_image(image_data)
    features = model(image_tensor)
    results = find_similar_images(features, top_k)

    return SearchResponse(...)
```

---

## Base de Données de Produits

### Format Attendu

Vos résultats doivent retourner des dictionnaires avec ces champs :

```python
{
    "product_id": "LUX-001",           # ID unique
    "name": "Nom du Produit",          # Nom
    "description": "Description...",   # Description (optionnel)
    "price": 2500.0,                   # Prix en euros
    "image_url": "https://...",        # URL de l'image
    "score": 0.95,                     # Score keyword (0-1)
    # OU
    "similarity": 0.98                 # Score image (0-1)
}
```

### Stockage Recommandé

Pour de meilleures performances :

#### Option 1 : Base Vectorielle (Recommandé)

```bash
# Installer
pip install faiss-cpu  # ou faiss-gpu

# Utiliser
import faiss
import numpy as np

# Créer l'index
dimension = 512  # dimension de vos embeddings
index = faiss.IndexFlatIP(dimension)  # Inner Product

# Ajouter des embeddings
embeddings_matrix = np.array([...])  # shape: (n_products, dimension)
index.add(embeddings_matrix)

# Rechercher
query_embedding = model.encode(query)
distances, indices = index.search(query_embedding, k=10)
```

#### Option 2 : Base de Données SQL

```python
import sqlite3

# Créer la base
conn = sqlite3.connect('products.db')
c = conn.cursor()

c.execute('''
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    image_url TEXT,
    embeddings BLOB
)
''')
```

#### Option 3 : JSON (Démo uniquement)

```python
import json

products = [
    {
        "product_id": "LUX-001",
        "name": "Sac à Main",
        "embeddings": [0.1, 0.2, ...],
        ...
    }
]

with open('products.json', 'w') as f:
    json.dump(products, f)
```

---

## Optimisation des Modèles

### Quantization

Pour réduire la taille et augmenter la vitesse :

```python
import torch

# Charger le modèle
model = torch.load('keyword_search.pth')

# Quantization dynamique
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Sauvegarder
torch.save(quantized_model, 'keyword_search_quantized.pth')
```

### TorchScript

Pour déploiement optimisé :

```python
# Tracer le modèle
example_input = torch.randn(1, 512)
traced_model = torch.jit.trace(model, example_input)

# Sauvegarder
traced_model.save('keyword_search_traced.pt')

# Charger
model = torch.jit.load('keyword_search_traced.pt')
```

### ONNX

Pour interopérabilité :

```python
import torch.onnx

dummy_input = torch.randn(1, 512)
torch.onnx.export(
    model,
    dummy_input,
    "keyword_search.onnx",
    input_names=['input'],
    output_names=['output']
)
```

---

## Utilisation GPU

### Configuration

Modifier `.env` :

```bash
DEVICE=cuda
```

### Code

Le code détecte automatiquement le device, mais vous pouvez forcer :

```python
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
```

### Docker avec GPU

Modifier `docker-compose.yml` :

```yaml
services:
  backend:
    runtime: nvidia
    environment:
      - DEVICE=cuda
```

---

## Tests de Performance

### Benchmark

```python
import time
import torch

model = torch.load('keyword_search.pth')
model.eval()

# Warm-up
for _ in range(10):
    _ = model.encode("test query")

# Benchmark
start = time.time()
for _ in range(100):
    results = model.encode("test query")
end = time.time()

print(f"Temps moyen: {(end - start) / 100 * 1000:.2f}ms")
```

---

## Exemples Complets

Consultez :
- `streamlit_app/models/model_manager.py` pour Streamlit
- `backend/app/api/routes.py` pour FastAPI

Les sections marquées `PLACEHOLDER` indiquent où insérer votre code.

---

## Support

Pour toute question sur l'intégration de vos modèles, contactez l'équipe technique.
