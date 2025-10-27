"""
Système avancé de similarité d'images combinant plusieurs techniques

Méthodes utilisées:
1. CLIP (OpenAI) - Similarité sémantique profonde (50% du score)
2. pHash - Perceptual hashing pour images quasi-identiques (30% du score)
3. ORB - Features géométriques pour transformations (20% du score)

Ce système est BEAUCOUP plus performant que ResNet50 seul pour trouver
des produits similaires, même avec variations de luminosité, angle, taille, etc.
"""

import logging
from typing import Union, Optional, Tuple
import numpy as np
from PIL import Image
import io
import requests

logger = logging.getLogger(__name__)

# Initialiser les flags de disponibilité
CLIP_AVAILABLE = False
PHASH_AVAILABLE = False
ORB_AVAILABLE = False

# Tentative d'import des librairies
try:
    import torch
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    logger.warning("CLIP non disponible. Installez avec: pip install git+https://github.com/openai/CLIP.git")

try:
    import imagehash
    PHASH_AVAILABLE = True
except ImportError:
    logger.warning("imagehash non disponible. Installez avec: pip install imagehash")

try:
    import cv2
    ORB_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV non disponible. Installez avec: pip install opencv-python")


class AdvancedImageSimilarity:
    """
    Système avancé de calcul de similarité d'images

    Combine 3 techniques complémentaires:
    - CLIP: Compréhension sémantique (produits similaires)
    - pHash: Détection d'images quasi-identiques
    - ORB: Détection de features géométriques
    """

    def __init__(
        self,
        device: str = 'cpu',
        clip_weight: float = 0.5,
        phash_weight: float = 0.3,
        orb_weight: float = 0.2
    ):
        """
        Initialise le système de similarité avancé

        Args:
            device: 'cpu' ou 'cuda'
            clip_weight: Poids pour CLIP (défaut: 0.5)
            phash_weight: Poids pour pHash (défaut: 0.3)
            orb_weight: Poids pour ORB (défaut: 0.2)
        """
        self.device = device
        self.clip_weight = clip_weight
        self.phash_weight = phash_weight
        self.orb_weight = orb_weight

        # Normaliser les poids
        total_weight = clip_weight + phash_weight + orb_weight
        self.clip_weight /= total_weight
        self.phash_weight /= total_weight
        self.orb_weight /= total_weight

        logger.info(f"🔧 Initializing Advanced Image Similarity (device: {device})")
        logger.info(f"   └─ Weights: CLIP={self.clip_weight:.1%}, pHash={self.phash_weight:.1%}, ORB={self.orb_weight:.1%}")

        # Initialiser CLIP
        self.clip_model = None
        self.clip_preprocess = None
        if CLIP_AVAILABLE:
            try:
                logger.info("   🔄 Loading CLIP model (ViT-B/32)...")
                self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=device)
                self.clip_model.eval()
                logger.info("   ✅ CLIP loaded successfully")
            except Exception as e:
                logger.error(f"   ❌ Failed to load CLIP: {e}")
                CLIP_AVAILABLE = False

        # Initialiser ORB
        self.orb = None
        if ORB_AVAILABLE:
            try:
                self.orb = cv2.ORB_create(nfeatures=500)
                logger.info("   ✅ ORB initialized")
            except Exception as e:
                logger.error(f"   ❌ Failed to initialize ORB: {e}")

        # Vérifier qu'au moins une méthode est disponible
        if not (CLIP_AVAILABLE or PHASH_AVAILABLE or ORB_AVAILABLE):
            raise RuntimeError(
                "Aucune méthode de similarité disponible! Installez au moins:\n"
                "  - CLIP: pip install git+https://github.com/openai/CLIP.git\n"
                "  - pHash: pip install imagehash\n"
                "  - ORB: pip install opencv-python"
            )

        logger.info("✅ Advanced Image Similarity initialized!")

    def load_image(self, image_source: Union[str, Image.Image]) -> Optional[Image.Image]:
        """
        Charge une image depuis URL, chemin local, ou objet PIL

        Args:
            image_source: URL, chemin fichier, ou PIL.Image

        Returns:
            PIL.Image ou None si erreur
        """
        try:
            if isinstance(image_source, Image.Image):
                return image_source.convert('RGB')

            elif isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    # Charger depuis URL
                    response = requests.get(image_source, timeout=10)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                else:
                    # Charger depuis fichier local
                    image = Image.open(image_source)

                return image.convert('RGB')

            else:
                logger.error(f"Type d'image non supporté: {type(image_source)}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image: {e}")
            return None

    def compute_clip_similarity(
        self,
        image1: Image.Image,
        image2: Image.Image
    ) -> float:
        """
        Calcule la similarité CLIP entre deux images

        CLIP comprend le contenu sémantique des images et est excellent
        pour trouver des produits similaires même avec variations d'angle,
        luminosité, etc.

        Args:
            image1: Première image PIL
            image2: Deuxième image PIL

        Returns:
            Score de similarité (0-1)
        """
        if not CLIP_AVAILABLE or self.clip_model is None:
            return 0.0

        try:
            # Préprocesser les images
            image1_input = self.clip_preprocess(image1).unsqueeze(0).to(self.device)
            image2_input = self.clip_preprocess(image2).unsqueeze(0).to(self.device)

            # Extraire les features
            with torch.no_grad():
                features1 = self.clip_model.encode_image(image1_input)
                features2 = self.clip_model.encode_image(image2_input)

            # Normaliser
            features1 = features1 / features1.norm(dim=-1, keepdim=True)
            features2 = features2 / features2.norm(dim=-1, keepdim=True)

            # Calculer similarité cosine
            similarity = (features1 @ features2.T).item()

            # Normaliser entre 0 et 1
            similarity = (similarity + 1) / 2

            return float(similarity)

        except Exception as e:
            logger.error(f"Erreur CLIP: {e}")
            return 0.0

    def compute_phash_similarity(
        self,
        image1: Image.Image,
        image2: Image.Image
    ) -> float:
        """
        Calcule la similarité perceptual hash entre deux images

        pHash est excellent pour détecter les images quasi-identiques,
        même avec compression, redimensionnement, ou légers ajustements.

        Args:
            image1: Première image PIL
            image2: Deuxième image PIL

        Returns:
            Score de similarité (0-1)
        """
        if not PHASH_AVAILABLE:
            return 0.0

        try:
            # Calculer les hash
            hash1 = imagehash.phash(image1)
            hash2 = imagehash.phash(image2)

            # Distance de Hamming
            distance = hash1 - hash2

            # Normaliser (hash size = 8x8 = 64 bits max)
            # Distance 0 = identique, distance 64 = totalement différent
            similarity = 1.0 - (distance / 64.0)

            return float(max(0.0, similarity))

        except Exception as e:
            logger.error(f"Erreur pHash: {e}")
            return 0.0

    def compute_orb_similarity(
        self,
        image1: Image.Image,
        image2: Image.Image
    ) -> float:
        """
        Calcule la similarité ORB (Oriented FAST and Rotated BRIEF)

        ORB détecte des points clés et est résistant aux rotations,
        changements d'échelle, et transformations géométriques.

        Args:
            image1: Première image PIL
            image2: Deuxième image PIL

        Returns:
            Score de similarité (0-1)
        """
        if not ORB_AVAILABLE or self.orb is None:
            return 0.0

        try:
            # Convertir en numpy array pour OpenCV
            img1_cv = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2GRAY)
            img2_cv = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2GRAY)

            # Détecter keypoints et descripteurs
            kp1, des1 = self.orb.detectAndCompute(img1_cv, None)
            kp2, des2 = self.orb.detectAndCompute(img2_cv, None)

            if des1 is None or des2 is None:
                return 0.0

            # Matcher avec BFMatcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)

            # Trier par distance
            matches = sorted(matches, key=lambda x: x.distance)

            # Calculer le score
            # Plus de matches = plus similaire
            # Distance faible = meilleur match
            if len(matches) == 0:
                return 0.0

            # Prendre les meilleurs matches (top 50%)
            good_matches = matches[:max(1, len(matches) // 2)]

            # Score basé sur nombre de matches et distance moyenne
            num_matches_score = len(good_matches) / max(len(kp1), len(kp2))
            avg_distance = sum(m.distance for m in good_matches) / len(good_matches)
            distance_score = 1.0 - (avg_distance / 100.0)  # Normaliser

            # Combiner
            similarity = (num_matches_score * 0.6 + distance_score * 0.4)

            return float(max(0.0, min(1.0, similarity)))

        except Exception as e:
            logger.error(f"Erreur ORB: {e}")
            return 0.0

    def compute_similarity(
        self,
        image1_source: Union[str, Image.Image],
        image2_source: Union[str, Image.Image],
        return_details: bool = False
    ) -> Union[float, Tuple[float, dict]]:
        """
        Calcule la similarité combinée entre deux images

        Combine CLIP + pHash + ORB avec pondération pour un score optimal.

        Args:
            image1_source: URL, chemin ou PIL.Image de la première image
            image2_source: URL, chemin ou PIL.Image de la deuxième image
            return_details: Si True, retourne aussi les scores individuels

        Returns:
            Score de similarité (0-1), ou (score, détails) si return_details=True
        """
        # Charger les images
        image1 = self.load_image(image1_source)
        image2 = self.load_image(image2_source)

        if image1 is None or image2 is None:
            if return_details:
                return 0.0, {}
            return 0.0

        # Calculer les scores individuels
        scores = {}

        if CLIP_AVAILABLE and self.clip_model is not None:
            scores['clip'] = self.compute_clip_similarity(image1, image2)
        else:
            scores['clip'] = 0.0

        if PHASH_AVAILABLE:
            scores['phash'] = self.compute_phash_similarity(image1, image2)
        else:
            scores['phash'] = 0.0

        if ORB_AVAILABLE and self.orb is not None:
            scores['orb'] = self.compute_orb_similarity(image1, image2)
        else:
            scores['orb'] = 0.0

        # Calculer le score pondéré final
        final_score = (
            scores['clip'] * self.clip_weight +
            scores['phash'] * self.phash_weight +
            scores['orb'] * self.orb_weight
        )

        # Log les détails
        logger.debug(f"Similarity scores: CLIP={scores['clip']:.2%}, pHash={scores['phash']:.2%}, "
                    f"ORB={scores['orb']:.2%} → Final={final_score:.2%}")

        if return_details:
            details = {
                'clip_score': scores['clip'],
                'phash_score': scores['phash'],
                'orb_score': scores['orb'],
                'final_score': final_score,
                'weights': {
                    'clip': self.clip_weight,
                    'phash': self.phash_weight,
                    'orb': self.orb_weight
                }
            }
            return final_score, details

        return final_score


def create_advanced_similarity_model(
    device: str = 'cpu',
    clip_weight: float = 0.5,
    phash_weight: float = 0.3,
    orb_weight: float = 0.2
) -> Optional[AdvancedImageSimilarity]:
    """
    Factory function pour créer un modèle de similarité avancé

    Args:
        device: 'cpu' ou 'cuda'
        clip_weight: Poids pour CLIP (défaut: 0.5)
        phash_weight: Poids pour pHash (défaut: 0.3)
        orb_weight: Poids pour ORB (défaut: 0.2)

    Returns:
        Instance AdvancedImageSimilarity ou None
    """
    try:
        model = AdvancedImageSimilarity(
            device=device,
            clip_weight=clip_weight,
            phash_weight=phash_weight,
            orb_weight=orb_weight
        )
        return model
    except Exception as e:
        logger.error(f"Failed to create advanced similarity model: {e}")
        return None


if __name__ == "__main__":
    # Test rapide
    print("Testing Advanced Image Similarity...")

    model = create_advanced_similarity_model(device='cpu')

    if model:
        print("✅ Model created successfully!")
        print("\nAvailable methods:")
        print(f"  - CLIP: {CLIP_AVAILABLE}")
        print(f"  - pHash: {PHASH_AVAILABLE}")
        print(f"  - ORB: {ORB_AVAILABLE}")
    else:
        print("❌ Failed to create model")
