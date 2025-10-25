"""
Configuration FastAPI Backend
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Configuration de l'application"""

    # Application
    APP_NAME: str = "Luxury AI Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # Models
    KEYWORD_MODEL_PATH: str = "../models/keyword_search.pth"
    IMAGE_MODEL_PATH: str = "../models/image_similarity.pth"
    DEVICE: str = "cpu"  # 'cuda' si GPU disponible
    MODEL_CACHE_TTL: int = 3600  # secondes

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
    ]

    # Security
    API_KEY: str = "your_secure_api_key_here"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale des settings
settings = Settings()

# Chemins absolus
BASE_DIR = Path(__file__).parent.parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
KEYWORD_MODEL_PATH = MODELS_DIR / "keyword_search.pth"
IMAGE_MODEL_PATH = MODELS_DIR / "image_similarity.pth"
