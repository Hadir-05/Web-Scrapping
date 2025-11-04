"""
Models de données pour le scraper web
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
import json


@dataclass
class ImageMetadata:
    """Métadonnées basiques d'une image"""
    src: str
    link: str

    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return asdict(self)


@dataclass
class ProductData:
    """Données complètes d'un produit"""
    item_url: str
    collection_date: datetime
    src_image: str
    title: str
    description: str
    price: str
    screenshot_path: str
    product_image_paths: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire avec sérialisation de datetime"""
        data = asdict(self)
        data['collection_date'] = self.collection_date.isoformat()
        return data


class DataManager:
    """Gestionnaire pour sauvegarder les données en JSON"""

    @staticmethod
    def save_image_metadata(data: List[ImageMetadata], output_path: str):
        """Sauvegarder les métadonnées d'images dans un fichier JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in data], f, indent=2, ensure_ascii=False)

    @staticmethod
    def save_product_data(data: List[ProductData], output_path: str):
        """Sauvegarder les données de produits dans un fichier JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in data], f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_image_metadata(input_path: str) -> List[ImageMetadata]:
        """Charger les métadonnées d'images depuis un fichier JSON"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [ImageMetadata(**item) for item in data]

    @staticmethod
    def load_product_data(input_path: str) -> List[ProductData]:
        """Charger les données de produits depuis un fichier JSON"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            item['collection_date'] = datetime.fromisoformat(item['collection_date'])
        return [ProductData(**item) for item in data]
