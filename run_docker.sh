#!/bin/bash

# Script de lancement pour le CLIENT
# Charge et lance l'image Docker AliExpress Scraper

set -e

echo "=========================================="
echo "🚀 AliExpress Scraper - Lancement Docker"
echo "=========================================="
echo ""

# Configuration
IMAGE_NAME="aliexpress-scraper"
IMAGE_TAG="latest"
IMAGE_FULL="${IMAGE_NAME}:${IMAGE_TAG}"
IMAGE_FILE="aliexpress-scraper-docker.tar"
CONTAINER_NAME="aliexpress_scraper"
PORT=8501

# Fonction pour vérifier Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé!"
        echo ""
        echo "📥 Installation Docker:"
        echo "   Windows/Mac: https://www.docker.com/products/docker-desktop"
        echo "   Linux: sudo apt-get install docker.io"
        echo ""
        exit 1
    fi
    echo "✅ Docker est installé"
}

# Fonction pour charger l'image si nécessaire
load_image_if_needed() {
    if docker image inspect "${IMAGE_FULL}" &> /dev/null; then
        echo "✅ Image déjà chargée: ${IMAGE_FULL}"
        return 0
    fi

    echo "📦 Image non trouvée, chargement nécessaire..."

    if [ ! -f "${IMAGE_FILE}" ]; then
        echo "❌ Fichier ${IMAGE_FILE} non trouvé!"
        echo "   Assurez-vous que le fichier .tar est dans ce dossier"
        exit 1
    fi

    echo "💾 Chargement de l'image depuis ${IMAGE_FILE}..."
    echo "   Cela peut prendre 2-5 minutes..."

    docker load -i "${IMAGE_FILE}"

    if [ $? -eq 0 ]; then
        echo "✅ Image chargée avec succès!"
    else
        echo "❌ Échec du chargement de l'image"
        exit 1
    fi
}

# Fonction pour arrêter le container existant
stop_existing_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "🛑 Arrêt du container existant..."
        docker stop "${CONTAINER_NAME}" 2>/dev/null || true
        docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    fi
}

# Fonction pour vérifier que le port est libre
check_port() {
    if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep -q ":${PORT}.*LISTEN"; then
        echo "⚠️  Le port ${PORT} est déjà utilisé!"
        echo ""
        read -p "Voulez-vous arrêter l'application existante? (oui/non): " confirm
        if [[ "$confirm" =~ ^(oui|o|yes|y)$ ]]; then
            stop_existing_container
        else
            echo "❌ Lancement annulé"
            exit 1
        fi
    fi
}

# Fonction principale
main() {
    echo "🔍 Vérifications préalables..."
    echo ""

    # Vérifications
    check_docker
    load_image_if_needed
    check_port
    stop_existing_container

    echo ""
    echo "=========================================="
    echo "🚀 Lancement de l'application..."
    echo "=========================================="
    echo ""

    # Créer les dossiers de sortie s'ils n'existent pas
    mkdir -p output_recherche{1..5}

    # Lancer le container
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p ${PORT}:${PORT} \
        -v "$(pwd)/output_recherche1:/app/output_recherche1" \
        -v "$(pwd)/output_recherche2:/app/output_recherche2" \
        -v "$(pwd)/output_recherche3:/app/output_recherche3" \
        -v "$(pwd)/output_recherche4:/app/output_recherche4" \
        -v "$(pwd)/output_recherche5:/app/output_recherche5" \
        --restart unless-stopped \
        "${IMAGE_FULL}"

    if [ $? -eq 0 ]; then
        echo "✅ Container démarré avec succès!"
        echo ""
        echo "=========================================="
        echo "🎉 APPLICATION PRÊTE!"
        echo "=========================================="
        echo ""
        echo "🌐 Accès à l'application:"
        echo "   http://localhost:${PORT}"
        echo ""
        echo "📁 Résultats sauvegardés dans:"
        echo "   $(pwd)/output_recherche1/"
        echo "   $(pwd)/output_recherche2/"
        echo "   ..."
        echo ""
        echo "📊 Commandes utiles:"
        echo "   Voir les logs:        docker logs -f ${CONTAINER_NAME}"
        echo "   Arrêter:              docker stop ${CONTAINER_NAME}"
        echo "   Redémarrer:           docker restart ${CONTAINER_NAME}"
        echo "   Supprimer:            docker rm -f ${CONTAINER_NAME}"
        echo ""
        echo "⏳ Attendez 10-20 secondes que l'app démarre..."
        echo "   Puis ouvrez votre navigateur sur: http://localhost:${PORT}"
        echo ""

        # Optionnel: Ouvrir le navigateur automatiquement
        sleep 3
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:${PORT}" 2>/dev/null
        elif command -v open &> /dev/null; then
            open "http://localhost:${PORT}" 2>/dev/null
        elif command -v start &> /dev/null; then
            start "http://localhost:${PORT}" 2>/dev/null
        fi

    else
        echo ""
        echo "❌ Échec du démarrage du container"
        echo ""
        echo "💡 Vérifiez les logs:"
        echo "   docker logs ${CONTAINER_NAME}"
        exit 1
    fi
}

# Exécuter
main
