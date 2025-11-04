"""
Application Streamlit pour le Web Scraping avec recherche par image
"""
import streamlit as st
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime

from src.scraper.web_scraper import WebScraper
from src.image_search.image_similarity import ImageSimilaritySearch
from src.models.data_models import DataManager, ImageMetadata, ProductData


# Configuration de la page
st.set_page_config(
    page_title="Web Scraper avec Recherche d'Images",
    page_icon="🔍",
    layout="wide"
)


def init_session_state():
    """Initialiser les variables de session"""
    if 'scraper' not in st.session_state:
        st.session_state.scraper = None
    if 'image_search' not in st.session_state:
        st.session_state.image_search = ImageSimilaritySearch()
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = "output"


async def run_scraper(url: str, max_requests: int, output_dir: str):
    """Exécuter le scraper de manière asynchrone"""
    scraper = WebScraper(output_dir)
    return await scraper.scrape_page(url, max_requests, headless=True)


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


def main():
    """Fonction principale de l'application"""
    init_session_state()

    st.title("🔍 Web Scraper avec Recherche d'Images")
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

        max_requests = st.slider(
            "Nombre max de requêtes",
            min_value=1,
            max_value=100,
            value=50,
            help="Limite le nombre de pages à scraper"
        )

        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        if st.session_state.scraped_data:
            img_count = len(st.session_state.scraped_data[0])
            prod_count = len(st.session_state.scraped_data[1])
            st.metric("Images scrapées", img_count)
            st.metric("Produits trouvés", prod_count)

    # Tabs pour organiser l'interface
    tab1, tab2, tab3 = st.tabs(["🌐 Scraping", "🖼️ Recherche d'Images", "📁 Résultats"])

    # Tab 1: Scraping
    with tab1:
        st.header("Web Scraping")

        url = st.text_input(
            "URL à scraper",
            placeholder="https://example.com",
            help="Entrez l'URL complète de la page à scraper"
        )

        col1, col2 = st.columns([1, 4])

        with col1:
            scrape_button = st.button("🚀 Lancer le Scraping", type="primary")

        if scrape_button and url:
            if not url.startswith(('http://', 'https://')):
                st.error("L'URL doit commencer par http:// ou https://")
            else:
                with st.spinner("Scraping en cours... Cela peut prendre quelques minutes."):
                    try:
                        # Exécuter le scraper
                        image_metadata_list, product_data_list = asyncio.run(
                            run_scraper(url, max_requests, output_dir)
                        )

                        st.session_state.scraped_data = (image_metadata_list, product_data_list)

                        # Sauvegarder les résultats
                        img_path, prod_path = save_results(
                            image_metadata_list,
                            product_data_list,
                            output_dir
                        )

                        st.success(f"✅ Scraping terminé avec succès!")
                        st.info(f"📊 {len(image_metadata_list)} images et {len(product_data_list)} produits trouvés")

                        # Mettre à jour l'index de recherche d'images
                        st.session_state.image_search.clear()
                        images_dir = Path(output_dir) / "images"
                        if images_dir.exists():
                            st.session_state.image_search.add_images_from_directory(str(images_dir))

                    except Exception as e:
                        st.error(f"❌ Erreur lors du scraping: {str(e)}")

        # Afficher un aperçu des résultats
        if st.session_state.scraped_data:
            st.markdown("---")
            st.subheader("📋 Aperçu des résultats")

            image_metadata_list, product_data_list = st.session_state.scraped_data

            # Afficher quelques produits
            if product_data_list:
                st.markdown("#### Produits trouvés")
                for idx, product in enumerate(product_data_list[:3]):
                    with st.expander(f"Produit {idx + 1}: {product.title}"):
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            if os.path.exists(product.screenshot_path):
                                st.image(product.screenshot_path, caption="Capture d'écran")

                        with col2:
                            st.write(f"**URL:** {product.item_url}")
                            st.write(f"**Prix:** {product.price}")
                            st.write(f"**Description:** {product.description[:200]}...")
                            st.write(f"**Images:** {len(product.product_image_paths)}")

    # Tab 2: Recherche d'Images
    with tab2:
        st.header("Recherche d'Images par Similarité")

        if st.session_state.image_search.get_stats()['total_images'] == 0:
            st.warning("⚠️ Aucune image dans l'index. Veuillez d'abord effectuer un scraping.")
        else:
            st.info(f"📊 {st.session_state.image_search.get_stats()['total_images']} images dans l'index")

            # Upload d'une image pour la recherche
            uploaded_file = st.file_uploader(
                "Télécharger une image pour rechercher des similaires",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
            )

            col1, col2 = st.columns(2)
            with col1:
                top_k = st.slider("Nombre de résultats", 1, 20, 5)
            with col2:
                threshold = st.slider("Seuil de similarité", 0, 30, 10,
                                     help="Plus bas = plus strict")

            if uploaded_file:
                # Afficher l'image uploadée
                st.subheader("🖼️ Image de recherche")
                st.image(uploaded_file, width=300)

                if st.button("🔍 Rechercher des images similaires", type="primary"):
                    with st.spinner("Recherche en cours..."):
                        try:
                            # Rechercher des images similaires
                            results = st.session_state.image_search.search_similar_from_bytes(
                                uploaded_file.getvalue(),
                                top_k=top_k,
                                threshold=threshold
                            )

                            if results:
                                st.success(f"✅ {len(results)} image(s) similaire(s) trouvée(s)")

                                st.markdown("---")
                                st.subheader("📊 Résultats")

                                # Afficher les résultats
                                for idx, (image_path, similarity, metadata) in enumerate(results):
                                    with st.expander(f"Résultat {idx + 1} - Similarité: {similarity:.2%}"):
                                        col1, col2 = st.columns([1, 2])

                                        with col1:
                                            if os.path.exists(image_path):
                                                st.image(image_path, use_container_width=True)

                                        with col2:
                                            st.write(f"**Chemin:** {image_path}")
                                            st.write(f"**Score de similarité:** {similarity:.2%}")
                                            if metadata:
                                                st.write("**Métadonnées:**")
                                                st.json(metadata)
                            else:
                                st.warning("Aucune image similaire trouvée avec ces critères.")

                        except Exception as e:
                            st.error(f"❌ Erreur lors de la recherche: {str(e)}")

            # Fonction pour détecter les doublons
            st.markdown("---")
            st.subheader("🔄 Détection de doublons")

            duplicate_threshold = st.slider(
                "Seuil pour les doublons",
                0, 10, 5,
                help="Seuil pour considérer deux images comme identiques"
            )

            if st.button("🔍 Détecter les doublons"):
                with st.spinner("Recherche de doublons..."):
                    duplicates = st.session_state.image_search.find_duplicates(duplicate_threshold)

                    if duplicates:
                        st.warning(f"⚠️ {len(duplicates)} groupe(s) de doublons trouvé(s)")

                        for idx, group in enumerate(duplicates):
                            with st.expander(f"Groupe {idx + 1} - {len(group)} images"):
                                cols = st.columns(min(len(group), 4))
                                for i, image_path in enumerate(group):
                                    with cols[i % 4]:
                                        if os.path.exists(image_path):
                                            st.image(image_path, use_container_width=True)
                                            st.caption(os.path.basename(image_path))
                    else:
                        st.success("✅ Aucun doublon trouvé!")

    # Tab 3: Résultats
    with tab3:
        st.header("Fichiers de Résultats")

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
            st.subheader("🖼️ Images scrapées")

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
            st.info("ℹ️ Aucun résultat disponible. Veuillez d'abord effectuer un scraping.")


if __name__ == "__main__":
    main()
