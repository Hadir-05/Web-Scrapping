"""
Application Streamlit pour la recherche de produits AliExpress par image
"""
import streamlit as st
import asyncio
import os
import sys
import json
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from PIL import Image

from src.scraper.aliexpress_scraper import AliExpressImageSearchScraper
from src.image_search.image_similarity import ImageSimilaritySearch
from src.models.data_models import DataManager, ImageMetadata, ProductData

# Configuration pour Windows - utiliser ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


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


def run_aliexpress_search_sync(image_path: str, category: str, max_results: int, output_dir: str):
    """
    Exécuter la recherche AliExpress par catégorie + image de manière synchrone
    Utilise un thread séparé avec son propre event loop pour éviter les conflits
    """
    result_container = {'result': None, 'error': None}

    def run_in_thread():
        try:
            # Créer un nouvel event loop pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Exécuter la recherche
            scraper = AliExpressImageSearchScraper(output_dir)
            result = loop.run_until_complete(
                scraper.search_by_image(image_path, category, max_results, headless=True)
            )
            result_container['result'] = result

            # Nettoyer
            loop.close()
        except Exception as e:
            result_container['error'] = e

    # Lancer dans un thread séparé
    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()

    if result_container['error']:
        raise result_container['error']

    return result_container['result']


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


def calculate_similarity_scores(uploaded_image_path: str, product_data_list, output_dir: str = "output"):
    """Calculer les scores de similarité entre l'image uploadée et les produits trouvés"""
    print(f"=== CALCUL DE SIMILARITÉ ===")
    print(f"Image uploadée: {uploaded_image_path}")
    print(f"Nombre de produits: {len(product_data_list)}")

    # Charger le mapping URL → chemin local depuis image_metadata.json
    image_metadata_path = Path(output_dir) / "image_metadata.json"
    url_to_local_path = {}

    if image_metadata_path.exists():
        print(f"Chargement du mapping d'images...")
        with open(image_metadata_path, 'r', encoding='utf-8') as f:
            image_metadata = json.load(f)
            for img_meta in image_metadata:
                url = img_meta.get('src', '')
                local_path = img_meta.get('local_path', '')
                if url and local_path:
                    url_to_local_path[url] = local_path
        print(f"  {len(url_to_local_path)} mappings chargés")
    else:
        print(f"  ⚠️ Fichier image_metadata.json non trouvé")

    image_search = ImageSimilaritySearch(use_clip=True)

    # Ajouter toutes les images de produits à l'index
    images_added = 0
    for product in product_data_list:
        for img_url in product.product_image_paths:
            # Récupérer le chemin local correspondant
            local_path = url_to_local_path.get(img_url, img_url)

            if os.path.exists(local_path):
                print(f"  ✅ Ajout image: {local_path}")
                image_search.add_image(local_path, {
                    'product_title': product.title,
                    'product_url': product.item_url,
                    'product_price': product.price,
                    'original_url': img_url
                })
                images_added += 1
            else:
                print(f"  ⚠️ Image manquante: {local_path} (URL: {img_url})")

    print(f"Images ajoutées à l'index: {images_added}")

    # Statistiques
    stats = image_search.get_stats()
    print(f"Stats: {stats}")

    # Rechercher les images similaires avec CLIP
    # Threshold plus bas pour CLIP (similarité cosinus 0-1)
    print(f"Recherche de similarité...")
    similar_images = image_search.search_similar(
        uploaded_image_path,
        top_k=len(product_data_list) * 5,  # Plus de résultats
        threshold=0.1  # Seuil plus bas pour debug (10%)
    )

    print(f"Images similaires trouvées: {len(similar_images)}")

    # Créer un dictionnaire de scores par URL (pas par chemin local)
    similarity_scores = {}
    for local_path, score, metadata in similar_images:
        # Retrouver l'URL d'origine
        original_url = metadata.get('original_url', local_path)
        print(f"  Score: {score:.4f} - {original_url}")
        similarity_scores[original_url] = score

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
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="Nombre maximum de produits à rechercher (parcourt plusieurs pages si nécessaire)"
        )

        # Estimation du nombre de pages
        estimated_pages = max(1, (max_results + 39) // 40)
        st.caption(f"📄 Environ {estimated_pages} page(s) seront parcourues")

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
        3. L'image est uploadée sur AliExpress
        4. AliExpress trouve des produits similaires
        5. Les résultats sont téléchargés et triés
        6. Téléchargez les résultats en JSON
        """)

        st.markdown("### 🎯 Technologie")
        st.markdown("""
        - **Fingerprinting** : Empreintes réalistes
        - **Session Pool** : Gestion de sessions
        - **Concurrency** : Téléchargements parallèles
        - **Image Search** : Upload natif AliExpress
        - **CLIP Model** : ViT-L-14 (Laion2B) pour similarité
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

                # Champ de catégorie (optionnel, non utilisé avec image search)
                st.markdown("#### 🏷️ Catégorie (Optionnel)")
                category = st.text_input(
                    "Catégorie optionnelle",
                    value="",
                    placeholder="Laissez vide pour utiliser uniquement l'image",
                    help="Non requis - AliExpress utilise l'upload d'image natif"
                )

                st.info("""
                **Ce que l'application va faire :**
                - Se connecter à AliExpress
                - Uploader votre image sur leur système
                - Utiliser la recherche par image native d'AliExpress
                - Télécharger les produits similaires trouvés
                - Calculer les scores de similarité localement
                - Trier par pertinence

                ⚡ **Nouvelle version avec fingerprinting et sessions pour éviter la détection**
                """)

                search_button = st.button(
                    "🔍 Rechercher sur AliExpress",
                    type="primary",
                    use_container_width=True
                )

                if search_button and st.session_state.uploaded_image_path:
                    with st.spinner(f"🔄 Recherche par image en cours sur AliExpress... Cela peut prendre quelques minutes."):
                        try:
                            # Exécuter la recherche
                            image_metadata_list, product_data_list = run_aliexpress_search_sync(
                                st.session_state.uploaded_image_path,
                                category,
                                max_results,
                                output_dir
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

                                # Calculer les scores de similarité avec CLIP
                                with st.spinner("🧠 Calcul des similarités avec CLIP (ViT-L-14)..."):
                                    similarity_scores = calculate_similarity_scores(
                                        st.session_state.uploaded_image_path,
                                        product_data_list,
                                        output_dir
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
                product_data_list,
                st.session_state.output_dir
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
                    st.markdown(f"🧠 **CLIP Score:** {similarity_score:.1%}")

                    if product.item_url:
                        st.markdown(f"[🔗 Voir sur AliExpress]({product.item_url})")

    # Tab 2: Résultats Détaillés
    with tab2:
        st.header("📋 Tous les Résultats")

        if st.session_state.search_results and st.session_state.search_results[1]:
            image_metadata_list, product_data_list = st.session_state.search_results

            # Charger le mapping URL → local path
            output_path = Path(st.session_state.output_dir)
            image_metadata_path = output_path / "image_metadata.json"
            url_to_local_path = {}

            if image_metadata_path.exists():
                with open(image_metadata_path, 'r', encoding='utf-8') as f:
                    image_metadata = json.load(f)
                    for img_meta in image_metadata:
                        url = img_meta.get('src', '')
                        local_path = img_meta.get('local_path', '')
                        if url and local_path:
                            url_to_local_path[url] = local_path

            # Calculer les similarités
            similarity_scores = calculate_similarity_scores(
                st.session_state.uploaded_image_path,
                product_data_list,
                st.session_state.output_dir
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
                with st.expander(f"🔢 Produit {idx + 1} - {product.title[:80]} - CLIP: {similarity_score:.1%}"):
                    # Section images: 3 premières images
                    st.markdown("### 🖼️ Images du Produit")

                    # Récupérer les 3 premières images locales
                    local_image_paths = []
                    for img_url in product.product_image_paths[:3]:
                        local_path = url_to_local_path.get(img_url, img_url)
                        if os.path.exists(local_path):
                            local_image_paths.append(local_path)

                    if local_image_paths:
                        # Afficher en colonnes
                        cols = st.columns(len(local_image_paths))
                        for i, img_path in enumerate(local_image_paths):
                            with cols[i]:
                                st.image(img_path, use_container_width=True, caption=f"Image {i+1}")
                    else:
                        st.warning("Aucune image disponible localement")

                    st.markdown("---")

                    # Section détails
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown("### 📊 Informations Produit")
                        st.markdown(f"**🏷️ Nom:** {product.title}")
                        st.markdown(f"**💰 Prix:** {product.price}")
                        st.markdown(f"**🧠 Score CLIP:** {similarity_score:.2%}")
                        st.caption("Score calculé avec CLIP ViT-L-14 (Laion2B)")
                        st.markdown(f"**📅 Date:** {product.collection_date.strftime('%Y-%m-%d %H:%M')}")

                    with col2:
                        st.markdown("### 🔗 Liens")
                        if product.item_url:
                            st.markdown(f"[➡️ Voir sur AliExpress]({product.item_url})")
                            st.code(product.item_url, language=None)

                        st.markdown(f"**🖼️ Images disponibles:** {len(product.product_image_paths)}")

                    if product.description and product.description != product.title:
                        st.markdown("### 📝 Description")
                        st.markdown(product.description)

        else:
            st.info("ℹ️ Aucun résultat disponible. Uploadez une image et lancez la recherche.")

    # Tab 3: Export
    with tab3:
        st.header("📊 Sélection et Export Excel")

        if st.session_state.search_results and st.session_state.search_results[1]:
            image_metadata_list, product_data_list = st.session_state.search_results

            # Charger le mapping URL → local path
            output_path = Path(st.session_state.output_dir)
            image_metadata_path = output_path / "image_metadata.json"
            url_to_local_path = {}

            if image_metadata_path.exists():
                with open(image_metadata_path, 'r', encoding='utf-8') as f:
                    image_metadata = json.load(f)
                    for img_meta in image_metadata:
                        url = img_meta.get('src', '')
                        local_path = img_meta.get('local_path', '')
                        if url and local_path:
                            url_to_local_path[url] = local_path

            # Calculer les similarités
            similarity_scores = calculate_similarity_scores(
                st.session_state.uploaded_image_path,
                product_data_list,
                st.session_state.output_dir
            )

            # Trier par similarité
            sorted_products = []
            for product in product_data_list:
                max_score = 0
                for img_path in product.product_image_paths:
                    score = similarity_scores.get(img_path, 0)
                    max_score = max(max_score, score)
                sorted_products.append((product, max_score))

            sorted_products.sort(key=lambda x: x[1], reverse=True)

            st.markdown(f"### 📋 Sélectionnez les annonces à exporter ({len(sorted_products)} résultats)")

            # Initialiser la sélection dans session_state
            if 'selected_products' not in st.session_state:
                st.session_state.selected_products = set()

            # Boutons de sélection
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Tout sélectionner"):
                    st.session_state.selected_products = set(range(len(sorted_products)))
                    st.rerun()
            with col2:
                if st.button("❌ Tout désélectionner"):
                    st.session_state.selected_products = set()
                    st.rerun()
            with col3:
                st.metric("Sélectionnés", len(st.session_state.selected_products))

            st.markdown("---")

            # Afficher chaque produit avec checkbox
            for idx, (product, similarity_score) in enumerate(sorted_products):
                # Récupérer la première image
                first_image = None
                if product.product_image_paths:
                    first_img_url = product.product_image_paths[0]
                    first_image = url_to_local_path.get(first_img_url, first_img_url)

                # Créer un container pour chaque produit
                with st.container():
                    col_check, col_img, col_info = st.columns([0.5, 1, 3])

                    with col_check:
                        st.markdown("<br>", unsafe_allow_html=True)
                        is_selected = st.checkbox(
                            "Sélectionner",
                            value=idx in st.session_state.selected_products,
                            key=f"product_{idx}",
                            label_visibility="collapsed"
                        )

                        # Mettre à jour la sélection
                        if is_selected:
                            st.session_state.selected_products.add(idx)
                        else:
                            st.session_state.selected_products.discard(idx)

                    with col_img:
                        if first_image and os.path.exists(first_image):
                            st.image(first_image, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/150", use_container_width=True)

                    with col_info:
                        st.markdown(f"**#{idx + 1}** | **CLIP:** {similarity_score:.1%}")
                        st.markdown(f"**🏷️** {product.title[:100]}")
                        st.markdown(f"**💰** {product.price}")
                        if product.item_url:
                            st.markdown(f"[🔗 Lien AliExpress]({product.item_url})")

                    st.markdown("---")

            # Section d'export
            if st.session_state.selected_products:
                st.markdown("---")
                st.markdown("### 📥 Export Excel")

                # Champ keyword
                keyword = st.text_input(
                    "🔍 Mot-clé de recherche",
                    value="",
                    placeholder="Ex: sac chanel, montre luxe, etc.",
                    help="Le mot-clé utilisé pour la recherche (sera inclus dans l'Excel)"
                )

                # Champ catégorie
                category = st.text_input(
                    "🏷️ Catégorie produit",
                    value="",
                    placeholder="Ex: bags, watches, jewelry, clothing",
                    help="La catégorie du produit recherché"
                )

                if st.button("📊 Générer fichier Excel", type="primary", use_container_width=True):
                    try:
                        import pandas as pd
                        from io import BytesIO

                        # Préparer les données pour Excel
                        excel_data = []
                        for idx in sorted(st.session_state.selected_products):
                            product, similarity_score = sorted_products[idx]

                            excel_data.append({
                                'Date de détection': product.collection_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'URL': product.item_url,
                                'Product Category': category if category else 'N/A',
                                'Product Name': product.title,
                                'Keyword': keyword if keyword else 'N/A',
                                'Marketplace': 'AliExpress',
                                'Prix': product.price,
                                'CLIP Score': f"{similarity_score:.2%}",
                            })

                        # Créer DataFrame
                        df = pd.DataFrame(excel_data)

                        # Créer le fichier Excel en mémoire
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Produits')

                            # Ajuster la largeur des colonnes
                            worksheet = writer.sheets['Produits']
                            for idx, col in enumerate(df.columns):
                                max_length = max(
                                    df[col].astype(str).map(len).max(),
                                    len(col)
                                ) + 2
                                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

                        excel_buffer.seek(0)

                        # Bouton de téléchargement
                        st.download_button(
                            label="⬇️ Télécharger le fichier Excel",
                            data=excel_buffer,
                            file_name=f"aliexpress_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

                        st.success(f"✅ Fichier Excel généré avec {len(excel_data)} produits!")

                        # Aperçu
                        with st.expander("👁️ Aperçu des données"):
                            st.dataframe(df, use_container_width=True)

                    except ImportError:
                        st.error("❌ Pandas ou openpyxl n'est pas installé. Installez avec: pip install pandas openpyxl")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la génération du fichier Excel: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            else:
                st.info("ℹ️ Sélectionnez au moins un produit pour activer l'export Excel")

        else:
            st.info("ℹ️ Aucun résultat disponible. Uploadez une image et lancez la recherche.")


if __name__ == "__main__":
    main()
