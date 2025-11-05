# Guide de Dépannage - Web Scrapping AliExpress

## 🔍 Problème: Score CLIP = 0%

Si vous voyez des scores de similarité à 0% dans l'application, suivez ces étapes de diagnostic:

### Étape 1: Vérifier l'installation de CLIP

```bash
python test_clip.py
```

**Ce que ce script fait:**
- ✅ Vérifie que `open-clip-torch` est installé
- ✅ Vérifie que PyTorch fonctionne
- ✅ Charge le modèle CLIP ViT-L-14
- ✅ Crée des images de test
- ✅ Calcule des embeddings
- ✅ Teste la similarité avec des couleurs simples
- ✅ Teste vos modules `CLIPSimilarityModel` et `ImageSimilaritySearch`

**Si ce test échoue:**
```bash
# Réinstallez les dépendances
pip install --upgrade open-clip-torch torch torchvision
```

### Étape 2: Inspecter le dossier output

```bash
python inspect_output.py
```

**Ce que ce script vérifie:**
- 📦 Existence de `product_data.json`
- 🖼️ Existence de `image_metadata.json`
- 🔍 Présence du champ `local_path` dans les métadonnées
- 📁 Organisation des images dans `output/images/product_XXX/`
- ✅ Correspondance entre les chemins et les fichiers réels

**Problèmes courants détectés:**

| Problème | Cause | Solution |
|----------|-------|----------|
| `local_path` manquant | Ancienne version du scraper | Relancez un scraping avec la nouvelle version |
| Images manquantes | Téléchargement échoué | Vérifiez les logs du scraper, problème de connexion? |
| Dossier images/ vide | Scraping incomplet | Relancez le scraping, vérifiez la connexion AliExpress |

### Étape 3: Lancer un scraping avec logs détaillés

```bash
streamlit run app.py
```

**Puis dans le terminal, observez:**

```
================================================================================
=== CALCUL DE SIMILARITÉ AVEC DEBUG COMPLET ===
================================================================================
📸 Image uploadée: /tmp/streamlit/xxxxx.jpg
   Existe? True
   Taille: (224, 224), Mode: RGB
📦 Nombre de produits: 10

📂 Chargement du mapping d'images depuis: output/image_metadata.json
   Total métadonnées: 30
   Exemple 1: https://ae01.alicdn.com/kf/xxx.jpg → output/images/product_001/image_1.jpg
   ✅ 30 mappings URL→local chargés

🤖 Initialisation ImageSimilaritySearch (use_clip=True)...
   Use CLIP: True

📥 Ajout des images à l'index CLIP...

   Produit 1/10: Women's Leather Handbag...
   URLs d'images: 3
      Image 1: URL=https://ae01.alicdn.com/kf/xxx.jpg...
                 Local=output/images/product_001/image_1.jpg
                 Existe? True
      ✅ Ajout à l'index CLIP...
🔧 Chargement du modèle CLIP: ViT-L-14 (laion2b_s32b_b82k)
   Device: cpu
      [CLIP] Computing features for: output/images/product_001/image_1.jpg
      [CLIP] Image size: (800, 800)
      [CLIP] Feature shape: (1, 768)
      ✅ Ajoutée avec succès (total: 1)
...

📊 Résumé ajout d'images:
   ✅ Images ajoutées: 30
   ❌ Images manquantes: 0

📈 Statistiques de l'index:
   total_images: 30
   total_metadata: 30
   using_clip: True

🔍 Recherche de similarité avec l'image uploadée...
  [ImageSearch] Computing query embedding...
  [ImageSearch] Query embedding shape: (1, 768)
  [ImageSearch] Comparing with 30 images
    [ImageSearch] output/images/product_001/image_1.jpg: score=0.8234
    [ImageSearch] output/images/product_001/image_2.jpg: score=0.7891
...

✨ Images similaires trouvées: 25

   #1: Score=0.8234 - https://ae01.alicdn.com/kf/xxx.jpg...
   #2: Score=0.7891 - https://ae01.alicdn.com/kf/yyy.jpg...

📊 Résumé final:
   Total scores calculés: 25
   Scores > 0.5: 18
   Scores > 0.3: 22
   Scores > 0.1: 25
================================================================================
```

**Interprétation des logs:**

