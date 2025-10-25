"""
Routes API FastAPI
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import logging

from ..schemas import (
    KeywordSearchRequest,
    ImageSearchRequest,
    SearchResponse,
    ProductResult,
    HealthResponse
)
from ..models import get_model_loader
from ..core import settings, KEYWORD_MODEL_PATH, IMAGE_MODEL_PATH

logger = logging.getLogger(__name__)

router = APIRouter()

# Variables pour stocker les modèles chargés
_keyword_model = None
_image_model = None


async def get_keyword_model():
    """Récupère le modèle keyword (charge si nécessaire)"""
    global _keyword_model
    if _keyword_model is None:
        loader = get_model_loader()
        _keyword_model = loader.load_model(
            model_path=str(KEYWORD_MODEL_PATH),
            model_key="keyword_search_model",
            cache_ttl=settings.MODEL_CACHE_TTL
        )
    return _keyword_model


async def get_image_model():
    """Récupère le modèle image (charge si nécessaire)"""
    global _image_model
    if _image_model is None:
        loader = get_model_loader()
        _image_model = loader.load_model(
            model_path=str(IMAGE_MODEL_PATH),
            model_key="image_similarity_model",
            cache_ttl=settings.MODEL_CACHE_TTL
        )
    return _image_model


@router.get("/", tags=["Root"])
async def root():
    """Endpoint racine"""
    return {
        "message": "Luxury AI Search API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check de l'API
    Vérifie le statut des modèles et Redis
    """
    try:
        loader = get_model_loader()
        redis_connected = loader.cache.redis_client is not None

        # Vérifier si modèles peuvent être chargés
        models_loaded = (
            KEYWORD_MODEL_PATH.exists() and
            IMAGE_MODEL_PATH.exists()
        )

        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            models_loaded=models_loaded,
            redis_connected=redis_connected
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            models_loaded=False,
            redis_connected=False
        )


@router.post("/search/keyword", response_model=SearchResponse, tags=["Search"])
async def search_by_keyword(request: KeywordSearchRequest):
    """
    Recherche par mots-clés

    Args:
        request: Requête de recherche

    Returns:
        Résultats de recherche
    """
    try:
        logger.info(f"🔍 Recherche keyword: '{request.query}'")

        # Charger le modèle
        model = await get_keyword_model()

        # PLACEHOLDER: Remplacez par votre logique de recherche
        # Exemple:
        # embeddings = model.encode(request.query)
        # results_data = search_in_database(embeddings, top_k=request.top_k)

        # Résultats simulés pour la démo
        results = [
            ProductResult(
                product_id=f"LUX-{i+1:03d}",
                name=f"Produit de Luxe {i+1}",
                description=f"Description pour '{request.query}'",
                price=1000.0 + (i * 100),
                image_url=f"https://via.placeholder.com/300x300?text=Product+{i+1}",
                score=0.95 - (i * 0.05)
            )
            for i in range(request.top_k)
        ]

        return SearchResponse(
            success=True,
            results=results,
            total_results=len(results),
            search_type="keyword"
        )

    except Exception as e:
        logger.error(f"Erreur recherche keyword: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/image/upload", response_model=SearchResponse, tags=["Search"])
async def search_by_image_upload(
    file: UploadFile = File(..., description="Image à rechercher"),
    top_k: int = 10
):
    """
    Recherche par image (upload)

    Args:
        file: Fichier image
        top_k: Nombre de résultats

    Returns:
        Résultats de recherche
    """
    try:
        # Valider le type de fichier
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image"
            )

        logger.info(f"🖼️ Recherche image: {file.filename}")

        # Lire l'image
        image_data = await file.read()

        # Charger le modèle
        model = await get_image_model()

        # PLACEHOLDER: Remplacez par votre logique de recherche
        # Exemple:
        # features = model.extract_features(image_data)
        # results_data = find_similar_images(features, top_k=top_k)

        # Résultats simulés
        results = [
            ProductResult(
                product_id=f"LUX-IMG-{i+1:03d}",
                name=f"Produit Similaire {i+1}",
                description="Produit similaire à votre image",
                price=1500.0 + (i * 150),
                image_url=f"https://via.placeholder.com/300x300?text=Similar+{i+1}",
                similarity=0.98 - (i * 0.05)
            )
            for i in range(top_k)
        ]

        return SearchResponse(
            success=True,
            results=results,
            total_results=len(results),
            search_type="image"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur recherche image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/image/url", response_model=SearchResponse, tags=["Search"])
async def search_by_image_url(request: ImageSearchRequest):
    """
    Recherche par image (URL)

    Args:
        request: Requête avec URL image

    Returns:
        Résultats de recherche
    """
    try:
        logger.info(f"🖼️ Recherche image URL: {request.image_url}")

        # Charger le modèle
        model = await get_image_model()

        # PLACEHOLDER: Télécharger l'image depuis URL et rechercher
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(request.image_url)
        #     image_data = response.content
        # features = model.extract_features(image_data)
        # results_data = find_similar_images(features, top_k=request.top_k)

        # Résultats simulés
        results = [
            ProductResult(
                product_id=f"LUX-URL-{i+1:03d}",
                name=f"Produit Similaire {i+1}",
                description="Produit similaire à l'image URL",
                price=1800.0 + (i * 180),
                image_url=f"https://via.placeholder.com/300x300?text=URLSimilar+{i+1}",
                similarity=0.96 - (i * 0.05)
            )
            for i in range(request.top_k)
        ]

        return SearchResponse(
            success=True,
            results=results,
            total_results=len(results),
            search_type="image_url"
        )

    except Exception as e:
        logger.error(f"Erreur recherche image URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
