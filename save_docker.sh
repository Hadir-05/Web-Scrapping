#!/bin/bash

# Script pour sauvegarder l'image Docker en fichier .tar
# Pour distribution au client

set -e

echo "=========================================="
echo "💾 Sauvegarde Image Docker"
echo "=========================================="
echo ""

# Configuration
IMAGE_NAME="aliexpress-scraper"
IMAGE_TAG="latest"
IMAGE_FULL="${IMAGE_NAME}:${IMAGE_TAG}"
OUTPUT_FILE="aliexpress-scraper-docker.tar"

# Vérifier que l'image existe
if ! docker image inspect "${IMAGE_FULL}" &> /dev/null; then
    echo "❌ L'image ${IMAGE_FULL} n'existe pas!"
    echo "   Buildez d'abord l'image avec: ./build_docker.sh"
    exit 1
fi

echo "✅ Image trouvée: ${IMAGE_FULL}"
echo ""

# Afficher la taille de l'image
IMAGE_SIZE=$(docker images "${IMAGE_NAME}" --format "{{.Size}}" | head -1)
echo "📊 Taille de l'image: ${IMAGE_SIZE}"
echo "⚠️  Le fichier .tar sera environ de la même taille"
echo ""

# Demander confirmation
read -p "Continuer la sauvegarde? (oui/non): " confirm
if [[ ! "$confirm" =~ ^(oui|o|yes|y)$ ]]; then
    echo "❌ Sauvegarde annulée"
    exit 0
fi

echo ""
echo "💾 Sauvegarde en cours..."
echo "   Fichier: ${OUTPUT_FILE}"
echo "   Cela peut prendre 5-10 minutes..."
echo ""

# Sauvegarder l'image
docker save "${IMAGE_FULL}" -o "${OUTPUT_FILE}"

# Vérifier le succès
if [ $? -eq 0 ] && [ -f "${OUTPUT_FILE}" ]; then
    FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)

    echo ""
    echo "=========================================="
    echo "✅ SAUVEGARDE RÉUSSIE!"
    echo "=========================================="
    echo ""
    echo "📦 Fichier créé:"
    echo "   Nom: ${OUTPUT_FILE}"
    echo "   Taille: ${FILE_SIZE}"
    echo "   Emplacement: $(pwd)/${OUTPUT_FILE}"
    echo ""
    echo "📤 Distribution au client:"
    echo ""
    echo "1. Donnez ces fichiers au client:"
    echo "   ✅ ${OUTPUT_FILE}"
    echo "   ✅ run_docker.sh (script de lancement)"
    echo "   ✅ README_DOCKER.md (guide d'utilisation)"
    echo ""
    echo "2. Le client devra:"
    echo "   - Installer Docker Desktop"
    echo "   - Charger l'image: docker load < ${OUTPUT_FILE}"
    echo "   - Lancer: ./run_docker.sh"
    echo "   - Ouvrir: http://localhost:8501"
    echo ""
    echo "💡 Conseil: Compressez le .tar avec:"
    echo "   gzip ${OUTPUT_FILE}"
    echo "   (Réduira la taille de ~30%)"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ SAUVEGARDE ÉCHOUÉE!"
    echo "=========================================="
    exit 1
fi
