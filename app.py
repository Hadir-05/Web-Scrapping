"""
Application Streamlit pour la recherche de produits AliExpress par image
"""
import streamlit as st
import asyncio
import nest_asyncio
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from PIL import Image

# Permettre les event loops imbriqués (nécessaire sur Windows avec Streamlit)
nest_asyncio.apply()

from src.scraper.aliexpress_scraper import AliExpressImageSearchScraper
from src.image_search.image_similarity import ImageSimilaritySearch
from src.models.data_models import DataManager, ImageMetadata, ProductData


# Configuration de la page
st.set_page_config(
    page_title="Recherche de Produits AliExpress par Image",
    page_icon="🔍",
    layout="wide"
)


def init_session_state():
    """Initialiser les variables de session"""
    if 'image_search' not in st.session_state:
        st.session_state.image_search = ImageSimilaritySearch()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'uploaded_image_path' not in st.session_state:
        st.session_state.uploaded_image_path = None
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = "output"


async def run_aliexpress_search(image_path: str, max_results: int, output_dir: str):
    """Exécuter la recherche AliExpress par image de manière asynchrone"""
    scraper = AliExpressImageSearchScraper(output_dir)
    return await scraper.search_by_image(image_path, max_results, headless=True)


def save_results(image_metadata_list, product_data_list, output_dir):
    """Sauvegarder les résultats dans des fichiers JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sauvegarder les métadonnées d'images
    image_metadata_path = output_path / "image_metadata.json"
    DataManager.save_image_metadata(image_metadata_list, str(image_metadata_path))

    # Sauvegarder les données de produits
    product_data_path = output_path / "product_data.json"
    DataManager.save_product_data(product_data_list, str(product_data_path))

    return image_metadata_path, product_data_path


def calculate_similarity_scores(uploaded_image_path: str, product_data_list):
    """Calculer les scores de similarité entre l'image uploadée et les produits trouvés"""
    image_search = ImageSimilaritySearch()

    # Ajouter toutes les images de produits à l'index
    for product in product_data_list:
        for img_path in product.product_image_paths:
            if os.path.exists(img_path):
                image_search.add_image(img_path, {
                    'product_title': product.title,
                    'product_url': product.item_url,
                    'product_price': product.price
                })

    # Rechercher les images similaires
    similar_images = image_search.search_similar(
        uploaded_image_path,
        top_k=len(product_data_list),
        threshold=50  # Seuil plus permissif
    )

    # Créer un dictionnaire de scores par chemin d'image
    similarity_scores = {}
    for img_path, score, metadata in similar_images:
        similarity_scores[img_path] = score

    return similarity_scores


