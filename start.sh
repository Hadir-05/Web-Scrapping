#!/bin/bash

# Script de démarrage rapide pour Luxury AI Search

set -e

echo "🚀 Luxury AI Search - Quick Start"
echo "=================================="
echo ""

# Fonction d'aide
show_help() {
    echo "Usage: ./start.sh [option]"
    echo ""
    echo "Options:"
    echo "  streamlit    - Lancer l'application Streamlit MVP"
    echo "  backend      - Lancer le backend FastAPI"
    echo "  frontend     - Lancer le frontend React"
    echo "  docker       - Lancer tous les services avec Docker Compose"
    echo "  help         - Afficher cette aide"
    echo ""
}

# Vérifier les prérequis
check_models() {
    if [ ! -f "models/keyword_search.pth" ] || [ ! -f "models/image_similarity.pth" ]; then
        echo "❌ Erreur: Modèles non trouvés dans models/"
        echo ""
        echo "Veuillez placer vos modèles .pth dans le dossier models/:"
        echo "  - models/keyword_search.pth"
        echo "  - models/image_similarity.pth"
        echo ""
        exit 1
    fi
    echo "✅ Modèles trouvés"
}

# Lancer Streamlit
start_streamlit() {
    echo "🎨 Lancement de Streamlit MVP..."
    check_models

    if [ ! -d "venv" ]; then
        echo "📦 Création de l'environnement virtuel..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt

    echo "✅ Streamlit prêt!"
    echo "📖 Accès: http://localhost:8501"
    cd streamlit_app
    streamlit run app.py
}

# Lancer Backend
start_backend() {
    echo "⚡ Lancement du backend FastAPI..."
    check_models

    # Vérifier Redis
    if ! command -v redis-cli &> /dev/null; then
        echo "⚠️  Redis non installé. Lancement avec Docker..."
        docker run -d -p 6379:6379 --name luxury-redis redis:alpine 2>/dev/null || echo "Redis déjà en cours..."
    fi

    if [ ! -d "venv" ]; then
        echo "📦 Création de l'environnement virtuel..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r backend/requirements.txt

    echo "✅ Backend prêt!"
    echo "📖 API Docs: http://localhost:8000/docs"
    cd backend
    uvicorn app.main:app --reload --port 8000
}

# Lancer Frontend
start_frontend() {
    echo "🎨 Lancement du frontend React..."

    if [ ! -d "frontend/node_modules" ]; then
        echo "📦 Installation des dépendances..."
        cd frontend
        npm install
        cd ..
    fi

    echo "✅ Frontend prêt!"
    echo "📖 Accès: http://localhost:3000"
    cd frontend
    npm start
}

# Lancer Docker Compose
start_docker() {
    echo "🐳 Lancement avec Docker Compose..."

    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé"
        echo "Installez Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    check_models

    echo "📦 Build des images Docker..."
    docker-compose -f docker/docker-compose.yml build

    echo "🚀 Lancement des services..."
    docker-compose -f docker/docker-compose.yml up -d

    echo ""
    echo "✅ Tous les services sont lancés!"
    echo ""
    echo "📖 URLs disponibles:"
    echo "  - Streamlit MVP:  http://localhost:8501"
    echo "  - Backend API:    http://localhost:8000"
    echo "  - Frontend React: http://localhost:3000"
    echo "  - API Docs:       http://localhost:8000/docs"
    echo ""
    echo "📊 Voir les logs:"
    echo "  docker-compose -f docker/docker-compose.yml logs -f"
    echo ""
    echo "🛑 Arrêter les services:"
    echo "  docker-compose -f docker/docker-compose.yml down"
}

# Main
case "${1:-help}" in
    streamlit)
        start_streamlit
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    docker)
        start_docker
        ;;
    help|*)
        show_help
        ;;
esac
