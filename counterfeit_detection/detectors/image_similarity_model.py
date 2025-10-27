"""
Image Similarity Model using Pre-trained ResNet
Modèle de similarité d'images utilisant ResNet pré-entraîné sur ImageNet
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageSimilarityModel:
    """
    Modèle de similarité d'images basé sur ResNet50 pré-entraîné
    """

    def __init__(self, device='cpu'):
        """
        Initialise le modèle

        Args:
            device: 'cpu' ou 'cuda'
        """
        self.device = torch.device(device)
        logger.info(f"Initializing ImageSimilarityModel on {self.device}")

        # Charger ResNet50 pré-entraîné
        self.model = models.resnet50(pretrained=True)

        # Retirer la dernière couche (classification)
        # On garde juste l'extracteur de features
        self.model = nn.Sequential(*list(self.model.children())[:-1])

        self.model.to(self.device)
        self.model.eval()

        # Transformation standard pour ImageNet
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        logger.info("✅ ImageSimilarityModel initialized successfully")

    def load_image(self, image_source):
        """
        Charge une image depuis URL ou chemin local

        Args:
            image_source: URL (str) ou Image PIL

        Returns:
            PIL Image
        """
        if isinstance(image_source, str):
            # C'est une URL ou un chemin
            if image_source.startswith('http'):
                # Télécharger depuis URL
                try:
                    response = requests.get(image_source, timeout=10)
                    image = Image.open(BytesIO(response.content)).convert('RGB')
                except Exception as e:
                    logger.error(f"Error loading image from URL: {str(e)}")
                    return None
            else:
                # Charger depuis fichier local
                try:
                    image = Image.open(image_source).convert('RGB')
                except Exception as e:
                    logger.error(f"Error loading image from file: {str(e)}")
                    return None
        elif isinstance(image_source, Image.Image):
            image = image_source.convert('RGB')
        else:
            logger.error(f"Invalid image source type: {type(image_source)}")
            return None

        return image

    def extract_features(self, image_source):
        """
        Extrait les features d'une image

        Args:
            image_source: URL, chemin, ou Image PIL

        Returns:
            Tensor de features (1, 2048)
        """
        # Charger l'image
        image = self.load_image(image_source)
        if image is None:
            return None

        # Appliquer les transformations
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Extraire les features
        with torch.no_grad():
            features = self.model(image_tensor)
            features = features.squeeze()

        return features

    def compute_similarity(self, image1_source, image2_source):
        """
        Calcule la similarité entre deux images

        Args:
            image1_source: Première image (URL, chemin, ou PIL)
            image2_source: Deuxième image (URL, chemin, ou PIL)

        Returns:
            Score de similarité entre 0 et 1 (1 = identique)
        """
        # Extraire les features des deux images
        features1 = self.extract_features(image1_source)
        features2 = self.extract_features(image2_source)

        if features1 is None or features2 is None:
            logger.warning("Failed to extract features from one or both images")
            return 0.0

        # Normaliser les features
        features1 = F.normalize(features1, dim=0)
        features2 = F.normalize(features2, dim=0)

        # Calculer la similarité cosinus
        similarity = F.cosine_similarity(features1.unsqueeze(0), features2.unsqueeze(0))
        similarity = float(similarity.item())

        # Convertir de [-1, 1] à [0, 1]
        similarity = (similarity + 1) / 2

        return similarity

    def find_most_similar(self, query_image, candidate_images, top_k=5):
        """
        Trouve les images les plus similaires à une image de requête

        Args:
            query_image: Image de requête
            candidate_images: Liste d'images candidates
            top_k: Nombre de résultats à retourner

        Returns:
            Liste de tuples (index, similarity_score)
        """
        # Extraire features de l'image de requête
        query_features = self.extract_features(query_image)
        if query_features is None:
            return []

        query_features = F.normalize(query_features, dim=0)

        similarities = []

        # Calculer similarité avec chaque candidate
        for idx, candidate in enumerate(candidate_images):
            candidate_features = self.extract_features(candidate)
            if candidate_features is None:
                similarities.append((idx, 0.0))
                continue

            candidate_features = F.normalize(candidate_features, dim=0)

            # Similarité cosinus
            similarity = F.cosine_similarity(
                query_features.unsqueeze(0),
                candidate_features.unsqueeze(0)
            )
            similarity = float(similarity.item())
            similarity = (similarity + 1) / 2  # Normaliser à [0, 1]

            similarities.append((idx, similarity))

        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Retourner top_k
        return similarities[:top_k]


# Factory function pour créer le modèle
def create_image_similarity_model(device='cpu'):
    """
    Crée et retourne un modèle de similarité d'images

    Args:
        device: 'cpu' ou 'cuda'

    Returns:
        ImageSimilarityModel instance
    """
    try:
        model = ImageSimilarityModel(device=device)
        return model
    except Exception as e:
        logger.error(f"Failed to create ImageSimilarityModel: {str(e)}")
        return None


if __name__ == "__main__":
    # Test rapide
    print("🧪 Testing ImageSimilarityModel...")

    model = create_image_similarity_model()

    if model:
        print("✅ Model created successfully!")

        # Test avec deux URLs d'images
        print("\n📸 Testing image similarity...")

        # Exemple: deux images similaires
        img1 = "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Image1"
        img2 = "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Image2"

        similarity = model.compute_similarity(img1, img2)
        print(f"Similarity: {similarity:.2%}")

        print("\n✅ Test complete!")
    else:
        print("❌ Failed to create model")
