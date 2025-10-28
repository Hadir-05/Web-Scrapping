"""
Base scraper class for all e-commerce sites
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers"""

    def __init__(self, use_proxy: bool = False):
        self.session = requests.Session()
        self.use_proxy = use_proxy

        # Headers pour éviter les blocages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    @abstractmethod
    def search(self, query: str, max_pages: int = 5) -> List[Dict]:
        """
        Recherche des produits sur le site

        Args:
            query: Requête de recherche
            max_pages: Nombre maximum de pages à scraper

        Returns:
            Liste de produits trouvés
        """
        pass

    @abstractmethod
    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Récupère les détails d'un produit

        Args:
            product_url: URL du produit

        Returns:
            Dictionnaire avec les détails du produit
        """
        pass

    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Récupère une page web avec gestion des erreurs

        Args:
            url: URL à récupérer
            max_retries: Nombre de tentatives

        Returns:
            BeautifulSoup object ou None
        """
        for attempt in range(max_retries):
            try:
                # Délai aléatoire pour éviter le rate limiting
                time.sleep(random.uniform(1, 3))

                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')

                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited on {url}, waiting...")
                    time.sleep(random.uniform(5, 10))

                else:
                    logger.warning(f"Status {response.status_code} for {url}")

            except requests.RequestException as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))

        return None

    def extract_images(self, soup: BeautifulSoup, selectors: List[str]) -> List[str]:
        """
        Extrait les URLs d'images depuis plusieurs sélecteurs

        Args:
            soup: BeautifulSoup object
            selectors: Liste de sélecteurs CSS

        Returns:
            Liste d'URLs d'images
        """
        images = []

        for selector in selectors:
            img_tags = soup.select(selector)
            for img in img_tags:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    # Nettoyer l'URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = urljoin(self.base_url, src)

                    images.append(src)

        return list(set(images))  # Dédupliquer

    def clean_price(self, price_str: str) -> Optional[float]:
        """
        Nettoie et convertit une chaîne de prix en float

        Args:
            price_str: Chaîne de prix (ex: "$19.99", "€50,00")

        Returns:
            Prix en float ou None
        """
        if not price_str:
            return None

        try:
            # Retirer les symboles de devise et espaces
            clean = price_str.replace('$', '').replace('€', '').replace('£', '')
            clean = clean.replace(',', '.').replace(' ', '').strip()

            # Extraire le premier nombre
            import re
            match = re.search(r'[\d.]+', clean)
            if match:
                return float(match.group())

        except (ValueError, AttributeError):
            pass

        return None

    @property
    @abstractmethod
    def base_url(self) -> str:
        """URL de base du site"""
        pass

    @property
    @abstractmethod
    def site_name(self) -> str:
        """Nom du site"""
        pass
