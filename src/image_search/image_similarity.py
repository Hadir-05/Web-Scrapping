"""
Module de recherche par similarité d'images
"""
import os
from typing import List, Tuple, Optional
from pathlib import Path
import io

from PIL import Image
import imagehash
import numpy as np


class ImageSimilaritySearch:
    """Classe pour la recherche de similarité d'images utilisant le hashing perceptuel"""

    def __init__(self):
        self.image_hashes = {}  # {image_path: hash}
        self.image_info = {}    # {image_path: metadata}

    def add_image(self, image_path: str, metadata: dict = None):
        """
        Ajouter une image à l'index de recherche

        Args:
            image_path: Chemin vers l'image
            metadata: Métadonnées optionnelles associées à l'image
        """
        try:
            img = Image.open(image_path)
            # Calculer plusieurs hashes pour une meilleure précision
            ahash = imagehash.average_hash(img)
            phash = imagehash.phash(img)
            dhash = imagehash.dhash(img)
            whash = imagehash.whash(img)

            # Stocker tous les hashes
            self.image_hashes[image_path] = {
                'ahash': ahash,
                'phash': phash,
                'dhash': dhash,
                'whash': whash
            }

            # Stocker les métadonnées
            self.image_info[image_path] = metadata or {}

        except Exception as e:
            print(f"Erreur lors de l'ajout de l'image {image_path}: {e}")

    def add_images_from_directory(self, directory: str, metadata_func=None):
        """
        Ajouter toutes les images d'un répertoire à l'index

        Args:
            directory: Répertoire contenant les images
            metadata_func: Fonction optionnelle pour générer les métadonnées (prend le chemin en argument)
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        directory_path = Path(directory)

        for image_path in directory_path.glob('*'):
            if image_path.suffix.lower() in image_extensions:
                metadata = metadata_func(str(image_path)) if metadata_func else None
                self.add_image(str(image_path), metadata)

    def search_similar(
        self,
        query_image_path: str,
        top_k: int = 5,
        threshold: int = 10
    ) -> List[Tuple[str, float, dict]]:
        """
        Rechercher les images similaires à l'image de requête

        Args:
            query_image_path: Chemin vers l'image de requête
            top_k: Nombre de résultats à retourner
            threshold: Seuil de distance maximale (plus bas = plus similaire)

        Returns:
            Liste de tuples (chemin_image, score_similarité, métadonnées)
        """
        try:
            query_img = Image.open(query_image_path)

            # Calculer les hashes de l'image de requête
            query_ahash = imagehash.average_hash(query_img)
            query_phash = imagehash.phash(query_img)
            query_dhash = imagehash.dhash(query_img)
            query_whash = imagehash.whash(query_img)

            # Calculer les distances pour toutes les images
            similarities = []
            for image_path, hashes in self.image_hashes.items():
                # Calculer la distance moyenne de tous les hashes
                ahash_dist = query_ahash - hashes['ahash']
                phash_dist = query_phash - hashes['phash']
                dhash_dist = query_dhash - hashes['dhash']
                whash_dist = query_whash - hashes['whash']

                # Distance moyenne pondérée (phash est généralement plus fiable)
                avg_distance = (ahash_dist + 2*phash_dist + dhash_dist + whash_dist) / 5.0

                # Convertir la distance en score de similarité (0-1, 1 = identique)
                # Distance typique est entre 0 et 64 pour un hash de 8x8
                similarity_score = max(0, 1 - (avg_distance / 64.0))

                if avg_distance <= threshold:
                    similarities.append((
                        image_path,
                        similarity_score,
                        self.image_info.get(image_path, {})
                    ))

            # Trier par score de similarité décroissant
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            print(f"Erreur lors de la recherche de similarité: {e}")
            return []

    def search_similar_from_bytes(
        self,
        image_bytes: bytes,
        top_k: int = 5,
        threshold: int = 10
    ) -> List[Tuple[str, float, dict]]:
        """
        Rechercher les images similaires à partir de bytes d'image

        Args:
            image_bytes: Bytes de l'image de requête
            top_k: Nombre de résultats à retourner
            threshold: Seuil de distance maximale

        Returns:
            Liste de tuples (chemin_image, score_similarité, métadonnées)
        """
        try:
            query_img = Image.open(io.BytesIO(image_bytes))

            # Calculer les hashes de l'image de requête
            query_ahash = imagehash.average_hash(query_img)
            query_phash = imagehash.phash(query_img)
            query_dhash = imagehash.dhash(query_img)
            query_whash = imagehash.whash(query_img)

            # Calculer les distances pour toutes les images
            similarities = []
            for image_path, hashes in self.image_hashes.items():
                # Calculer la distance moyenne de tous les hashes
                ahash_dist = query_ahash - hashes['ahash']
                phash_dist = query_phash - hashes['phash']
                dhash_dist = query_dhash - hashes['dhash']
                whash_dist = query_whash - hashes['whash']

                # Distance moyenne pondérée
                avg_distance = (ahash_dist + 2*phash_dist + dhash_dist + whash_dist) / 5.0

                # Convertir la distance en score de similarité
                similarity_score = max(0, 1 - (avg_distance / 64.0))

                if avg_distance <= threshold:
                    similarities.append((
                        image_path,
                        similarity_score,
                        self.image_info.get(image_path, {})
                    ))

            # Trier par score de similarité décroissant
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            print(f"Erreur lors de la recherche de similarité: {e}")
            return []

    def find_duplicates(self, threshold: int = 5) -> List[List[str]]:
        """
        Trouver les images en double dans l'index

        Args:
            threshold: Seuil de distance pour considérer deux images comme duplicata

        Returns:
            Liste de groupes d'images similaires
        """
        duplicates = []
        processed = set()

        for image_path, hashes in self.image_hashes.items():
            if image_path in processed:
                continue

            group = [image_path]
            processed.add(image_path)

            # Comparer avec toutes les autres images
            for other_path, other_hashes in self.image_hashes.items():
                if other_path in processed:
                    continue

                # Calculer la distance moyenne
                ahash_dist = hashes['ahash'] - other_hashes['ahash']
                phash_dist = hashes['phash'] - other_hashes['phash']
                dhash_dist = hashes['dhash'] - other_hashes['dhash']
                whash_dist = hashes['whash'] - other_hashes['whash']

                avg_distance = (ahash_dist + 2*phash_dist + dhash_dist + whash_dist) / 5.0

                if avg_distance <= threshold:
                    group.append(other_path)
                    processed.add(other_path)

            if len(group) > 1:
                duplicates.append(group)

        return duplicates

    def clear(self):
        """Vider l'index de recherche"""
        self.image_hashes.clear()
        self.image_info.clear()

    def get_stats(self) -> dict:
        """Obtenir des statistiques sur l'index"""
        return {
            'total_images': len(self.image_hashes),
            'total_metadata': len(self.image_info)
        }
