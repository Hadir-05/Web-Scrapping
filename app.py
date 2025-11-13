"""
Application Streamlit pour la recherche de produits
AliExpress et MercadoLibre par image avec CLIP
"""
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Scraping Multi-Plateformes",
    page_icon="🔍",
    layout="wide"
)

# Titre principal
st.title("🔍 Recherche de Produits par Image")
st.markdown("### Choisissez votre plateforme de scraping")

st.markdown("---")

# Introduction
st.markdown("""
Cette application vous permet de rechercher des produits similaires à une image de référence
sur différentes plateformes de e-commerce en utilisant la technologie CLIP (Vision AI).
""")

# Deux colonnes pour les deux plateformes
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🛒 AliExpress")
    st.markdown("""
    **Fonctionnalités:**
    - 🔍 Recherche par image native AliExpress
    - 🧠 Calcul de similarité avec CLIP ViT-L-14
    - 📊 Export Excel personnalisable
    - 💾 Sauvegarde automatique des résultats
    - 🖼️ Téléchargement des images produits

    **Technologie:**
    - Fingerprinting anti-détection
    - Session pool pour éviter les blocages
    - Téléchargements parallèles
    - Tri par score de similarité CLIP
    """)

    if st.button("➡️ Accéder à AliExpress", type="primary", use_container_width=True):
        st.switch_page("pages/1_🛒_AliExpress.py")

with col2:
    st.markdown("## 🌍 MercadoLibre")
    st.markdown("""
    **Fonctionnalités:**
    - 🔍 Scraping multi-pays (MX, AR, BR, CL, CO)
    - 🧠 Similarité CLIP avec segmentation avancée
    - 🎯 Détection de catégories produits (Vision Transformer)
    - 🔑 Extraction intelligente de détails (CLIPSeg + U-Net)
    - 📊 Export Excel avec scores détaillés

    **Technologie:**
    - BeautifulSoup pour scraping robuste
    - CLIP pour embeddings d'images
    - CLIPSeg pour segmentation sémantique
    - U-Net pour détection de détails
    - Dictionnaires multilingues (FR, EN, ES, PT)
    """)

    if st.button("➡️ Accéder à MercadoLibre", type="primary", use_container_width=True):
        st.switch_page("pages/2_🌍_MercadoLibre.py")

st.markdown("---")

# Section informations
with st.expander("ℹ️ Comment ça marche ?"):
    st.markdown("""
    ### 🚀 Processus de recherche

    1. **Upload** : Uploadez une image de référence du produit que vous cherchez
    2. **Configuration** : Choisissez les paramètres (nombre de résultats, catégorie, etc.)
    3. **Scraping** : L'application scrape la plateforme sélectionnée
    4. **Analyse CLIP** : Calcul des scores de similarité avec votre image
    5. **Résultats** : Affichage trié par pertinence
    6. **Export** : Téléchargement des données en Excel

    ### 🧠 Technologie CLIP

    CLIP (Contrastive Language-Image Pre-training) est un modèle d'IA de OpenAI qui comprend
    à la fois les images et le texte. Nous l'utilisons pour :
    - Calculer des embeddings (représentations vectorielles) d'images
    - Comparer la similarité entre votre image de référence et les produits trouvés
    - Segmenter les images pour extraire des détails spécifiques

    ### 📊 Organisation des résultats

    Les résultats de chaque recherche sont automatiquement sauvegardés dans :
    - `RESULTATS/aliexpress/recherche_YYYY-MM-DD_HH-MM-SS/`
    - `RESULTATS/mercadolibre/recherche_YYYY-MM-DD_HH-MM-SS/`

    Chaque dossier contient :
    - Images téléchargées
    - Métadonnées JSON
    - Fichier Excel exportable
    """)

with st.expander("🎯 Cas d'usage"):
    st.markdown("""
    ### Exemples d'utilisation

    - **Mode** : Rechercher des sacs, chaussures, vêtements similaires
    - **Accessoires** : Montres, bijoux, lunettes
    - **Électronique** : Gadgets, coques de téléphone
    - **Décoration** : Meubles, objets décoratifs
    - **Veille concurrentielle** : Surveiller les copies et contrefaçons
    - **Recherche de produits** : Retrouver un produit à partir d'une photo
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🔬 Powered by CLIP (OpenAI), CLIPSeg, U-Net, Vision Transformer</p>
    <p>Built with Streamlit 🎈</p>
</div>
""", unsafe_allow_html=True)
