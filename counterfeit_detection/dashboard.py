"""
Advanced Streamlit Dashboard for Counterfeit Detection System
Tableau de bord pour la détection de contrefaçons
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter les chemins pour les imports
sys.path.append(str(Path(__file__).parent))

from database.models import DatabaseManager, CounterfeitProduct, AuthenticProduct
from scrapers.aliexpress_scraper import AliExpressScraper
from scrapers.dhgate_scraper import DHgateScraper
from detectors.counterfeit_detector import CounterfeitDetector

# Configuration de la page
st.set_page_config(
    page_title="Anti-Counterfeit Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def apply_custom_css():
    """CSS personnalisé pour le dashboard"""
    st.markdown("""
    <style>
    /* Design professionnel */
    .main {
        background-color: #F8F9FA;
    }

    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Arial', sans-serif;
    }

    /* Cards de statistiques */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    /* Alert boxes */
    .alert-high {
        background-color: #FFE5E5;
        border-left: 4px solid #E74C3C;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    .alert-medium {
        background-color: #FFF4E5;
        border-left: 4px solid #F39C12;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #3498DB;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
    }

    .stButton>button:hover {
        background-color: #2980B9;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialise les variables de session"""
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()

    if 'detector' not in st.session_state:
        st.session_state.detector = CounterfeitDetector()

    if 'scrapers' not in st.session_state:
        st.session_state.scrapers = {
            'AliExpress': AliExpressScraper(),
            'DHgate': DHgateScraper()
        }


def render_sidebar():
    """Barre latérale avec navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/2C3E50/FFFFFF?text=ANTI-COUNTERFEIT", use_column_width=True)
        st.markdown("---")

        st.markdown("### 🎯 Navigation")
        page = st.radio(
            "",
            options=[
                "📊 Dashboard",
                "🔍 New Scan",
                "📋 Detections List",
                "⚙️ Configuration",
                "📈 Analytics"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Stats rapides
        stats = st.session_state.db.get_statistics()
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Detections", stats.get('total_counterfeits', 0))
        st.metric("High Risk", stats.get('high_risk_count', 0), delta="Critical")

        st.markdown("---")

        st.markdown("""
        <div style='text-align: center; color: #7F8C8D;'>
            <small>🛡️ Anti-Counterfeit System v1.0</small>
        </div>
        """, unsafe_allow_html=True)

    return page


def render_dashboard():
    """Page principale du dashboard"""
    st.markdown("# 🛡️ Anti-Counterfeit Detection Dashboard")
    st.markdown("Système de détection de contrefaçons pour produits de luxe")

    st.markdown("---")

    # Statistiques principales
    col1, col2, col3, col4 = st.columns(4)

    stats = st.session_state.db.get_statistics()

    with col1:
        st.metric(
            "Total Detections",
            stats.get('total_counterfeits', 0),
            delta="+12 today"
        )

    with col2:
        st.metric(
            "High Risk",
            stats.get('high_risk_count', 0),
            delta="Critical",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "Authentic Products",
            stats.get('total_authentic', 0)
        )

    with col4:
        st.metric(
            "Sites Monitored",
            len(st.session_state.scrapers),
            delta="Active"
        )

    st.markdown("---")

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Detections by Site")
        render_detections_by_site_chart(stats)

    with col2:
        st.markdown("### ⚠️ Risk Distribution")
        render_risk_distribution_chart()

    st.markdown("---")

    # Dernières détections
    st.markdown("### 🚨 Recent High-Risk Detections")
    render_recent_detections()


def render_detections_by_site_chart(stats):
    """Graphique des détections par site"""
    # Données de démonstration
    data = {
        'Site': ['AliExpress', 'DHgate', 'Wish', 'Temu'],
        'Detections': [45, 32, 18, 12]
    }

    fig = px.bar(
        data,
        x='Site',
        y='Detections',
        color='Detections',
        color_continuous_scale='Reds'
    )

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_column_width=True)


def render_risk_distribution_chart():
    """Graphique de distribution des risques"""
    data = {
        'Risk Level': ['Low', 'Medium', 'High', 'Critical'],
        'Count': [15, 25, 40, 27]
    }

    fig = px.pie(
        data,
        values='Count',
        names='Risk Level',
        color='Risk Level',
        color_discrete_map={
            'Low': '#27AE60',
            'Medium': '#F39C12',
            'High': '#E67E22',
            'Critical': '#E74C3C'
        }
    )

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_column_width=True)


def render_recent_detections():
    """Affiche les détections récentes"""
    # Récupérer les contrefaçons de la DB
    counterfeits = st.session_state.db.get_counterfeits(
        filters={'min_risk': 0.7},
        limit=10
    )

    if not counterfeits:
        st.info("No high-risk detections yet. Run a scan to detect counterfeits.")
        return

    for counterfeit in counterfeits:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                if counterfeit.image_urls:
                    st.image(counterfeit.image_urls[0], use_column_width=True)

            with col2:
                risk_color = "🔴" if counterfeit.overall_risk_score >= 0.85 else "🟠"
                st.markdown(f"{risk_color} **{counterfeit.title[:80]}...**")
                st.markdown(f"**Site:** {counterfeit.source_site} | **Price:** ${counterfeit.price:.2f}")
                st.markdown(f"**Risk Score:** {counterfeit.overall_risk_score:.1%}")

            with col3:
                st.markdown(f"**Status:** {counterfeit.status}")
                if st.button("View Details", key=f"view_{counterfeit.id}"):
                    st.session_state.selected_counterfeit = counterfeit.id

            st.markdown("---")


def render_new_scan():
    """Page pour lancer un nouveau scan"""
    st.markdown("# 🔍 New Counterfeit Scan")
    st.markdown("Search e-commerce sites for potential counterfeits")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Sélection du site
        site = st.selectbox(
            "Select E-commerce Site",
            options=list(st.session_state.scrapers.keys())
        )

        # Requête de recherche
        query = st.text_input(
            "Search Query",
            placeholder="Ex: Louis Vuitton bag, Gucci shoes, Rolex watch..."
        )

        # Nombre de pages
        max_pages = st.slider("Maximum Pages to Scan", 1, 10, 3)

    with col2:
        st.markdown("### ⚙️ Scan Options")
        auto_detect = st.checkbox("Auto-detect brands", value=True)
        deep_analysis = st.checkbox("Deep analysis (slower)", value=False)

    st.markdown("---")

    if st.button("🚀 Start Scan", type="primary"):
        if not query:
            st.error("Please enter a search query")
            return

        run_scan(site, query, max_pages, auto_detect, deep_analysis)


def run_scan(site: str, query: str, max_pages: int, auto_detect: bool, deep_analysis: bool):
    """Exécute un scan de contrefaçons"""
    scraper = st.session_state.scrapers[site]
    detector = st.session_state.detector
    db = st.session_state.db

    progress_bar = st.progress(0)
    status_text = st.empty()

    # 1. Scraping
    status_text.text(f"🔍 Scanning {site} for: {query}...")
    products = scraper.search(query, max_pages=max_pages)
    progress_bar.progress(0.3)

    if not products:
        st.warning(f"No products found on {site}")
        return

    status_text.text(f"✅ Found {len(products)} products. Analyzing...")
    progress_bar.progress(0.5)

    # 2. Récupérer les produits authentiques
    authentic_products = []  # TODO: Récupérer depuis la DB

    # 3. Détection
    counterfeits_found = 0

    for i, product in enumerate(products):
        # Détecter si c'est une contrefaçon
        detection_result = detector.detect_counterfeit(product, authentic_products)

        if detection_result['overall_risk_score'] >= 0.5:
            # Sauvegarder dans la DB
            db.add_counterfeit(
                detection_id=f"{site}_{hash(product['url'])}_{int(datetime.now().timestamp())}",
                source_site=site,
                source_url=product['url'],
                title=product['title'],
                price=product.get('price'),
                image_urls=product.get('image_urls', []),
                seller_name=product.get('seller_name'),
                similarity_score=detection_result['similarity_score'],
                keyword_match_score=detection_result['keyword_match_score'],
                price_suspicion_score=detection_result['price_suspicion_score'],
                overall_risk_score=detection_result['overall_risk_score'],
                confidence_level=detection_result['confidence_level'],
                detected_brands=detection_result['detected_brands'],
                status='DETECTED'
            )

            counterfeits_found += 1

        # Update progress
        progress = 0.5 + (0.5 * (i + 1) / len(products))
        progress_bar.progress(progress)

    progress_bar.progress(1.0)
    status_text.text(f"✅ Scan complete!")

    # Résultats
    st.success(f"🎯 Scan Complete!")
    st.markdown(f"""
    - **Products scanned:** {len(products)}
    - **Counterfeits detected:** {counterfeits_found}
    - **Detection rate:** {(counterfeits_found/len(products)*100):.1f}%
    """)

    if counterfeits_found > 0:
        st.warning(f"⚠️ {counterfeits_found} potential counterfeits found! Check the Detections List.")


def render_detections_list():
    """Page listant toutes les détections"""
    st.markdown("# 📋 Counterfeit Detections List")
    st.markdown("Manage and review detected counterfeits")

    st.markdown("---")

    # Filtres
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_site = st.selectbox("Filter by Site", ["All"] + list(st.session_state.scrapers.keys()))

    with col2:
        filter_risk = st.selectbox("Filter by Risk", ["All", "Critical (>85%)", "High (>70%)", "Medium (>50%)"])

    with col3:
        filter_status = st.selectbox("Filter by Status", ["All", "DETECTED", "REVIEWED", "CONFIRMED"])

    # Appliquer les filtres
    filters = {}
    if filter_site != "All":
        filters['site'] = filter_site
    if filter_risk == "Critical (>85%)":
        filters['min_risk'] = 0.85
    elif filter_risk == "High (>70%)":
        filters['min_risk'] = 0.70
    elif filter_risk == "Medium (>50%)":
        filters['min_risk'] = 0.50

    counterfeits = st.session_state.db.get_counterfeits(filters=filters, limit=50)

    st.markdown(f"### {len(counterfeits)} Detections Found")

    # Tableau
    if counterfeits:
        data = []
        for c in counterfeits:
            data.append({
                'ID': c.id,
                'Site': c.source_site,
                'Title': c.title[:50] + '...' if len(c.title) > 50 else c.title,
                'Price': f"${c.price:.2f}" if c.price else 'N/A',
                'Risk Score': f"{c.overall_risk_score:.1%}",
                'Status': c.status,
                'Detected': c.first_detected_at.strftime('%Y-%m-%d %H:%M')
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_column_width=True, height=600)
    else:
        st.info("No detections found with the selected filters.")


def render_configuration():
    """Page de configuration"""
    st.markdown("# ⚙️ Configuration")
    st.markdown("Configure the anti-counterfeit system")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🏷️ Brands", "🔍 Scrapers", "🔔 Alerts"])

    with tab1:
        st.markdown("### Luxury Brands to Monitor")
        st.markdown("Add or remove brands to monitor for counterfeits")

        brands = st.session_state.detector.luxury_brands

        new_brand = st.text_input("Add new brand")
        if st.button("Add Brand"):
            if new_brand and new_brand not in brands:
                brands.append(new_brand)
                st.success(f"Added {new_brand}")

        st.markdown("**Current Brands:**")
        for brand in brands:
            st.markdown(f"- {brand}")

    with tab2:
        st.markdown("### Scraper Configuration")

        for site_name, scraper in st.session_state.scrapers.items():
            with st.expander(f"{site_name} Settings"):
                st.markdown(f"**Base URL:** {scraper.base_url}")
                st.checkbox(f"Enable {site_name}", value=True, key=f"enable_{site_name}")
                st.number_input(f"Max pages per scan", value=5, min_value=1, max_value=20, key=f"max_pages_{site_name}")

    with tab3:
        st.markdown("### Alert Configuration")

        st.checkbox("Email alerts", value=False)
        email = st.text_input("Email address", "admin@company.com")

        st.checkbox("Webhook alerts", value=False)
        webhook = st.text_input("Webhook URL")

        st.slider("Alert threshold (risk score)", 0.0, 1.0, 0.7)


def render_analytics():
    """Page d'analytics avancées"""
    st.markdown("# 📈 Analytics & Reports")
    st.markdown("Advanced analytics and trend analysis")

    st.markdown("---")

    # Timeline
    st.markdown("### 📅 Detections Timeline (Last 30 Days)")
    render_timeline_chart()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏷️ Top Brands Targeted")
        render_top_brands_chart()

    with col2:
        st.markdown("### 💰 Price Distribution")
        render_price_distribution_chart()


def render_timeline_chart():
    """Graphique temporel des détections"""
    # Données de démo
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    detections = [int(20 + 15 * abs(np.sin(i/3))) for i in range(30)]

    import numpy as np

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=detections,
        mode='lines+markers',
        name='Detections',
        line=dict(color='#E74C3C', width=2),
        fill='tozeroy'
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="Date",
        yaxis_title="Detections"
    )

    st.plotly_chart(fig, use_column_width=True)


def render_top_brands_chart():
    """Top marques ciblées"""
    data = {
        'Brand': ['Louis Vuitton', 'Gucci', 'Rolex', 'Hermès', 'Chanel'],
        'Count': [45, 38, 32, 28, 22]
    }

    fig = px.bar(data, x='Count', y='Brand', orientation='h', color='Count', color_continuous_scale='Reds')
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)

    st.plotly_chart(fig, use_column_width=True)


def render_price_distribution_chart():
    """Distribution des prix"""
    import numpy as np

    prices = np.random.lognormal(3, 1, 100)

    fig = px.histogram(x=prices, nbins=20, color_discrete_sequence=['#3498DB'])
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    fig.update_xaxes(title="Price ($)")
    fig.update_yaxes(title="Count")

    st.plotly_chart(fig, use_column_width=True)


def main():
    """Fonction principale"""
    apply_custom_css()
    initialize_session_state()

    # Navigation
    page = render_sidebar()

    # Routing
    if "Dashboard" in page:
        render_dashboard()
    elif "New Scan" in page:
        render_new_scan()
    elif "Detections List" in page:
        render_detections_list()
    elif "Configuration" in page:
        render_configuration()
    elif "Analytics" in page:
        render_analytics()


if __name__ == "__main__":
    main()
