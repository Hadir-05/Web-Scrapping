"""
Application Streamlit MVP - Luxury AI Search Interface
Interface de recherche intelligente pour produits de luxe
"""
import streamlit as st
from pathlib import Path
import sys

# Ajouter les chemins pour imports
sys.path.append(str(Path(__file__).parent))

from config import (
    PAGE_CONFIG,
    KEYWORD_MODEL_PATH,
    IMAGE_MODEL_PATH,
    DEVICE,
    MAX_RESULTS
)
from models.model_manager import ModelManager
from utils.helpers import (
    apply_custom_css,
    display_product_card,
    load_image
)


# Configuration de la page
st.set_page_config(**PAGE_CONFIG)


def initialize_session_state():
    """Initialise les variables de session"""
    if 'model_manager' not in st.session_state:
        st.session_state.model_manager = None
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'search_type' not in st.session_state:
        st.session_state.search_type = None


def load_models():
    """Charge les modèles une seule fois"""
    if st.session_state.model_manager is None:
        with st.spinner("🔄 Chargement des modèles IA..."):
            try:
                st.session_state.model_manager = ModelManager(
                    keyword_path=str(KEYWORD_MODEL_PATH),
                    image_path=str(IMAGE_MODEL_PATH),
                    device=DEVICE
                )
                st.success("✅ Modèles chargés et mis en cache!")
            except FileNotFoundError as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.info("""
                **Instructions:**
                1. Placez vos modèles .pth dans le dossier `models/`
                2. Nommez-les: `keyword_search.pth` et `image_similarity.pth`
                3. Relancez l'application
                """)
                st.stop()
            except Exception as e:
                st.error(f"❌ Erreur de chargement: {str(e)}")
                st.stop()


def render_sidebar():
    """Affiche la barre latérale"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80?text=LUXURY+BRAND", use_container_width=True)
        st.markdown("---")

        st.markdown("### 🎯 Mode de Recherche")
        search_mode = st.radio(
            "",
            options=["🔤 Recherche par Mots-Clés", "🖼️ Recherche par Image"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown("### ⚙️ Paramètres")
        max_results = st.slider("Nombre de résultats", 5, 20, MAX_RESULTS)

        st.markdown("---")

        st.markdown("### 📊 Statistiques")
        if st.session_state.model_manager:
            st.metric("Modèles chargés", "2/2 ✅")
            st.metric("Device", DEVICE.upper())
        else:
            st.metric("Modèles chargés", "0/2 ⏳")

        st.markdown("---")

        st.markdown("""
        <div style='text-align: center; color: #D4AF37;'>
            <small>💎 Luxury AI Search v1.0</small>
        </div>
        """, unsafe_allow_html=True)

    return search_mode, max_results


def render_keyword_search(max_results: int):
    """Interface de recherche par mots-clés"""
    st.markdown("## 🔤 Recherche par Mots-Clés")
    st.markdown("Trouvez vos produits de luxe en quelques mots...")

    # Zone de recherche
    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_input(
            "Que recherchez-vous ?",
            placeholder="Ex: sac à main en cuir noir, montre suisse, parfum floral...",
            label_visibility="collapsed"
        )

    with col2:
        search_button = st.button("🔍 Rechercher", use_container_width=True)

    # Recherche
    if search_button and query:
        with st.spinner("🔍 Recherche en cours..."):
            results = st.session_state.model_manager.search_by_keyword(
                query=query,
                top_k=max_results
            )
            st.session_state.search_results = results
            st.session_state.search_type = "keyword"

    # Affichage des résultats
    if st.session_state.search_results and st.session_state.search_type == "keyword":
        st.markdown("---")
        st.markdown(f"### 📦 {len(st.session_state.search_results)} Résultats Trouvés")

        for i, product in enumerate(st.session_state.search_results):
            with st.container():
                display_product_card(product)


def render_image_search(max_results: int):
    """Interface de recherche par image"""
    st.markdown("## 🖼️ Recherche par Image")
    st.markdown("Uploadez une image pour trouver des produits similaires...")

    # Upload d'image
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📤 Upload d'Image")
        uploaded_file = st.file_uploader(
            "Choisissez une image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            image = load_image(uploaded_file)
            if image:
                st.image(image, caption="Votre image", use_container_width=True)

                if st.button("🔍 Rechercher des produits similaires", use_container_width=True):
                    with st.spinner("🖼️ Analyse de l'image..."):
                        # Convertir l'image en bytes
                        image_bytes = uploaded_file.getvalue()

                        results = st.session_state.model_manager.search_by_image(
                            image_data=image_bytes,
                            top_k=max_results
                        )
                        st.session_state.search_results = results
                        st.session_state.search_type = "image"

    with col2:
        st.markdown("### 🌐 Ou URL d'Image")
        image_url = st.text_input(
            "URL de l'image",
            placeholder="https://example.com/image.jpg",
            label_visibility="collapsed"
        )

        if image_url:
            try:
                st.image(image_url, caption="Image depuis URL", use_container_width=True)
                if st.button("🔍 Rechercher", key="url_search", use_container_width=True):
                    st.info("Recherche par URL - Fonctionnalité à implémenter")
            except Exception as e:
                st.error(f"Erreur de chargement de l'image: {str(e)}")

    # Affichage des résultats
    if st.session_state.search_results and st.session_state.search_type == "image":
        st.markdown("---")
        st.markdown(f"### 📦 {len(st.session_state.search_results)} Produits Similaires")

        for i, product in enumerate(st.session_state.search_results):
            with st.container():
                display_product_card(product)


def main():
    """Fonction principale"""
    # Initialisation
    initialize_session_state()
    apply_custom_css()

    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0;'>💎 Luxury AI Search</h1>
        <p style='color: #D4AF37; font-size: 1.2rem;'>
            Recherche Intelligente pour Produits de Luxe
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Chargement des modèles
    load_models()

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
            Propulsé par Intelligence Artificielle |
            Modèles PyTorch en cache pour performance optimale
        </small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
