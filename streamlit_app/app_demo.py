"""
Application Streamlit MVP - Luxury AI Search Interface (VERSION DÉMO)
Cette version fonctionne sans modèles PyTorch pour démo rapide
"""
import streamlit as st
from pathlib import Path
import sys
from PIL import Image
import io

# Configuration de la page
st.set_page_config(
    page_title="Luxury AI Search",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)


def apply_custom_css():
    """Applique un CSS personnalisé pour thème luxe"""
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

    /* Product cards */
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #E0E0E0;
    }

    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(212, 175, 55, 0.2);
        transition: all 0.3s ease;
    }

    /* Metrics personnalisées */
    .metric-container {
        background: linear-gradient(135deg, #D4AF37 0%, #F4E5B8 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)


def generate_mock_results(query: str, num_results: int = 10) -> list:
    """Génère des résultats mock pour la démo"""
    results = [
        {
            "product_id": f"LUX-{i+1:03d}",
            "name": f"Produit de Luxe {i+1}",
            "description": f"Description élégante pour '{query}'",
            "score": 0.95 - (i * 0.05),
            "price": 1000 + (i * 100),
            "image_url": f"https://via.placeholder.com/300x300/D4AF37/000000?text=Produit+{i+1}"
        }
        for i in range(num_results)
    ]
    return results


def format_price(price: float) -> str:
    """Formate un prix en euros"""
    return f"{price:,.2f} €".replace(",", " ").replace(".", ",")


def format_score(score: float) -> str:
    """Formate un score de pertinence"""
    return f"{score * 100:.0f}%"


def display_product_card(product: dict):
    """Affiche une carte produit"""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(product["image_url"], use_container_width=True)

    with col2:
        st.markdown(f"### {product['name']}")
        st.markdown(f"**ID:** `{product['product_id']}`")
        st.markdown(product["description"])

        col_score, col_price = st.columns(2)
        with col_score:
            st.metric("Pertinence", format_score(product["score"]))
        with col_price:
            st.markdown(f"### {format_price(product['price'])}")

    st.markdown("---")


def render_sidebar():
    """Affiche la barre latérale"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/000000/D4AF37?text=LUXURY+BRAND", use_container_width=True)
        st.markdown("---")

        st.markdown("### 🎯 Mode de Recherche")
        search_mode = st.radio(
            "",
            options=["🔤 Recherche par Mots-Clés", "🖼️ Recherche par Image"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("### ⚙️ Paramètres")
        max_results = st.slider("Nombre de résultats", 5, 20, 10)

        st.markdown("---")

        st.markdown("### 📊 Statistiques")
        st.metric("Mode", "DÉMO", delta="Sans modèles PyTorch")
        st.info("💡 Cette version démo fonctionne sans modèles AI. Pour utiliser vos vrais modèles, installez PyTorch et placez vos fichiers .pth dans models/")

        st.markdown("---")

        st.markdown("""
        <div style='text-align: center; color: #D4AF37;'>
            <small>💎 Luxury AI Search v1.0 (Demo)</small>
        </div>
        """, unsafe_allow_html=True)

    return search_mode, max_results


def render_keyword_search(max_results: int):
    """Interface de recherche par mots-clés"""
    st.markdown("## 🔤 Recherche par Mots-Clés")
    st.markdown("Trouvez vos produits de luxe en quelques mots...")

    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_input(
            "Que recherchez-vous ?",
            placeholder="Ex: sac à main en cuir noir, montre suisse, parfum floral...",
            label_visibility="collapsed"
        )

    with col2:
        search_button = st.button("🔍 Rechercher", use_container_width=True)

    if search_button and query:
        with st.spinner("🔍 Recherche en cours..."):
            results = generate_mock_results(query, max_results)
            st.session_state['search_results'] = results
            st.session_state['search_type'] = 'keyword'

    if 'search_results' in st.session_state and st.session_state.get('search_type') == 'keyword':
        st.markdown("---")
        st.markdown(f"### 📦 {len(st.session_state['search_results'])} Résultats Trouvés")

        for product in st.session_state['search_results']:
            display_product_card(product)


def render_image_search(max_results: int):
    """Interface de recherche par image"""
    st.markdown("## 🖼️ Recherche par Image")
    st.markdown("Uploadez une image pour trouver des produits similaires...")

    uploaded_file = st.file_uploader(
        "Choisissez une image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        col1, col2 = st.columns([1, 1])

        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Votre image", use_container_width=True)

        with col2:
            st.markdown("### 📊 Analyse")
            st.info("Mode DÉMO : Résultats simulés")

            if st.button("🔍 Rechercher des produits similaires", use_container_width=True):
                with st.spinner("🖼️ Analyse de l'image..."):
                    results = generate_mock_results("image similaire", max_results)
                    st.session_state['search_results'] = results
                    st.session_state['search_type'] = 'image'

    if 'search_results' in st.session_state and st.session_state.get('search_type') == 'image':
        st.markdown("---")
        st.markdown(f"### 📦 {len(st.session_state['search_results'])} Produits Similaires")

        for product in st.session_state['search_results']:
            display_product_card(product)


def main():
    """Fonction principale"""
    apply_custom_css()

    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0;'>💎 Luxury AI Search</h1>
        <p style='color: #D4AF37; font-size: 1.2rem;'>
            Recherche Intelligente pour Produits de Luxe (Version Démo)
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Sidebar
    search_mode, max_results = render_sidebar()

    # Interface selon le mode
    if "Mots-Clés" in search_mode:
        render_keyword_search(max_results)
    else:
        render_image_search(max_results)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 2rem 0;'>
        <small>
            💎 Version DÉMO - Fonctionne sans modèles PyTorch<br>
            Pour activer l'IA : installez PyTorch et placez vos modèles .pth dans models/
        </small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