def main():
    """Fonction principale de l'application"""
    init_session_state()

    st.title("🔍 Recherche de Produits AliExpress par Image")
    st.markdown("### Uploadez une image et trouvez des produits similaires sur AliExpress")
    st.markdown("---")

    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        output_dir = st.text_input(
            "Répertoire de sortie",
            value="output",
            help="Répertoire où seront sauvegardés les résultats"
        )
        st.session_state.output_dir = output_dir

        max_results = st.slider(
            "Nombre max de produits",
            min_value=5,
            max_value=50,
            value=20,
            help="Nombre maximum de produits à rechercher"
        )

        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        if st.session_state.search_results:
            img_count = len(st.session_state.search_results[0])
            prod_count = len(st.session_state.search_results[1])
            st.metric("Images trouvées", img_count)
            st.metric("Produits trouvés", prod_count)

        st.markdown("---")
        st.markdown("### ℹ️ Comment ça marche ?")
        st.markdown("""
        1. Uploadez une image de produit
        2. Cliquez sur "Rechercher sur AliExpress"
        3. L'application cherchera des produits similaires
        4. Les résultats sont triés par similarité
        5. Téléchargez les résultats en JSON
        """)

    # Tabs pour organiser l'interface
    tab1, tab2, tab3 = st.tabs(["🖼️ Recherche par Image", "📊 Résultats Détaillés", "📁 Export"])

    # Tab 1: Recherche par Image
    with tab1:
        st.header("Upload et Recherche")

        # Upload de l'image
        uploaded_file = st.file_uploader(
            "📤 Uploadez une image de produit",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            help="Choisissez une image du produit que vous cherchez"
        )

        if uploaded_file:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("🖼️ Votre Image")
                st.image(uploaded_file, use_container_width=True)

                # Sauvegarder temporairement l'image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    st.session_state.uploaded_image_path = tmp_file.name

            with col2:
                st.subheader("🚀 Lancer la Recherche")

                st.info("""
                **Ce que l'application va faire :**
                - Se connecter à AliExpress
                - Rechercher des produits similaires à votre image
                - Télécharger les images et informations des produits
                - Comparer la similarité avec votre image
                """)

                search_button = st.button(
                    "🔍 Rechercher sur AliExpress",
                    type="primary",
                    use_container_width=True
                )

                if search_button and st.session_state.uploaded_image_path:
                    with st.spinner("🔄 Recherche en cours sur AliExpress... Cela peut prendre plusieurs minutes."):
                        try:
                            # Exécuter la recherche
                            image_metadata_list, product_data_list = asyncio.run(
                                run_aliexpress_search(
                                    st.session_state.uploaded_image_path,
                                    max_results,
                                    output_dir
                                )
                            )

                            st.session_state.search_results = (image_metadata_list, product_data_list)

                            if product_data_list:
                                # Sauvegarder les résultats
                                img_path, prod_path = save_results(
                                    image_metadata_list,
                                    product_data_list,
                                    output_dir
                                )

                                st.success(f"✅ Recherche terminée avec succès!")
                                st.info(f"📊 {len(product_data_list)} produits trouvés")

                                # Calculer les scores de similarité
                                st.info("🔄 Calcul des similarités...")
                                similarity_scores = calculate_similarity_scores(
                                    st.session_state.uploaded_image_path,
                                    product_data_list
                                )

                                # Trier les produits par similarité
                                sorted_products = []
                                for product in product_data_list:
                                    max_score = 0
                                    for img_path in product.product_image_paths:
                                        score = similarity_scores.get(img_path, 0)
                                        max_score = max(max_score, score)
                                    sorted_products.append((product, max_score))

                                sorted_products.sort(key=lambda x: x[1], reverse=True)

                                st.success("✅ Tri par similarité terminé!")

                            else:
                                st.warning("⚠️ Aucun produit trouvé. Essayez avec une autre image.")

                        except Exception as e:
                            st.error(f"❌ Erreur lors de la recherche: {str(e)}")
                            st.exception(e)

        # Afficher un aperçu des résultats
        if st.session_state.search_results and st.session_state.search_results[1]:
            st.markdown("---")
            st.subheader("🎯 Produits les Plus Similaires")

            image_metadata_list, product_data_list = st.session_state.search_results

            # Calculer et trier par similarité
            similarity_scores = calculate_similarity_scores(
                st.session_state.uploaded_image_path,
                product_data_list
            )

            sorted_products = []
            for product in product_data_list:
                max_score = 0
                for img_path in product.product_image_paths:
                    score = similarity_scores.get(img_path, 0)
                    max_score = max(max_score, score)
                sorted_products.append((product, max_score))

            sorted_products.sort(key=lambda x: x[1], reverse=True)

            # Afficher les 6 meilleurs résultats
            cols = st.columns(3)
            for idx, (product, similarity_score) in enumerate(sorted_products[:6]):
                with cols[idx % 3]:
                    if product.product_image_paths and os.path.exists(product.product_image_paths[0]):
                        st.image(product.product_image_paths[0], use_container_width=True)

                    st.markdown(f"**{product.title[:60]}...**")
                    st.markdown(f"💰 **Prix:** {product.price}")
                    st.markdown(f"🎯 **Similarité:** {similarity_score:.1%}")

                    if product.item_url:
                        st.markdown(f"[🔗 Voir sur AliExpress]({product.item_url})")

    # Tab 2: Résultats Détaillés
    with tab2:
        st.header("📋 Tous les Résultats")

        if st.session_state.search_results and st.session_state.search_results[1]:
            image_metadata_list, product_data_list = st.session_state.search_results

            # Calculer les similarités
            similarity_scores = calculate_similarity_scores(
                st.session_state.uploaded_image_path,
                product_data_list
            )

            sorted_products = []
            for product in product_data_list:
                max_score = 0
                for img_path in product.product_image_paths:
                    score = similarity_scores.get(img_path, 0)
                    max_score = max(max_score, score)
                sorted_products.append((product, max_score))

            sorted_products.sort(key=lambda x: x[1], reverse=True)

            # Afficher tous les produits
            for idx, (product, similarity_score) in enumerate(sorted_products):
                with st.expander(f"🔢 Produit {idx + 1} - {product.title} - Similarité: {similarity_score:.1%}"):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        if product.product_image_paths and os.path.exists(product.product_image_paths[0]):
                            st.image(product.product_image_paths[0], use_container_width=True)

                        if os.path.exists(product.screenshot_path):
                            st.caption("Capture d'écran")
                            st.image(product.screenshot_path, use_container_width=True)

                    with col2:
                        st.markdown(f"### {product.title}")
                        st.markdown(f"**💰 Prix:** {product.price}")
                        st.markdown(f"**🎯 Score de Similarité:** {similarity_score:.2%}")
                        st.markdown(f"**🔗 URL:** {product.item_url}")
                        st.markdown(f"**📅 Date de collecte:** {product.collection_date.strftime('%Y-%m-%d %H:%M')}")

                        if product.description:
                            st.markdown(f"**📝 Description:** {product.description}")

                        st.markdown(f"**🖼️ Nombre d'images:** {len(product.product_image_paths)}")

                        if product.item_url:
                            st.markdown(f"[➡️ Voir le produit sur AliExpress]({product.item_url})")

        else:
            st.info("ℹ️ Aucun résultat disponible. Uploadez une image et lancez la recherche.")

    # Tab 3: Export
    with tab3:
        st.header("📁 Fichiers de Résultats")

        output_path = Path(st.session_state.output_dir)

        # Vérifier si les fichiers existent
        image_metadata_path = output_path / "image_metadata.json"
        product_data_path = output_path / "product_data.json"

        if image_metadata_path.exists() and product_data_path.exists():
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📄 image_metadata.json")
                st.write(f"**Chemin:** {image_metadata_path}")

                # Afficher un aperçu
                with open(image_metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.write(f"**Nombre d'entrées:** {len(data)}")

                if data:
                    with st.expander("Aperçu (première entrée)"):
                        st.json(data[0])

                # Bouton de téléchargement
                with open(image_metadata_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        "⬇️ Télécharger image_metadata.json",
                        data=f.read(),
                        file_name="image_metadata.json",
                        mime="application/json"
                    )

            with col2:
                st.subheader("📄 product_data.json")
                st.write(f"**Chemin:** {product_data_path}")

                # Afficher un aperçu
                with open(product_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.write(f"**Nombre d'entrées:** {len(data)}")

                if data:
                    with st.expander("Aperçu (première entrée)"):
                        st.json(data[0])

                # Bouton de téléchargement
                with open(product_data_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        "⬇️ Télécharger product_data.json",
                        data=f.read(),
                        file_name="product_data.json",
                        mime="application/json"
                    )

            # Section pour les images
            st.markdown("---")
            st.subheader("🖼️ Images téléchargées")

            images_dir = output_path / "images"
            if images_dir.exists():
                image_files = list(images_dir.glob("*"))
                image_files = [f for f in image_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']]

                st.write(f"**Nombre d'images:** {len(image_files)}")
                st.write(f"**Répertoire:** {images_dir}")

                if image_files:
                    # Afficher une galerie d'images
                    st.markdown("### Galerie d'images")

                    # Pagination
                    images_per_page = 12
                    total_pages = (len(image_files) + images_per_page - 1) // images_per_page

                    page = st.number_input(
                        "Page",
                        min_value=1,
                        max_value=total_pages,
                        value=1
                    )

                    start_idx = (page - 1) * images_per_page
                    end_idx = min(start_idx + images_per_page, len(image_files))

                    cols = st.columns(4)
                    for idx, image_file in enumerate(image_files[start_idx:end_idx]):
                        with cols[idx % 4]:
                            st.image(str(image_file), use_container_width=True)
                            st.caption(image_file.name)

        else:
            st.info("ℹ️ Aucun résultat disponible. Uploadez une image et lancez la recherche.")


if __name__ == "__main__":
    main()
