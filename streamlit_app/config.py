"""
Configuration pour l'application Streamlit
"""
import os
from pathlib import Path

# Chemins des modèles
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
KEYWORD_MODEL_PATH = MODELS_DIR / "keyword_search.pth"
IMAGE_MODEL_PATH = MODELS_DIR / "image_similarity.pth"

# Configuration Device
DEVICE = os.getenv("DEVICE", "cpu")  # 'cuda' si GPU disponible

# Configuration UI
APP_TITLE = "Luxury AI Search"
APP_ICON = "💎"
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Thème Luxe
COLORS = {
    "primary": "#D4AF37",  # Or
    "secondary": "#000000",  # Noir
    "background": "#FFFFFF",  # Blanc
    "text": "#333333"
}

# Paramètres de recherche
MAX_RESULTS = 10
SIMILARITY_THRESHOLD = 0.5
