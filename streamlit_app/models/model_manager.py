"""
Gestionnaire de modèles PyTorch avec cache Streamlit
Les modèles sont chargés une seule fois et gardés en mémoire
"""
import torch
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Ajouter le chemin parent pour imports
sys.path.append(str(Path(__file__).parent.parent.parent))


@st.cache_resource
def load_keyword_model(model_path: str, device: str = "cpu"):
    """
    Charge le modèle de recherche par mots-clés
    Utilise @st.cache_resource pour garder le modèle en mémoire

    Args:
        model_path: Chemin vers le fichier .pth
        device: 'cpu' ou 'cuda'

    Returns:
        Modèle PyTorch chargé et en mode eval
    """
    print(f"🔄 Chargement du modèle keyword depuis {model_path}...")

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Modèle non trouvé: {model_path}\n"
            f"Placez votre modèle .pth dans le dossier models/"
        )

    try:
        # Charger le modèle
        model = torch.load(model_path, map_location=device)

        # Si c'est un state_dict, vous devrez adapter selon votre architecture
        # Exemple: model = YourModelClass(); model.load_state_dict(torch.load(...))

        # Mode évaluation
        if hasattr(model, 'eval'):
            model.eval()

        print(f"✅ Modèle keyword chargé avec succès sur {device}")
        return model

    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement du modèle: {str(e)}")


@st.cache_resource
def load_image_model(model_path: str, device: str = "cpu"):
    """
    Charge le modèle de recherche par image
    Utilise @st.cache_resource pour garder le modèle en mémoire

    Args:
        model_path: Chemin vers le fichier .pth
        device: 'cpu' ou 'cuda'

    Returns:
        Modèle PyTorch chargé et en mode eval
    """
    print(f"🔄 Chargement du modèle image depuis {model_path}...")

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Modèle non trouvé: {model_path}\n"
            f"Placez votre modèle .pth dans le dossier models/"
        )

    try:
        # Charger le modèle
        model = torch.load(model_path, map_location=device)

        # Mode évaluation
        if hasattr(model, 'eval'):
            model.eval()

        print(f"✅ Modèle image chargé avec succès sur {device}")
        return model

    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement du modèle: {str(e)}")


class ModelManager:
    """
    Gestionnaire centralisé des modèles avec cache
    """

    def __init__(self, keyword_path: str, image_path: str, device: str = "cpu"):
        self.keyword_path = keyword_path
        self.image_path = image_path
        self.device = device
        self._keyword_model = None
        self._image_model = None

    def get_keyword_model(self):
        """Récupère le modèle keyword (avec cache)"""
        if self._keyword_model is None:
            self._keyword_model = load_keyword_model(self.keyword_path, self.device)
        return self._keyword_model

    def get_image_model(self):
        """Récupère le modèle image (avec cache)"""
        if self._image_model is None:
            self._image_model = load_image_model(self.image_path, self.device)
        return self._image_model

    @st.cache_data
    def search_by_keyword(_self, query: str, top_k: int = 10) -> list:
        """
        Recherche par mots-clés

        Args:
            query: Texte de recherche
            top_k: Nombre de résultats

        Returns:
            Liste de résultats [{product_id, name, score, image_url}, ...]
        """
        # PLACEHOLDER: Remplacez par votre logique de recherche
        print(f"🔍 Recherche keyword: '{query}'")

        # Exemple de résultats simulés
        # Dans votre implémentation réelle, utilisez le modèle:
        # model = _self.get_keyword_model()
        # embeddings = model.encode(query)
        # results = search_in_database(embeddings)

        results = [
            {
                "product_id": f"LUX-{i+1:03d}",
                "name": f"Produit de Luxe {i+1}",
                "description": f"Description pour '{query}'",
                "score": 0.95 - (i * 0.05),
                "price": 1000 + (i * 100),
                "image_url": f"https://via.placeholder.com/300x300?text=Product+{i+1}"
            }
            for i in range(top_k)
        ]

        return results

    @st.cache_data
    def search_by_image(_self, image_data: bytes, top_k: int = 10) -> list:
        """
        Recherche par similarité d'image

        Args:
            image_data: Données de l'image
            top_k: Nombre de résultats

        Returns:
            Liste de résultats [{product_id, name, similarity, image_url}, ...]
        """
        # PLACEHOLDER: Remplacez par votre logique de recherche
        print(f"🖼️ Recherche image similarity...")

        # Exemple de résultats simulés
        # Dans votre implémentation réelle:
        # model = _self.get_image_model()
        # features = model.extract_features(image_data)
        # results = find_similar_images(features)

        results = [
            {
                "product_id": f"LUX-IMG-{i+1:03d}",
                "name": f"Produit Similaire {i+1}",
                "description": "Produit similaire à votre image",
                "similarity": 0.98 - (i * 0.05),
                "price": 1500 + (i * 150),
                "image_url": f"https://via.placeholder.com/300x300?text=Similar+{i+1}"
            }
            for i in range(top_k)
        ]

        return results