✅ **Tout fonctionne si vous voyez:**
- `Use CLIP: True`
- `🔧 Chargement du modèle CLIP...` (une seule fois)
- `✅ Ajoutée avec succès` pour chaque image
- `Images ajoutées: > 0`
- `Scores > 0.5: > 0` (au moins quelques scores élevés)

❌ **Problème si vous voyez:**
- `Use CLIP: False` → CLIP non disponible
- `❌ Images manquantes: X` où X > 0 → Les fichiers n'existent pas
- `Images ajoutées: 0` → Aucune image indexée
- `Total scores calculés: 0` → Aucune similarité trouvée
- Tous les scores = 0.0000 → Problème avec CLIP

### Étape 4: Cas spécifiques

#### Cas A: "Use CLIP: False"

**Cause:** CLIP n'est pas installé ou ne peut pas être importé

**Solution:**
```bash
pip install --upgrade open-clip-torch
pip install --upgrade torch torchvision
python -c "import open_clip; print('CLIP OK')"
```

#### Cas B: "Images manquantes: 30"

**Cause:** Les chemins dans `image_metadata.json` ne correspondent pas aux fichiers réels

**Vérification:**
```bash
python inspect_output.py
ls -la output/images/
```

**Solution:**
- Supprimez le dossier `output/`
- Relancez un scraping complet

#### Cas C: "Scores calculés: 0"

**Cause:** Seuil trop élevé ou aucune image dans l'index

**Solution:**
- Vérifiez `Images ajoutées: X` doit être > 0
- Le seuil est déjà à 0.1 (10%)
- Si toujours 0, lancez `python test_clip.py` pour vérifier CLIP

#### Cas D: Tous les scores = 0.XXXX (très faible)

**Cause:** Possible mais rare - images vraiment très différentes

**Vérification:**
- Les produits trouvés sont-ils pertinents?
- L'image uploadée est-elle de bonne qualité?
- Essayez avec une image de produit AliExpress directement

## 🚀 Autres Problèmes

### Prix non affiché (N/A)

**Cause:** Sélecteurs CSS ne correspondent pas à la structure AliExpress actuelle

**Solution à venir:** Le scraper essaie déjà 8 sélecteurs différents. Si aucun ne fonctionne:
1. Ouvrez manuellement une page produit AliExpress
2. Inspectez l'élément du prix (F12 → Inspect)
3. Trouvez la classe CSS exacte
4. Ajoutez-la dans `src/scraper/aliexpress_scraper.py` ligne 292

### "Tout sélectionner" ne coche pas visuellement

**Déjà corrigé** dans la dernière version. Si le problème persiste:
```bash
git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

### Images non organisées par produit

**Déjà corrigé** dans la dernière version. Les images sont maintenant dans:
```
output/images/
  product_001/
    image_1.jpg
    image_2.jpg
    image_3.jpg
  product_002/
    image_1.jpg
    image_2.jpg
    image_3.jpg
```

Si vous voyez encore l'ancien format (`image_0001.jpg` à plat):
1. Supprimez le dossier `output/`
2. Assurez-vous d'avoir la dernière version du code
3. Relancez un scraping

## 📞 Support

Si aucune de ces solutions ne fonctionne:

1. **Lancez tous les scripts de diagnostic:**
   ```bash
   python test_clip.py > test_clip_output.txt 2>&1
   python inspect_output.py > inspect_output.txt 2>&1
   ```

2. **Capturez les logs de l'application:**
   ```bash
   streamlit run app.py > app_logs.txt 2>&1
   ```

3. **Partagez ces 3 fichiers** avec les informations sur votre problème

## ✅ Checklist de vérification

Avant de signaler un bug, vérifiez:

- [ ] Python 3.8+ installé
- [ ] Toutes les dépendances installées: `pip install -r requirements.txt`
- [ ] `python test_clip.py` passe tous les tests
- [ ] `python inspect_output.py` ne montre aucun problème critique
- [ ] Le dossier `output/images/` contient des sous-dossiers `product_XXX/`
- [ ] Le fichier `output/image_metadata.json` contient le champ `local_path`
- [ ] Les logs de l'app montrent "Use CLIP: True"
- [ ] Les logs montrent "Images ajoutées: > 0"
