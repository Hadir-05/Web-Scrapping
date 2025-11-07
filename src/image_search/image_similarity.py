"""
Module de recherche par similarité d'images
Utilise CLIP pour des embeddings de haute qualité
"""
import os
from typing import List, Tuple, Optional
from pathlib import Path
import io

from PIL import Image
import numpy as np

# Essayer d'importer CLIP, sinon utiliser le fallback perceptual hashing
try:
    from src.image_search.clip_similarity import CLIPSimilarityModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    try:
        print("CLIP not available, falling back to perceptual hashing")
    except:
        pass  # Ignorer les erreurs d'encodage
    import imagehash


class ImageSimilaritySearch:
    """
    Classe pour la recherche de similarité d'images
    Utilise CLIP si disponible, sinon perceptual hashing
    """

    def __init__(self, use_clip: bool = True):
        """
        Initialise la recherche de similarité

        Args:
            use_clip: Utiliser CLIP si disponible (True par défaut)
        """
        self.use_clip = use_clip and CLIP_AVAILABLE

        if self.use_clip:
            self._safe_print("Utilisation de CLIP pour la similarite d'images")
            self.clip_model = None  # Sera initialisé lors de la première recherche
            self.image_embeddings = {}  # {image_path: embedding}
        else:
            self._safe_print("Utilisation du perceptual hashing pour la similarite")
            self.image_hashes = {}  # {image_path: hash}

        self.image_info = {}    # {image_path: metadata}

    @staticmethod
    def _safe_print(message: str):
        """Print avec gestion des erreurs d'encodage Windows"""
        try:
            print(message)
        except UnicodeEncodeError:
            # Fallback pour Windows avec encodage limité
            try:
                print(message.encode('ascii', 'ignore').decode('ascii'))
            except:
                pass  # Ignorer complètement si ça ne marche toujours pas

    def add_image(self, image_path: str, metadata: dict = None):
        """
        Ajouter une image à l'index de recherche

        Args:
            image_path: Chemin vers l'image
            metadata: Métadonnées optionnelles associées à l'image
        """
        try:
            print(f"  [ImageSearch] Adding: {image_path}")
            if self.use_clip:
                print(f"    [ImageSearch] Using CLIP")
                # Initialiser CLIP si nécessaire
                if self.clip_model is None:
                    print(f"    [ImageSearch] Initializing CLIP model...")
                    self.clip_model = CLIPSimilarityModel()

                # Calculer l'embedding CLIP
                embedding = self.clip_model.compute_features(image_path)
                self.image_embeddings[image_path] = embedding
                print(f"    [ImageSearch] Embedding stored, shape: {embedding.shape}")
            else:
                print(f"    [ImageSearch] Using perceptual hashing")
                # Perceptual hashing (fallback)
                img = Image.open(image_path)
                ahash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                dhash = imagehash.dhash(img)
                whash = imagehash.whash(img)

                self.image_hashes[image_path] = {
                    'ahash': ahash,
                    'phash': phash,
                    'dhash': dhash,
                    'whash': whash
                }

            # Stocker les métadonnées
            self.image_info[image_path] = metadata or {}

        except Exception as e:
            self._safe_print(f"Erreur lors de l'ajout de l'image {image_path}: {e}")
            import traceback
            traceback.print_exc()

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
        threshold: float = 0.5
    ) -> List[Tuple[str, float, dict]]:
        """
        Rechercher les images similaires à l'image de requête

        Args:
            query_image_path: Chemin vers l'image de requête
            top_k: Nombre de résultats à retourner
            threshold: Seuil de similarité minimale (0-1, plus haut = plus similaire)
                      - Pour CLIP: 0.5 par défaut (similarité cosinus)
                      - Pour hashing: 10 par défaut (distance hamming)

        Returns:
            Liste de tuples (chemin_image, score_similarité, métadonnées)
        """
        try:
            print(f"  [ImageSearch] Searching for: {query_image_path}")
            print(f"  [ImageSearch] Use CLIP: {self.use_clip}")
            print(f"  [ImageSearch] Threshold: {threshold}")

            if self.use_clip:
                print(f"  [ImageSearch] Using CLIP for search")
                # Initialiser CLIP si nécessaire
                if self.clip_model is None:
                    print(f"  [ImageSearch] Initializing CLIP model...")
                    self.clip_model = CLIPSimilarityModel()

                # Calculer l'embedding de la requête
                print(f"  [ImageSearch] Computing query embedding...")
                query_embedding = self.clip_model.compute_features(query_image_path)
                print(f"  [ImageSearch] Query embedding shape: {query_embedding.shape}")

                # Calculer la similarité cosinus avec toutes les images
                from sklearn.metrics.pairwise import cosine_similarity

                print(f"  [ImageSearch] Comparing with {len(self.image_embeddings)} images")
                similarities = []
                for image_path, embedding in self.image_embeddings.items():
                    sim = cosine_similarity(query_embedding, embedding)[0][0]
                    similarity_score = float(sim)
                    print(f"    [ImageSearch] {image_path}: score={similarity_score:.4f}")

                    if similarity_score >= threshold:
                        similarities.append((
                            image_path,
                            similarity_score,
                            self.image_info.get(image_path, {})
                        ))
                    else:
                        print(f"      [ImageSearch] Below threshold ({threshold}), skipped")

            else:
                # Perceptual hashing (fallback)
                query_img = Image.open(query_image_path)

                query_ahash = imagehash.average_hash(query_img)
                query_phash = imagehash.phash(query_img)
                query_dhash = imagehash.dhash(query_img)
                query_whash = imagehash.whash(query_img)

                similarities = []
                hash_threshold = int(threshold) if threshold < 100 else 10

                for image_path, hashes in self.image_hashes.items():
                    ahash_dist = query_ahash - hashes['ahash']
                    phash_dist = query_phash - hashes['phash']
                    dhash_dist = query_dhash - hashes['dhash']
                    whash_dist = query_whash - hashes['whash']

                    avg_distance = (ahash_dist + 2*phash_dist + dhash_dist + whash_dist) / 5.0
                    similarity_score = max(0, 1 - (avg_distance / 64.0))

                    if avg_distance <= hash_threshold:
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
            import traceback
            traceback.print_exc()
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
        if self.use_clip:
            self.image_embeddings.clear()
        else:
            self.image_hashes.clear()
        self.image_info.clear()

    def get_stats(self) -> dict:
        """Obtenir des statistiques sur l'index"""
        if self.use_clip:
            total_images = len(self.image_embeddings)
        else:
            total_images = len(self.image_hashes)

        return {
            'total_images': total_images,
            'total_metadata': len(self.image_info),
            'using_clip': self.use_clip
        }
