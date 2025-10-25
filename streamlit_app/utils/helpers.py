"""
Fonctions utilitaires pour l'application Streamlit
"""
from PIL import Image
import io
from typing import Optional


def load_image(image_file) -> Optional[Image.Image]:
    """
    Charge une image depuis un fichier uploadé

    Args:
        image_file: Fichier uploadé via st.file_uploader

    Returns:
        Image PIL ou None
    """
    try:
        img = Image.open(image_file)
        return img
    except Exception as e:
        print(f"Erreur chargement image: {e}")
        return None


def format_price(price: float) -> str:
    """
    Formate un prix en euros

    Args:
        price: Prix en float

    Returns:
        Prix formaté (ex: "1 234,56 €")
    """
    return f"{price:,.2f} €".replace(",", " ").replace(".", ",")


def format_score(score: float) -> str:
    """
    Formate un score de pertinence

    Args:
        score: Score entre 0 et 1

    Returns:
        Score formaté en pourcentage (ex: "95%")
    """
    return f"{score * 100:.0f}%"


def apply_custom_css():
    """
    Applique un CSS personnalisé pour thème luxe
    """
    import streamlit as st

    st.markdown("""
    <style>
    /* Thème Luxe */
    .main {
        background-color: #FAFAFA;
    }

    /* Titres dorés */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Playfair Display', serif;
    }

    /* Boutons élégants */
    .stButton>button {
        background-color: #D4AF37;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: 2px solid #B8960F;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #B8960F;
        border-color: #D4AF37;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(212, 175, 55, 0.3);
    }

    /* Cards produits */
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border: 1px solid #E0E0E0;
    }

    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(212, 175, 55, 0.2);
    }

    /* Input search */
    .stTextInput>div>div>input {
        border: 2px solid #D4AF37;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
    }

    /* Sidebar luxe */
    .css-1d391kg {
        background-color: #1A1A1A;
    }

    /* Metrics personnalisées */
    .metric-container {
        background: linear-gradient(135deg, #D4AF37 0%, #F4E5B8 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #000;
    }

    /* Separator doré */
    hr {
        border: 1px solid #D4AF37;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def display_product_card(product: dict):
    """
    Affiche une carte produit élégante

    Args:
        product: Dictionnaire avec infos produit
    """
    import streamlit as st

    with st.container():
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(product.get("image_url", ""), use_container_width=True)

        with col2:
            st.markdown(f"### {product['name']}")
            st.markdown(f"**ID:** `{product['product_id']}`")

            if "description" in product:
                st.markdown(product["description"])

            # Score ou similarité
            if "score" in product:
                st.metric("Pertinence", format_score(product["score"]))
            elif "similarity" in product:
                st.metric("Similarité", format_score(product["similarity"]))

            # Prix
            if "price" in product:
                st.markdown(f"### {format_price(product['price'])}")

        st.markdown("---")
