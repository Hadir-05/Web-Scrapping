"""
Module de similarité d'images basé sur CLIP
Utilise OpenCLIP pour des embeddings de haute qualité
"""
import os
from pathlib import Path
from typing import Optional
import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

try:
    import open_clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️ open_clip not available, install with: pip install open-clip-torch")


# ========= CONFIG =========
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".avif"}


def is_image_file(filename):
    """Vérifie si un fichier est une image valide selon son extension"""
    return Path(filename).suffix.lower() in VALID_EXTS


def load_clip_model(
    model_name: str = "ViT-L-14",
    pretrained: str = "laion2b_s32b_b82k",
    device=DEVICE
):
    """
    Charge le modèle CLIP avec OpenCLIP

    Args:
        model_name: Nom du modèle (ViT-L-14, ViT-B-32, etc.)
        pretrained: Dataset de pré-entraînement
        device: CPU ou CUDA

    Returns:
        model, preprocess, tokenizer
    """
    if not CLIP_AVAILABLE:
        raise ImportError("open_clip not installed. Install with: pip install open-clip-torch")

    model, _, preprocess = open_clip.create_model_and_transforms(
        model_name,
        pretrained=pretrained,
        device=device
    )

    tokenizer = open_clip.get_tokenizer(model_name)

    return model, preprocess, tokenizer


def compute_embedding(model, preprocess, image: Image.Image, device=DEVICE):
    """
    Calcule l'embedding CLIP d'une image

    Args:
        model: Modèle CLIP
        preprocess: Fonction de prétraitement
        image: Image PIL
        device: CPU ou CUDA

    Returns:
        Embedding normalisé (torch.Tensor)
    """
    # Prétraiter l'image
    image_input = preprocess(image).unsqueeze(0).to(device)

    # Calculer l'embedding
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        # Normaliser
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

    return image_features


class CLIPSimilarityModel:
    """
    Modèle de similarité basé sur CLIP
    Calcule la similarité cosinus entre embeddings d'images
    """

    def __init__(
        self,
        ref_img: Optional[str] = None,
        model_name: str = "ViT-L-14",
        pretrained: str = "laion2b_s32b_b82k"
    ):
        """
        Initialise le modèle CLIP

        Args:
            ref_img: Chemin vers l'image de référence (optionnel)
            model_name: Nom du modèle CLIP
            pretrained: Dataset de pré-entraînement
        """
        print(f"🔧 Chargement du modèle CLIP: {model_name} ({pretrained})")
        print(f"   Device: {DEVICE}")

        self.clip_model, self.preprocess, self.tokenizer = load_clip_model(
            model_name=model_name,
            pretrained=pretrained,
            device=DEVICE
        )

        self.ref_img = ref_img
        self.ref_feat = None

        if ref_img is not None:
            print(f"   📸 Calcul de l'embedding de référence: {ref_img}")
            self.ref_feat = self.compute_features(ref_img)

        print("✅ Modèle CLIP chargé avec succès")

    def compute_features(self, img_path: str) -> np.ndarray:
        """
        Calcule les features CLIP d'une image

        Args:
            img_path: Chemin vers l'image

        Returns:
            Features normalisées (numpy array)
        """
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        print(f"      [CLIP] Computing features for: {img_path}")
        img = Image.open(img_path).convert("RGB")
        print(f"      [CLIP] Image size: {img.size}")
        feat = compute_embedding(self.clip_model, self.preprocess, img, device=DEVICE)
        print(f"      [CLIP] Feature shape: {feat.shape}")
        return feat.cpu().numpy()

    def similarity(self, img_in: str, img_ref: Optional[str] = None) -> float:
        """
        Calcule la similarité cosinus entre deux images via CLIP

        Args:
            img_in: Chemin vers l'image à comparer
            img_ref: Chemin vers l'image de référence (optionnel, utilise self.ref_img si None)

        Returns:
            Score de similarité (0-1, 1 = identique)
        """
        print(f"    [CLIP] Calculating similarity...")
        print(f"    [CLIP] Image in: {img_in}")

        # Calculer les features de l'image d'entrée
        feat1 = self.compute_features(img_in)

        # Gérer l'image de référence
        if img_ref is None:
            img_ref = self.ref_img

        if img_ref is None:
            raise ValueError("No reference image specified")

        print(f"    [CLIP] Image ref: {img_ref}")

        # Calculer les features de référence si nécessaire
        if self.ref_feat is None or self.ref_img != img_ref:
            self.ref_img = img_ref
            self.ref_feat = self.compute_features(self.ref_img)

        # Similarité cosinus
        sim = cosine_similarity(feat1, self.ref_feat)[0][0]
        print(f"    [CLIP] Similarity score: {sim:.4f}")

        return float(sim)

    def batch_similarity(self, img_paths: list, img_ref: Optional[str] = None) -> list:
        """
        Calcule la similarité pour un batch d'images

        Args:
            img_paths: Liste de chemins d'images
            img_ref: Image de référence (optionnel)

        Returns:
            Liste de scores de similarité
        """
        scores = []

        # Préparer la référence
        if img_ref is None:
            img_ref = self.ref_img

        if img_ref is None:
            raise ValueError("No reference image specified")

        if self.ref_feat is None or self.ref_img != img_ref:
            self.ref_img = img_ref
            self.ref_feat = self.compute_features(self.ref_img)

        # Calculer les similarités
        for img_path in img_paths:
            try:
                if os.path.exists(img_path):
                    feat = self.compute_features(img_path)
                    sim = cosine_similarity(feat, self.ref_feat)[0][0]
                    scores.append(float(sim))
                else:
                    scores.append(0.0)
            except Exception as e:
                print(f"⚠️ Erreur pour {img_path}: {e}")
                scores.append(0.0)

        return scores


# Alias pour compatibilité avec le code fourni
GenericSimilarityModel = CLIPSimilarityModel
