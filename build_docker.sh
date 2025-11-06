#!/bin/bash

# Script de build de l'image Docker AliExpress Scraper
# Pour le développeur

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "🐳 Build Docker - AliExpress Scraper"
echo "=========================================="
echo ""

# Configuration
IMAGE_NAME="aliexpress-scraper"
IMAGE_TAG="latest"
IMAGE_FULL="${IMAGE_NAME}:${IMAGE_TAG}"

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé!"
    echo "   Installez Docker depuis: https://www.docker.com/get-started"
    exit 1
fi

echo "✅ Docker est installé"
echo ""

# Vérifier que nous sommes dans le bon dossier
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile non trouvé!"
    echo "   Lancez ce script depuis le dossier racine du projet"
    exit 1
fi

echo "✅ Dockerfile trouvé"
echo ""

# Afficher les infos
echo "📋 Configuration:"
echo "   Image: ${IMAGE_FULL}"
echo "   Build context: $(pwd)"
echo ""

# Demander confirmation
read -p "⚠️  Le build peut prendre 10-30 minutes. Continuer? (oui/non): " confirm
if [[ ! "$confirm" =~ ^(oui|o|yes|y)$ ]]; then
    echo "❌ Build annulé"
    exit 0
fi

echo ""
echo "🚀 Démarrage du build..."
echo "   Cela peut prendre 10-30 minutes"
echo "   ☕ Prenez un café!"
echo ""

# Build l'image
docker build \
    --tag "${IMAGE_FULL}" \
    --progress=plain \
    .

# Vérifier le succès
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ BUILD RÉUSSI!"
    echo "=========================================="
    echo ""
    echo "📊 Informations sur l'image:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo "🎯 Prochaines étapes:"
    echo ""
    echo "Option 1 - Tester localement:"
    echo "   docker-compose up"
    echo "   ou"
    echo "   docker run -p 8501:8501 ${IMAGE_FULL}"
    echo "   Puis ouvrir: http://localhost:8501"
    echo ""
    echo "Option 2 - Sauvegarder pour distribution:"
    echo "   ./save_docker.sh"
    echo "   Puis donner le fichier .tar au client"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ BUILD ÉCHOUÉ!"
    echo "=========================================="
    echo ""
    echo "💡 Solutions possibles:"
    echo "   1. Vérifiez votre connexion internet"
    echo "   2. Assurez-vous que Docker a assez d'espace disque (min 10GB)"
    echo "   3. Vérifiez que le Dockerfile est correct"
    echo "   4. Consultez les logs ci-dessus pour l'erreur exacte"
    exit 1
fi
