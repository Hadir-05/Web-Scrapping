"""
FastAPI Application - Luxury AI Search Backend
Backend API pour recherche intelligente de produits de luxe
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Ajouter le chemin parent pour imports
sys.path.append(str(Path(__file__).parent.parent))

from .core import settings
from .models import initialize_model_system
from .api import router

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## API de Recherche AI pour Produits de Luxe

    ### Fonctionnalités:
    - 🔤 **Recherche par mots-clés**: Recherche sémantique intelligente
    - 🖼️ **Recherche par image**: Recherche par similarité visuelle
    - ⚡ **Cache Redis**: Modèles PyTorch en cache pour performance optimale
    - 📊 **Swagger UI**: Documentation interactive

    ### Endpoints Principaux:
    - `/search/keyword` - Recherche par texte
    - `/search/image/upload` - Upload d'image pour recherche
    - `/search/image/url` - Recherche par URL d'image
    - `/health` - Health check
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Événement au démarrage de l'application
    Initialise le système de modèles et le cache Redis
    """
    logger.info("🚀 Démarrage de Luxury AI Search API...")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Device: {settings.DEVICE}")

    # Initialiser le système de modèles avec Redis
    try:
        initialize_model_system(
            redis_host=settings.REDIS_HOST,
            redis_port=settings.REDIS_PORT,
            redis_password=settings.REDIS_PASSWORD,
            device=settings.DEVICE
        )
        logger.info("✅ Système de modèles initialisé")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation modèles: {str(e)}")
        logger.warning("⚠️ L'API continuera sans cache Redis")

    logger.info("✅ API prête à recevoir des requêtes")
    logger.info(f"📖 Documentation: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt de l'application"""
    logger.info("🛑 Arrêt de l'API...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global pour les exceptions"""
    logger.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Erreur interne du serveur",
            "detail": str(exc) if settings.DEBUG else "Contactez l'administrateur"
        }
    )


# Inclure les routes
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine"""
    return {
        "message": "Luxury AI Search API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
