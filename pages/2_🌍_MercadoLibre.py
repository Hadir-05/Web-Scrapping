"""
Application Streamlit pour la recherche de produits MercadoLibre par image avec CLIP
Scraping avec BeautifulSoup + analyse de similarité avancée (CLIPSeg + U-Net)
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import tempfile
from typing import List, Dict
import pandas as pd
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Recherche MercadoLibre par Image",
    page_icon="🌍",
    layout="wide"
)

# Domaines MercadoLibre par pays
MERCADOLIBRE_DOMAINS = {
    "Argentina": "mercadolibre.com.ar",
    "Brasil": "mercadolivre.com.br",
    "Chile": "mercadolibre.cl",
    "Colombia": "mercadolibre.com.co",
    "México": "mercadolibre.com.mx",
}

# Produits disponibles pour la recherche
PRODUCTS = [
    "255",
    "Timeless",
    "Chanel 22",
    "Slingback",
    "Baskets",
    "J12",
    "Première",
    "Coco Crush",
    "Costume Jewelry",
    "Veste Tweed",
    "Accessories",
    "Coco Mademoiselle"
]

def get_next_output_dir():
    """Générer le prochain nom de dossier unique pour la recherche"""
    base_dir = Path("RESULTATS/mercadolibre")
    base_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = base_dir / f"recherche_{timestamp}"

    counter = 1
    while output_dir.exists():
        output_dir = base_dir / f"recherche_{timestamp}_{counter}"
        counter += 1

    return str(output_dir)

def build_search_url(domain: str, keyword: str, offset: int = 0) -> str:
    """Construire l'URL de recherche MercadoLibre avec pagination"""
    base_url = f"https://listado.{domain}/{keyword}"
    if offset > 0:
        base_url += f"_Desde_{offset+1}"
    # Remplacer les espaces par des tirets pour MercadoLibre
    keyword_formatted = keyword.replace(" ", "-").lower()
    return base_url.replace(keyword, keyword_formatted)

def scrape_page(url: str, max_items_per_page: int = 50) -> List[Dict]:
    """
    Scraper une page de résultats MercadoLibre
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        listings = []

        # Trouver tous les éléments de produits
        items = soup.find_all('li', class_='ui-search-layout__item')[:max_items_per_page]

        for item in items:
            try:
                # Titre
                title_tag = item.find('h2', class_='ui-search-item__title')
                title = title_tag.get_text(strip=True) if title_tag else "Sans titre"

                # Prix
                price_tag = item.find('span', class_='andes-money-amount__fraction')
                currency_tag = item.find('span', class_='andes-money-amount__currency-symbol')
                price = ""
                if currency_tag and price_tag:
                    price = f"{currency_tag.get_text(strip=True)} {price_tag.get_text(strip=True)}"
                elif price_tag:
                    price = price_tag.get_text(strip=True)
                else:
                    price = "N/A"

                # Lien produit
                link_tag = item.find('a', class_='ui-search-link')
                listing_url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else ""

                # Image principale
                img_tag = item.find('img', class_='ui-search-result-image__element')
                image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""

                if title and listing_url and image_url:
                    listings.append({
                        'title': title,
                        'price': price,
                        'listing_url': listing_url,
                        'image_url': image_url,
                        'collection_date': datetime.now()
                    })
            except Exception as e:
                print(f"Erreur lors du parsing d'un item: {e}")
                continue

        return listings

    except Exception as e:
        print(f"Erreur lors du scraping de {url}: {e}")
        st.error(f"Erreur de connexion: {str(e)}")
        return []

def scrape_all(domain: str, keyword: str, max_results: int = 50) -> List[Dict]:
    """Scraper plusieurs pages de résultats jusqu'à obtenir max_results produits"""
    all_listings = []
    page = 0
    items_per_page = 50  # MercadoLibre affiche ~50 items par page

    progress_bar = st.progress(0)
    status_text = st.empty()

    while len(all_listings) < max_results:
        offset = page * items_per_page
        url = build_search_url(domain, keyword, offset)

        status_text.text(f"🔍 Scraping page {page + 1}... ({len(all_listings)}/{max_results} produits)")

        page_listings = scrape_page(url, max_items_per_page=min(items_per_page, max_results - len(all_listings)))

        if not page_listings:
            st.warning(f"⚠️ Aucun résultat trouvé sur la page {page + 1}. Fin du scraping.")
            break

        all_listings.extend(page_listings)
        page += 1

        # Mise à jour de la barre de progression
        progress = min(len(all_listings) / max_results, 1.0)
        progress_bar.progress(progress)

        # Limiter à max 10 pages pour éviter de bloquer
        if page >= 10:
            st.info(f"ℹ️ Limite de 10 pages atteinte. {len(all_listings)} produits trouvés.")
            break

    progress_bar.empty()
    status_text.empty()

    return all_listings[:max_results]

