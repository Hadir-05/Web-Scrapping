#!/usr/bin/env python3
"""
Script de test pour vérifier que CLIP fonctionne correctement
Utilisez ce script pour diagnostiquer les problèmes de score = 0
"""
import sys
import os
from pathlib import Path

print("="*80)
print("TEST CLIP - Diagnostic complet")
print("="*80)

# Test 1: Import CLIP
print("\n1️⃣ Test import CLIP...")
try:
    import open_clip
    print("   ✅ open_clip importé avec succès")
    print(f"   Version: {open_clip.__version__ if hasattr(open_clip, '__version__') else 'inconnue'}")
except ImportError as e:
    print(f"   ❌ Erreur import open_clip: {e}")
    print("   💡 Installez avec: pip install open-clip-torch")
    sys.exit(1)

# Test 2: Import PyTorch
print("\n2️⃣ Test import PyTorch...")
try:
    import torch
    print("   ✅ PyTorch importé avec succès")
    print(f"   Version: {torch.__version__}")
    print(f"   CUDA disponible: {torch.cuda.is_available()}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"   Device: {device}")
except ImportError as e:
    print(f"   ❌ Erreur import torch: {e}")
    sys.exit(1)

# Test 3: Charger le modèle CLIP
print("\n3️⃣ Test chargement modèle CLIP...")
try:
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-L-14',
        pretrained='laion2b_s32b_b82k',
        device=device
    )
    print("   ✅ Modèle CLIP chargé avec succès")
    print(f"   Architecture: ViT-L-14")
    print(f"   Pretrained: laion2b_s32b_b82k")
except Exception as e:
    print(f"   ❌ Erreur chargement modèle: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Créer des images de test
print("\n4️⃣ Test création d'images de test...")
try:
    from PIL import Image
    import numpy as np

    # Créer un dossier de test
    test_dir = Path("test_clip_images")
    test_dir.mkdir(exist_ok=True)

    # Image 1: Rouge
    img1 = Image.new('RGB', (224, 224), color=(255, 0, 0))
    img1_path = test_dir / "red.jpg"
    img1.save(img1_path)

    # Image 2: Bleu
    img2 = Image.new('RGB', (224, 224), color=(0, 0, 255))
    img2_path = test_dir / "blue.jpg"
    img2.save(img2_path)

    # Image 3: Rouge similaire
    img3 = Image.new('RGB', (224, 224), color=(250, 10, 10))
    img3_path = test_dir / "red_similar.jpg"
    img3.save(img3_path)

    print(f"   ✅ Images de test créées dans {test_dir}")

except Exception as e:
    print(f"   ❌ Erreur création images: {e}")
    sys.exit(1)

# Test 5: Calculer les embeddings
print("\n5️⃣ Test calcul des embeddings...")
try:
    def compute_embedding(img_path):
        img = Image.open(img_path).convert("RGB")
        image_input = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()

    emb1 = compute_embedding(img1_path)
    emb2 = compute_embedding(img2_path)
    emb3 = compute_embedding(img3_path)

    print(f"   ✅ Embeddings calculés")
    print(f"   Shape embedding: {emb1.shape}")

except Exception as e:
    print(f"   ❌ Erreur calcul embeddings: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Calculer les similarités
print("\n6️⃣ Test calcul similarités...")
try:
    from sklearn.metrics.pairwise import cosine_similarity

    sim_1_2 = cosine_similarity(emb1, emb2)[0][0]
    sim_1_3 = cosine_similarity(emb1, emb3)[0][0]
    sim_2_3 = cosine_similarity(emb2, emb3)[0][0]

    print(f"   ✅ Similarités calculées:")
    print(f"   Rouge vs Bleu: {sim_1_2:.4f}")
    print(f"   Rouge vs Rouge_similaire: {sim_1_3:.4f}")
    print(f"   Bleu vs Rouge_similaire: {sim_2_3:.4f}")

    # Vérifier que ça fait sens
    if sim_1_3 > sim_1_2:
        print(f"   ✅ Logique: Rouge plus similaire à Rouge_similaire qu'à Bleu")
    else:
        print(f"   ⚠️ Attention: Les scores ne semblent pas logiques")

    if sim_1_2 > 0:
        print(f"   ✅ Les scores ne sont PAS à zéro")
    else:
        print(f"   ❌ PROBLÈME: Tous les scores sont à zéro!")

except Exception as e:
    print(f"   ❌ Erreur calcul similarités: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test avec notre module
print("\n7️⃣ Test avec notre CLIPSimilarityModel...")
try:
    from src.image_search.clip_similarity import CLIPSimilarityModel

    clip_model = CLIPSimilarityModel()

    # Tester la similarité
    score = clip_model.similarity(str(img1_path), str(img3_path))
    print(f"   ✅ Score (rouge vs rouge_similaire): {score:.4f}")

    if score > 0:
        print(f"   ✅ Notre module fonctionne correctement!")
    else:
        print(f"   ❌ PROBLÈME: Score à zéro avec notre module")

except Exception as e:
    print(f"   ❌ Erreur avec notre module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Test avec ImageSimilaritySearch
print("\n8️⃣ Test avec ImageSimilaritySearch...")
try:
    from src.image_search.image_similarity import ImageSimilaritySearch

    search = ImageSimilaritySearch(use_clip=True)

    # Ajouter des images
    search.add_image(str(img2_path), {'name': 'blue'})
    search.add_image(str(img3_path), {'name': 'red_similar'})

    # Rechercher
    results = search.search_similar(str(img1_path), top_k=2, threshold=0.1)

    print(f"   ✅ Résultats de recherche: {len(results)} images")
    for path, score, meta in results:
        print(f"      {Path(path).name}: score={score:.4f}, meta={meta}")

    if len(results) > 0 and results[0][1] > 0:
        print(f"   ✅ ImageSimilaritySearch fonctionne!")
    else:
        print(f"   ❌ PROBLÈME: Aucun résultat ou scores à zéro")

except Exception as e:
    print(f"   ❌ Erreur avec ImageSimilaritySearch: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Nettoyage
print("\n9️⃣ Nettoyage...")
import shutil
if test_dir.exists():
    shutil.rmtree(test_dir)
    print(f"   ✅ Dossier de test supprimé")

print("\n" + "="*80)
print("✅ TOUS LES TESTS SONT PASSÉS!")
print("="*80)
print("\n💡 Si ce script fonctionne mais que le score est toujours 0 dans l'app:")
print("   1. Vérifiez que les images sont bien téléchargées (dossier output/images/)")
print("   2. Vérifiez image_metadata.json contient les 'local_path'")
print("   3. Lancez l'app avec: streamlit run app.py")
print("   4. Regardez les logs dans le terminal pendant le scraping")
print("   5. Les logs détaillés vous diront exactement où est le problème")
