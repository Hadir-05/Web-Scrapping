"""
Chargeur de modèles PyTorch avec cache Redis
Les modèles restent en mémoire pour performance optimale
"""
import torch
import pickle
import redis
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class ModelCache:
    """
    Cache Redis pour modèles PyTorch
    Garde les modèles en mémoire pour éviter rechargement
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: str = "",
        redis_db: int = 0
    ):
        """
        Initialise la connexion Redis

        Args:
            redis_host: Hôte Redis
            redis_port: Port Redis
            redis_password: Mot de passe Redis (optionnel)
            redis_db: Database Redis
        """
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password if redis_password else None,
                db=redis_db,
                decode_responses=False  # Pour stocker des bytes
            )
            self.redis_client.ping()
            logger.info(f"✅ Connecté à Redis: {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis non disponible: {str(e)}")
            logger.warning("Les modèles seront chargés en mémoire locale")
            self.redis_client = None

        # Cache local en mémoire (fallback si Redis indisponible)
        self.local_cache = {}

    def get_model(self, key: str) -> Optional[Any]:
        """
        Récupère un modèle depuis le cache

        Args:
            key: Clé du modèle

        Returns:
            Modèle PyTorch ou None
        """
        # Essayer Redis d'abord
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    logger.info(f"✅ Modèle '{key}' récupéré depuis Redis")
                    return pickle.loads(data)
            except Exception as e:
                logger.warning(f"Erreur Redis get: {str(e)}")

        # Fallback: cache local
        if key in self.local_cache:
            logger.info(f"✅ Modèle '{key}' récupéré depuis cache local")
            return self.local_cache[key]

        return None

    def set_model(self, key: str, model: Any, ttl: int = 3600):
        """
        Stocke un modèle dans le cache

        Args:
            key: Clé du modèle
            model: Modèle PyTorch
            ttl: Durée de vie en secondes
        """
        # Stocker dans cache local
        self.local_cache[key] = model

        # Essayer de stocker dans Redis
        if self.redis_client:
            try:
                serialized = pickle.dumps(model)
                self.redis_client.setex(key, ttl, serialized)
                logger.info(f"✅ Modèle '{key}' mis en cache Redis (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Erreur Redis set: {str(e)}")
        else:
            logger.info(f"✅ Modèle '{key}' mis en cache local")


class ModelLoader:
    """
    Gestionnaire de chargement des modèles PyTorch
    """

    def __init__(self, cache: ModelCache, device: str = "cpu"):
        """
        Args:
            cache: Instance ModelCache
            device: 'cpu' ou 'cuda'
        """
        self.cache = cache
        self.device = device

    def load_model(
        self,
        model_path: str,
        model_key: str,
        cache_ttl: int = 3600
    ) -> Any:
        """
        Charge un modèle PyTorch (avec cache)

        Args:
            model_path: Chemin vers le fichier .pth
            model_key: Clé unique pour le cache
            cache_ttl: Durée de vie du cache

        Returns:
            Modèle PyTorch chargé et en mode eval

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            RuntimeError: Si erreur de chargement
        """
        # Vérifier le cache
        cached_model = self.cache.get_model(model_key)
        if cached_model is not None:
            return cached_model

        # Charger depuis le fichier
        logger.info(f"🔄 Chargement du modèle depuis {model_path}...")

        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Modèle non trouvé: {model_path}\n"
                f"Placez vos modèles .pth dans le dossier models/"
            )

        try:
            # Charger le modèle
            model = torch.load(model_path, map_location=self.device)

            # Si c'est un state_dict, adapter selon votre architecture
            # Exemple: model = YourModelClass(); model.load_state_dict(...)

            # Mode évaluation
            if hasattr(model, 'eval'):
                model.eval()

            # Mettre en cache
            self.cache.set_model(model_key, model, ttl=cache_ttl)

            logger.info(f"✅ Modèle '{model_key}' chargé sur {self.device}")
            return model

        except Exception as e:
            raise RuntimeError(f"Erreur chargement modèle: {str(e)}")


# Instance globale (initialisée au démarrage de l'app)
_model_cache: Optional[ModelCache] = None
_model_loader: Optional[ModelLoader] = None


def initialize_model_system(
    redis_host: str,
    redis_port: int,
    redis_password: str,
    device: str
):
    """
    Initialise le système de modèles

    Args:
        redis_host: Hôte Redis
        redis_port: Port Redis
        redis_password: Mot de passe Redis
        device: Device PyTorch
    """
    global _model_cache, _model_loader

    _model_cache = ModelCache(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password
    )

    _model_loader = ModelLoader(cache=_model_cache, device=device)

    logger.info("✅ Système de modèles initialisé")


def get_model_loader() -> ModelLoader:
    """Récupère le loader de modèles"""
    if _model_loader is None:
        raise RuntimeError("ModelLoader non initialisé. Appelez initialize_model_system()")
    return _model_loader