def download_and_save_images(listings: List[Dict], output_dir: str):
    """Télécharger les images des produits scrapés"""
    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, listing in enumerate(listings):
        try:
            status_text.text(f"📥 Téléchargement image {idx + 1}/{len(listings)}...")

            img_url = listing['image_url']
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()

            # Sauvegarder l'image
            img_filename = f"product_{idx:04d}.jpg"
            img_path = images_dir / img_filename
            with open(img_path, 'wb') as f:
                f.write(response.content)

            listing['local_image_path'] = str(img_path)

            progress = (idx + 1) / len(listings)
            progress_bar.progress(progress)

        except Exception as e:
            print(f"Erreur téléchargement image {idx}: {e}")
            listing['local_image_path'] = None

    progress_bar.empty()
    status_text.empty()

    return listings

def save_results(listings: List[Dict], output_dir: str):
    """Sauvegarder les résultats dans un fichier JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convertir les dates en strings pour JSON
    listings_json = []
    for listing in listings:
        listing_copy = listing.copy()
        listing_copy['collection_date'] = listing_copy['collection_date'].isoformat()
        listings_json.append(listing_copy)

    json_path = output_path / "listings.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(listings_json, f, ensure_ascii=False, indent=2)

    return json_path

def init_session_state():
    """Initialiser les variables de session"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'uploaded_image_path' not in st.session_state:
        st.session_state.uploaded_image_path = None
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = None
    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = set()

