"""
Counterfeit detection system using AI models
"""
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

# Import du modèle de similarité d'images
try:
    from .image_similarity_model import create_image_similarity_model
    IMAGE_MODEL_AVAILABLE = True
except ImportError:
    IMAGE_MODEL_AVAILABLE = False
    logger.warning("Image similarity model not available")


class CounterfeitDetector:
    """Système de détection de contrefaçons multi-critères"""

    def __init__(self, image_model=None, keyword_model=None, device='cpu', use_pretrained=True):
        """
        Args:
            image_model: Modèle PyTorch personnalisé pour similarité d'images (optionnel)
            keyword_model: Modèle PyTorch pour matching de mots-clés (optionnel)
            device: 'cpu' ou 'cuda'
            use_pretrained: Utiliser le modèle ResNet pré-entraîné (recommandé)
        """
        # Modèle d'images
        if image_model is not None:
            # Utiliser le modèle personnalisé fourni
            self.image_model = image_model
        elif use_pretrained and IMAGE_MODEL_AVAILABLE:
            # Créer le modèle pré-entraîné
            logger.info("🔄 Loading pre-trained image similarity model...")
            self.image_model = create_image_similarity_model(device=device)
            if self.image_model:
                logger.info("✅ Pre-trained image model loaded successfully!")
            else:
                logger.warning("⚠️ Failed to load pre-trained model")
                self.image_model = None
        else:
            self.image_model = None

        self.keyword_model = keyword_model

        # Marques de luxe à détecter
        self.luxury_brands = [
            "Louis Vuitton", "LV", "Gucci", "Hermès", "Hermes", "Chanel",
            "Prada", "Dior", "Fendi", "Burberry", "Versace", "Rolex",
            "Cartier", "Balenciaga", "Givenchy", "Valentino", "Saint Laurent",
            "YSL", "Bottega Veneta", "Celine", "Loewe", "Bvlgari", "Bulgari"
        ]

        # Variantes et fautes d'orthographe communes
        self.brand_variants = {
            "Louis Vuitton": ["LV", "L.V", "Louisvuitton", "Louis V", "LV bags"],
            "Hermès": ["Hermes", "Hermés", "Hermess"],
            "Gucci": ["Guccy", "Guuci", "G ucci"],
            # Ajoutez d'autres variantes...
        }

        # Mots suspects dans les titres
        self.suspicious_keywords = [
            "replica", "copy", "inspired", "style", "luxury style",
            "designer style", "high quality", "AAA", "1:1", "mirror",
            "super copy", "top quality"
        ]

    def detect_counterfeit(
        self,
        scraped_product: Dict,
        authentic_products: List[Dict]
    ) -> Dict:
        """
        Détecte si un produit scrapé est une contrefaçon

        Args:
            scraped_product: Produit scrapé d'un site e-commerce
            authentic_products: Liste des produits authentiques de référence

        Returns:
            Dictionnaire avec les scores de détection
        """

        results = {
            'is_counterfeit': False,
            'confidence_level': 'LOW',
            'overall_risk_score': 0.0,
            'similarity_score': 0.0,
            'keyword_match_score': 0.0,
            'price_suspicion_score': 0.0,
            'detected_brands': [],
            'detection_methods': [],
            'matched_authentic_product': None,
            'reasons': []
        }

        # 1. Détection de marques de luxe dans le titre
        detected_brands = self._detect_brands(scraped_product.get('title', ''))
        results['detected_brands'] = detected_brands

        if not detected_brands:
            # Pas de marque détectée, risque faible
            return results

        # 2. Score de correspondance par mots-clés
        keyword_score, best_match = self._keyword_matching(
            scraped_product,
            authentic_products,
            detected_brands
        )
        results['keyword_match_score'] = keyword_score

        if best_match:
            results['matched_authentic_product'] = best_match

        # 3. Score de similarité d'images (si modèle disponible)
        if self.image_model and scraped_product.get('image_urls'):
            image_score = self._image_similarity(
                scraped_product.get('image_urls', []),
                best_match.get('image_urls', []) if best_match else []
            )
            results['similarity_score'] = image_score
            results['detection_methods'].append('IMAGE_SIMILARITY')

        # 4. Analyse du prix
        if best_match and scraped_product.get('price'):
            price_score = self._price_analysis(
                scraped_product.get('price', 0),
                best_match.get('official_price', 0)
            )
            results['price_suspicion_score'] = price_score
            results['detection_methods'].append('PRICE_ANALYSIS')

        # 5. Détection de mots suspects
        suspicious_score = self._detect_suspicious_keywords(
            scraped_product.get('title', '') + ' ' + scraped_product.get('description', '')
        )

        # 6. Calcul du score global de risque
        overall_score = self._calculate_overall_risk(
            keyword_score,
            results['similarity_score'],
            price_score,
            suspicious_score
        )

        results['overall_risk_score'] = overall_score

        # 7. Détermination si c'est une contrefaçon
        if overall_score >= 0.7:
            results['is_counterfeit'] = True
            results['confidence_level'] = 'HIGH' if overall_score >= 0.85 else 'MEDIUM'
            results['detection_methods'].append('KEYWORD_MATCH')

        # 8. Raisons de détection
        results['reasons'] = self._generate_reasons(results, scraped_product, best_match)

        return results

    def _detect_brands(self, text: str) -> List[str]:
        """Détecte les marques de luxe dans un texte"""
        detected = []
        text_lower = text.lower()

        for brand in self.luxury_brands:
            if brand.lower() in text_lower:
                detected.append(brand)

            # Vérifier les variantes
            variants = self.brand_variants.get(brand, [])
            for variant in variants:
                if variant.lower() in text_lower:
                    detected.append(brand)
                    break

        return list(set(detected))

    def _keyword_matching(
        self,
        scraped_product: Dict,
        authentic_products: List[Dict],
        detected_brands: List[str]
    ) -> Tuple[float, Optional[Dict]]:
        """
        Matching par mots-clés avec les produits authentiques

        Returns:
            (score, meilleur produit correspondant)
        """
        if not authentic_products:
            return 0.0, None

        best_score = 0.0
        best_match = None

        scraped_text = f"{scraped_product.get('title', '')} {scraped_product.get('description', '')}"

        for auth_product in authentic_products:
            # Vérifier si la marque correspond
            if auth_product.get('brand') not in detected_brands:
                continue

            auth_text = f"{auth_product.get('name', '')} {auth_product.get('description', '')}"

            # Similarité de texte
            similarity = SequenceMatcher(None, scraped_text.lower(), auth_text.lower()).ratio()

            if similarity > best_score:
                best_score = similarity
                best_match = auth_product

        return best_score, best_match

    def _image_similarity(
        self,
        scraped_images: List[str],
        authentic_images: List[str]
    ) -> float:
        """
        Calcule la similarité entre les images

        Args:
            scraped_images: URLs des images scrapées
            authentic_images: URLs des images authentiques

        Returns:
            Score de similarité (0-1)
        """
        if not scraped_images or not authentic_images:
            return 0.0

        # Vérifier si le modèle est disponible
        if self.image_model is None:
            logger.warning("Image model not available, using placeholder score")
            return 0.5

        try:
            # Utiliser la première image de chaque liste
            scraped_img = scraped_images[0]
            authentic_img = authentic_images[0]

            # Calculer la similarité avec le modèle
            similarity = self.image_model.compute_similarity(scraped_img, authentic_img)

            logger.info(f"✅ Image similarity computed: {similarity:.2%}")
            return similarity

        except Exception as e:
            logger.error(f"Error computing image similarity: {str(e)}")
            return 0.0

    def _price_analysis(self, scraped_price: float, official_price: float) -> float:
        """
        Analyse du prix pour détecter les suspicions

        Prix suspect si beaucoup trop bas par rapport au prix officiel
        """
        if not official_price or official_price == 0:
            return 0.0

        price_ratio = scraped_price / official_price

        # Score de suspicion basé sur le ratio de prix
        if price_ratio < 0.1:  # Moins de 10% du prix officiel
            return 1.0  # Très suspect
        elif price_ratio < 0.2:
            return 0.8
        elif price_ratio < 0.3:
            return 0.6
        elif price_ratio < 0.5:
            return 0.4
        else:
            return 0.0  # Prix normal ou élevé

    def _detect_suspicious_keywords(self, text: str) -> float:
        """Détecte des mots suspects dans le texte"""
        text_lower = text.lower()
        count = 0

        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                count += 1

        # Score basé sur le nombre de mots suspects
        max_score = min(count * 0.3, 1.0)
        return max_score

    def _calculate_overall_risk(
        self,
        keyword_score: float,
        image_score: float,
        price_score: float,
        suspicious_score: float
    ) -> float:
        """
        Calcule le score global de risque (0-1)

        Pondération:
        - Mots-clés: 30%
        - Similarité image: 30%
        - Prix: 25%
        - Mots suspects: 15%
        """
        weights = {
            'keyword': 0.30,
            'image': 0.30,
            'price': 0.25,
            'suspicious': 0.15
        }

        overall = (
            keyword_score * weights['keyword'] +
            image_score * weights['image'] +
            price_score * weights['price'] +
            suspicious_score * weights['suspicious']
        )

        return min(overall, 1.0)

    def _generate_reasons(
        self,
        results: Dict,
        scraped_product: Dict,
        authentic_product: Optional[Dict]
    ) -> List[str]:
        """Génère les raisons de détection pour l'utilisateur"""
        reasons = []

        # Marques détectées
        if results['detected_brands']:
            reasons.append(f"Marques détectées: {', '.join(results['detected_brands'])}")

        # Prix suspect
        if results['price_suspicion_score'] > 0.5:
            if authentic_product:
                reasons.append(
                    f"Prix suspect: ${scraped_product.get('price', 0):.2f} vs "
                    f"prix officiel ${authentic_product.get('official_price', 0):.2f}"
                )
            else:
                reasons.append("Prix anormalement bas pour une marque de luxe")

        # Similarité élevée
        if results['similarity_score'] > 0.7:
            reasons.append(f"Similarité d'image élevée: {results['similarity_score']:.1%}")

        # Mots-clés correspondants
        if results['keyword_match_score'] > 0.6:
            reasons.append("Forte correspondance avec produit authentique")

        # Site source
        if scraped_product.get('source_site') in ['AliExpress', 'DHgate', 'Wish']:
            reasons.append(f"Trouvé sur {scraped_product['source_site']} (site à risque)")

        return reasons
