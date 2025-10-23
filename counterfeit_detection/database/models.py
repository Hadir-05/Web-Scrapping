"""
Database schema and models for counterfeit detection system
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class AuthenticProduct(Base):
    """Table des produits authentiques de luxe"""
    __tablename__ = 'authentic_products'

    id = Column(Integer, primary_key=True)
    product_id = Column(String(100), unique=True, nullable=False)
    brand = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    official_price = Column(Float)
    image_urls = Column(JSON)  # Liste d'URLs d'images
    keywords = Column(JSON)  # Mots-clés associés
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    counterfeits = relationship("CounterfeitProduct", back_populates="authentic")

    def __repr__(self):
        return f"<AuthenticProduct(brand='{self.brand}', name='{self.name}')>"


class CounterfeitProduct(Base):
    """Table des contrefaçons détectées"""
    __tablename__ = 'counterfeit_products'

    id = Column(Integer, primary_key=True)
    detection_id = Column(String(100), unique=True, nullable=False)

    # Source
    source_site = Column(String(100), nullable=False, index=True)  # AliExpress, DHgate, etc.
    source_url = Column(String(500), nullable=False)
    seller_name = Column(String(255))
    seller_url = Column(String(500))

    # Produit
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float)
    currency = Column(String(10), default='USD')
    image_urls = Column(JSON)

    # Détection
    authentic_product_id = Column(Integer, ForeignKey('authentic_products.id'))
    similarity_score = Column(Float)  # Score de similarité d'image (0-1)
    keyword_match_score = Column(Float)  # Score de correspondance mots-clés (0-1)
    price_suspicion_score = Column(Float)  # Score de suspicion prix (0-1)
    overall_risk_score = Column(Float, index=True)  # Score global de risque (0-1)

    # Classification
    is_confirmed_counterfeit = Column(Boolean, default=False)
    confidence_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), default='DETECTED', index=True)  # DETECTED, REVIEWED, CONFIRMED, FALSE_POSITIVE

    # Métadonnées
    detected_brands = Column(JSON)  # Marques détectées dans le titre/description
    detection_method = Column(JSON)  # Méthodes de détection utilisées
    additional_data = Column(JSON)  # Données supplémentaires

    # Timestamps
    first_detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_checked_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    authentic = relationship("AuthenticProduct", back_populates="counterfeits")
    actions = relationship("CounterfeitAction", back_populates="counterfeit")

    def __repr__(self):
        return f"<CounterfeitProduct(site='{self.source_site}', risk={self.overall_risk_score})>"


class CounterfeitAction(Base):
    """Actions prises sur les contrefaçons"""
    __tablename__ = 'counterfeit_actions'

    id = Column(Integer, primary_key=True)
    counterfeit_id = Column(Integer, ForeignKey('counterfeit_products.id'))

    action_type = Column(String(50), nullable=False)  # ALERT_SENT, REPORT_FILED, TAKEDOWN_REQUEST, etc.
    action_status = Column(String(50))  # PENDING, COMPLETED, FAILED
    details = Column(Text)
    performed_by = Column(String(100))
    performed_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    counterfeit = relationship("CounterfeitProduct", back_populates="actions")

    def __repr__(self):
        return f"<CounterfeitAction(type='{self.action_type}', status='{self.action_status}')>"


class ScrapingJob(Base):
    """Historique des tâches de scraping"""
    __tablename__ = 'scraping_jobs'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(100), unique=True, nullable=False)

    site = Column(String(100), nullable=False)
    search_query = Column(String(255))
    target_brand = Column(String(100))

    status = Column(String(20), default='PENDING')  # PENDING, RUNNING, COMPLETED, FAILED
    items_scraped = Column(Integer, default=0)
    counterfeits_found = Column(Integer, default=0)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)

    job_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict

    def __repr__(self):
        return f"<ScrapingJob(site='{self.site}', status='{self.status}')>"


class BrandKeyword(Base):
    """Mots-clés de marques pour la détection"""
    __tablename__ = 'brand_keywords'

    id = Column(Integer, primary_key=True)
    brand = Column(String(100), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    keyword_type = Column(String(50))  # EXACT, VARIANT, COMMON_MISSPELLING
    weight = Column(Float, default=1.0)  # Poids du mot-clé

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BrandKeyword(brand='{self.brand}', keyword='{self.keyword}')>"


# Database Manager Class
class DatabaseManager:
    """Gestionnaire de base de données"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'counterfeit_detection.db')

        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_authentic_product(self, **kwargs):
        """Ajoute un produit authentique"""
        product = AuthenticProduct(**kwargs)
        self.session.add(product)
        self.session.commit()
        return product

    def add_counterfeit(self, **kwargs):
        """Ajoute une contrefaçon détectée"""
        counterfeit = CounterfeitProduct(**kwargs)
        self.session.add(counterfeit)
        self.session.commit()
        return counterfeit

    def get_counterfeits(self, filters=None, limit=100):
        """Récupère les contrefaçons avec filtres"""
        query = self.session.query(CounterfeitProduct)

        if filters:
            if 'site' in filters:
                query = query.filter(CounterfeitProduct.source_site == filters['site'])
            if 'min_risk' in filters:
                query = query.filter(CounterfeitProduct.overall_risk_score >= filters['min_risk'])
            if 'status' in filters:
                query = query.filter(CounterfeitProduct.status == filters['status'])

        return query.order_by(CounterfeitProduct.first_detected_at.desc()).limit(limit).all()

    def get_statistics(self):
        """Récupère les statistiques globales"""
        total_counterfeits = self.session.query(CounterfeitProduct).count()
        total_authentic = self.session.query(AuthenticProduct).count()

        high_risk = self.session.query(CounterfeitProduct).filter(
            CounterfeitProduct.overall_risk_score >= 0.8
        ).count()

        by_site = self.session.query(
            CounterfeitProduct.source_site,
            CounterfeitProduct.id
        ).all()

        return {
            'total_counterfeits': total_counterfeits,
            'total_authentic': total_authentic,
            'high_risk_count': high_risk,
            'by_site': by_site
        }

    def close(self):
        """Ferme la session"""
        self.session.close()