def main():
    """Fonction principale de l'application"""
    init_session_state()

    st.title("🌍 Recherche de Produits MercadoLibre par Image")
    st.markdown("### Scraping + Analyse CLIP avec segmentation avancée (CLIPSeg + U-Net)")
    st.markdown("---")

    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Afficher le prochain dossier qui sera créé
        next_dir = get_next_output_dir()
        st.info(f"📁 **Prochaine recherche:** `{next_dir}`")
        st.caption("Un nouveau dossier sera créé automatiquement à chaque recherche")

        # Liste des recherches précédentes
        resultats_dir = Path("RESULTATS/mercadolibre")
        if resultats_dir.exists():
            existing_searches = sorted(resultats_dir.glob("recherche_*"), reverse=True)
            if existing_searches:
                st.markdown("### 📂 Recherches Précédentes")
                for search_dir in existing_searches[:5]:
                    # Compter les produits
                    json_file = search_dir / "listings.json"
                    count = 0
                    if json_file.exists():
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                listings = json.load(f)
                                count = len(listings)
                        except:
                            pass
                    st.caption(f"📦 {search_dir.name} ({count} produits)")

        st.markdown("---")

        # Sélection du pays
        country = st.selectbox(
            "🌎 Pays MercadoLibre",
            list(MERCADOLIBRE_DOMAINS.keys()),
            index=4  # México par défaut
        )

        max_results = st.slider(
            "Nombre max de produits",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="Nombre maximum de produits à scraper"
        )

        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        if st.session_state.search_results:
            st.metric("Produits trouvés", len(st.session_state.search_results))

        st.markdown("---")
        st.markdown("### ℹ️ Comment ça marche ?")
        st.markdown("""
        1. Uploadez une image de référence
        2. Choisissez le produit et le pays
        3. L'app scrape MercadoLibre
        4. **CLIP + CLIPSeg + U-Net** analysent les images
        5. Résultats triés par similarité
        6. Export Excel disponible
        """)

        st.markdown("### 🎯 Technologie")
        st.markdown("""
        - **Scraping** : BeautifulSoup
        - **CLIP** : Embeddings d'images
        - **CLIPSeg** : Segmentation sémantique
        - **U-Net** : Détection de détails
        - **ViT** : Classification de catégories
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

                # Sélection du produit
                product = st.selectbox(
                    "🏷️ Type de produit",
                    PRODUCTS,
                    help="Sélectionnez le type de produit que vous recherchez"
                )

                # Mot-clé de recherche
                keyword = st.text_input(
                    "🔍 Mot-clé de recherche",
                    value=product.lower(),
                    placeholder="Ex: chanel bag, watch luxury, etc.",
                    help="Mot-clé utilisé pour la recherche sur MercadoLibre"
                )

                st.info(f"""
                **Ce que l'application va faire :**
                - Scraper MercadoLibre {country} pour "{keyword}"
                - Télécharger les images des produits
                - **[TODO]** Analyser avec CLIP, CLIPSeg et U-Net
                - **[TODO]** Calculer les scores de similarité
                - Trier par pertinence

                ⚡ **Version actuelle : Scraping de base**
                🚧 **À venir : Intégration CLIP/CLIPSeg/U-Net complète**
                """)

                search_button = st.button(
                    "🔍 Rechercher sur MercadoLibre",
                    type="primary",
                    use_container_width=True
                )

                if search_button and keyword:
                    # Générer un nouveau dossier unique pour cette recherche
                    search_output_dir = get_next_output_dir()
                    st.session_state.output_dir = search_output_dir

                    with st.spinner(f"🔄 Scraping de MercadoLibre {country}..."):
                        st.info(f"📁 Résultats seront sauvegardés dans: `{search_output_dir}`")

                        try:
                            # Scraper MercadoLibre
                            domain = MERCADOLIBRE_DOMAINS[country]
                            listings = scrape_all(domain, keyword, max_results)

                            if listings:
                                st.success(f"✅ {len(listings)} produits trouvés!")

                                # Télécharger les images
                                with st.spinner("📥 Téléchargement des images..."):
                                    listings = download_and_save_images(listings, search_output_dir)

                                # Sauvegarder les résultats
                                json_path = save_results(listings, search_output_dir)
                                st.success(f"📁 Résultats sauvegardés dans: `{search_output_dir}`")

                                st.session_state.search_results = listings

                                # TODO: Intégration CLIP/CLIPSeg/U-Net ici
                                st.warning("""
                                🚧 **Analyse CLIP en développement**

                                Pour l'instant, les résultats sont affichés tels quels.
                                L'intégration complète avec CLIP, CLIPSeg et U-Net sera ajoutée
                                pour calculer les scores de similarité et trier les résultats.

                                Les fonctions sont disponibles dans `src/mercadolibre_helpers.py`.
                                """)

                            else:
                                st.warning(f"⚠️ Aucun produit trouvé pour '{keyword}' sur MercadoLibre {country}.")

                        except Exception as e:
                            st.error(f"❌ Erreur lors du scraping: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

        # Afficher un aperçu des résultats
        if st.session_state.search_results:
            st.markdown("---")
            st.subheader("🎯 Produits Trouvés")

            listings = st.session_state.search_results

            # Afficher les 6 premiers résultats
            cols = st.columns(3)
            for idx, listing in enumerate(listings[:6]):
                with cols[idx % 3]:
                    # Afficher l'image
                    if listing.get('local_image_path') and os.path.exists(listing['local_image_path']):
                        st.image(listing['local_image_path'], use_container_width=True)
                    elif listing.get('image_url'):
                        st.image(listing['image_url'], use_container_width=True)

                    st.markdown(f"**{listing['title'][:60]}...**")
                    st.markdown(f"💰 **Prix:** {listing['price']}")

                    if listing['listing_url']:
                        st.markdown(f"[🔗 Voir sur MercadoLibre]({listing['listing_url']})")

    # Tab 2: Résultats Détaillés
    with tab2:
        st.header("📋 Tous les Résultats")

        if st.session_state.search_results:
            listings = st.session_state.search_results

            for idx, listing in enumerate(listings):
                col_img, col_info = st.columns([1, 3])

                with col_img:
                    # Afficher l'image
                    if listing.get('local_image_path') and os.path.exists(listing['local_image_path']):
                        st.image(listing['local_image_path'], use_container_width=True)
                    elif listing.get('image_url'):
                        st.image(listing['image_url'], use_container_width=True)
                    else:
                        st.markdown("### 🖼️")
                        st.caption("Pas d'image")

                with col_info:
                    st.markdown(f"### 🔢 Produit {idx + 1}")
                    st.markdown(f"**{listing['title']}**")
                    st.markdown(f"💰 **Prix:** {listing['price']}")
                    if listing['listing_url']:
                        st.markdown(f"[➡️ Voir sur MercadoLibre]({listing['listing_url']})")

                st.markdown("---")

        else:
            st.info("ℹ️ Aucun résultat disponible. Uploadez une image et lancez la recherche.")

    # Tab 3: Export
    with tab3:
        st.header("📊 Sélection et Export Excel")

        if st.session_state.search_results:
            listings = st.session_state.search_results

            st.markdown(f"### 📋 Sélectionnez les annonces à exporter ({len(listings)} résultats)")

            # Boutons de sélection
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Tout sélectionner"):
                    st.session_state.selected_products = set(range(len(listings)))
                    st.rerun()
            with col2:
                if st.button("❌ Tout désélectionner"):
                    st.session_state.selected_products = set()
                    st.rerun()
            with col3:
                st.metric("Sélectionnés", len(st.session_state.selected_products))

            st.markdown("---")

            # Afficher chaque produit avec checkbox
            for idx, listing in enumerate(listings):
                with st.container():
                    col_check, col_img, col_info = st.columns([0.5, 1, 3])

                    with col_check:
                        st.markdown("<br>", unsafe_allow_html=True)
                        is_checked = st.checkbox(
                            "Sélectionner",
                            value=idx in st.session_state.selected_products,
                            key=f"mercado_product_checkbox_{idx}",
                            label_visibility="collapsed"
                        )

                        if is_checked:
                            st.session_state.selected_products.add(idx)
                        else:
                            st.session_state.selected_products.discard(idx)

                    with col_img:
                        if listing.get('local_image_path') and os.path.exists(listing['local_image_path']):
                            st.image(listing['local_image_path'], use_container_width=True)
                        elif listing.get('image_url'):
                            st.image(listing['image_url'], use_container_width=True)
                        else:
                            st.markdown("🖼️")

                    with col_info:
                        st.markdown(f"**#{idx + 1}**")
                        st.markdown(f"**🏷️** {listing['title'][:100]}")
                        st.markdown(f"**💰** {listing['price']}")
                        if listing['listing_url']:
                            st.markdown(f"[🔗 Lien MercadoLibre]({listing['listing_url']})")

                    st.markdown("---")

            # Section d'export
            if st.session_state.selected_products:
                st.markdown("---")
                st.markdown("### 📥 Export Excel")

                # Champ keyword
                keyword = st.text_input(
                    "🔍 Mot-clé de recherche",
                    value="",
                    placeholder="Ex: chanel bag, luxury watch, etc.",
                    help="Le mot-clé utilisé pour la recherche"
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
                        # Préparer les données pour Excel
                        excel_data = []
                        for idx in sorted(st.session_state.selected_products):
                            listing = listings[idx]

                            excel_data.append({
                                'Date de détection': listing['collection_date'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(listing['collection_date'], datetime) else str(listing['collection_date']),
                                'URL': listing['listing_url'],
                                'Product Category': category if category else 'N/A',
                                'Product Name': listing['title'],
                                'Keyword': keyword if keyword else 'N/A',
                                'Marketplace': 'MercadoLibre',
                                'Prix': listing['price'],
                                'CLIP Score': 'N/A (en développement)',
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
                            file_name=f"mercadolibre_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
