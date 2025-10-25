"""
Schémas Pydantic pour les requêtes et réponses de recherche
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class KeywordSearchRequest(BaseModel):
    """Requête de recherche par mots-clés"""
    query: str = Field(..., description="Texte de recherche", min_length=1)
    top_k: int = Field(10, description="Nombre de résultats", ge=1, le=50)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "sac à main en cuir noir",
                "top_k": 10
            }
        }


class ImageSearchRequest(BaseModel):
    """Requête de recherche par image (URL)"""
    image_url: str = Field(..., description="URL de l'image")
    top_k: int = Field(10, description="Nombre de résultats", ge=1, le=50)

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/product.jpg",
                "top_k": 10
            }
        }


class ProductResult(BaseModel):
    """Résultat de recherche de produit"""
    product_id: str = Field(..., description="ID unique du produit")
    name: str = Field(..., description="Nom du produit")
    description: Optional[str] = Field(None, description="Description")
    price: float = Field(..., description="Prix en euros")
    image_url: str = Field(..., description="URL de l'image produit")
    score: Optional[float] = Field(None, description="Score de pertinence (0-1)")
    similarity: Optional[float] = Field(None, description="Score de similarité (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "LUX-001",
                "name": "Sac à Main Classique",
                "description": "Sac en cuir italien premium",
                "price": 2500.0,
                "image_url": "https://example.com/product1.jpg",
                "score": 0.95
            }
        }


class SearchResponse(BaseModel):
    """Réponse de recherche"""
    success: bool = Field(..., description="Statut de la requête")
    results: List[ProductResult] = Field(..., description="Liste des résultats")
    total_results: int = Field(..., description="Nombre total de résultats")
    search_type: str = Field(..., description="Type de recherche (keyword/image)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "results": [
                    {
                        "product_id": "LUX-001",
                        "name": "Sac à Main Classique",
                        "description": "Sac en cuir italien",
                        "price": 2500.0,
                        "image_url": "https://example.com/product1.jpg",
                        "score": 0.95
                    }
                ],
                "total_results": 1,
                "search_type": "keyword"
            }
        }


class HealthResponse(BaseModel):
    """Réponse health check"""
    status: str = Field(..., description="Statut de l'API")
    version: str = Field(..., description="Version de l'API")
    models_loaded: bool = Field(..., description="Modèles chargés")
    redis_connected: bool = Field(..., description="Connexion Redis")
