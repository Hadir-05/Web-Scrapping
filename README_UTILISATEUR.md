# 📦 AliExpress Scraper - Guide d'Utilisation

## 🚀 Installation et Lancement

### Installation

1. **Décompressez** le fichier ZIP que vous avez reçu
2. Vous aurez un dossier `AliExpress_Scraper` contenant:
   ```
   AliExpress_Scraper/
   ├── AliExpress_Scraper.exe  ← Double-cliquez sur ce fichier
   ├── _internal/              ← Dossier de dépendances (ne pas toucher)
   └── ...
   ```

### Lancement

1. **Double-cliquez** sur `AliExpress_Scraper.exe`
2. Une fenêtre de terminal s'ouvrira (NE LA FERMEZ PAS)
3. Attendez 10-30 secondes
4. Votre navigateur s'ouvrira automatiquement avec l'application

⚠️ **IMPORTANT:** Ne fermez JAMAIS la fenêtre terminal (noire) pendant l'utilisation!

---

## 📖 Utilisation de l'Application

### 1️⃣ Upload d'Image

1. Cliquez sur **"Browse files"**
2. Sélectionnez une image de produit (JPG, PNG, etc.)
3. L'image s'affichera à gauche

### 2️⃣ Configuration de la Recherche

**Dans la barre latérale (gauche):**
- **Nombre max de produits:** Combien de produits similaires chercher (10-200)
- Le prochain dossier de résultats s'affichera (ex: `output_recherche1`)

### 3️⃣ Lancer la Recherche

1. Cliquez sur **"🔍 Rechercher sur AliExpress"**
2. Attendez 2-10 minutes selon le nombre de produits
3. Un message de succès s'affichera quand c'est terminé

### 4️⃣ Voir les Résultats

**3 onglets disponibles:**

**📊 Onglet 1 - Recherche par Image:**
- Les 6 meilleurs produits similaires
- Score de similarité CLIP

**📋 Onglet 2 - Résultats Détaillés:**
- Tous les produits trouvés avec images
- Cliquez pour voir les détails complets

**📁 Onglet 3 - Export:**
- Sélectionnez les produits à exporter
- Boutons "Tout sélectionner" / "Tout désélectionner"
- Générez un fichier Excel avec les produits sélectionnés

---

## 📁 Où Sont les Résultats?

Les résultats sont sauvegardés dans des dossiers numérotés:

```
📂 Dossier de l'application/
├── output_recherche1/
│   ├── product_data.json        ← Données des produits
│   ├── image_metadata.json      ← Métadonnées des images
│   └── images/
│       ├── product_001/         ← Images du produit 1
│       │   ├── image_1.jpg
│       │   ├── image_2.jpg
│       │   └── image_3.jpg
│       ├── product_002/
│       └── ...
│
├── output_recherche2/           ← Deuxième recherche
└── ...
```

**Chaque recherche crée un nouveau dossier automatiquement!**

---

## ❓ Problèmes Courants

### L'application ne démarre pas

**Solutions:**
1. Assurez-vous que votre antivirus ne bloque pas l'exe
2. Essayez de lancer en tant qu'administrateur (clic droit → "Exécuter en tant qu'administrateur")
3. Vérifiez qu'il y a au moins 2GB d'espace disque disponible
4. Redémarrez votre ordinateur

### Le navigateur ne s'ouvre pas

1. Attendez 30 secondes supplémentaires
2. Ouvrez manuellement votre navigateur et allez sur: `http://localhost:8501`
3. Si ça ne marche toujours pas, fermez tout et relancez l'exe

### "Port already in use" (Port déjà utilisé)

1. Fermez toutes les instances de l'application
2. Redémarrez votre ordinateur
3. Relancez l'application

### La recherche est très lente

C'est normal! La recherche peut prendre:
- **2-5 minutes** pour 10 produits
- **5-10 minutes** pour 50 produits
- **10-20 minutes** pour 200 produits

**Patience!** Le navigateur affichera la progression.

### Les images ne s'affichent pas

1. Vérifiez votre connexion internet (les images peuvent venir d'internet)
2. Attendez que le téléchargement des images se termine
3. Les images avec 🌐 viennent d'internet (pas encore téléchargées localement)

---

## 💡 Conseils d'Utilisation

### Pour de Meilleurs Résultats

1. **Utilisez des images claires:**
   - Produit bien visible
   - Fond uni si possible
   - Bonne résolution (pas de photos floues)

2. **Commencez petit:**
   - Testez avec 10 produits d'abord
   - Augmentez si les résultats sont bons

3. **Vérifiez les scores:**
   - Score > 80% = Très similaire
   - Score 60-80% = Similaire
   - Score < 60% = Peu similaire

### Export Excel

1. Sélectionnez les produits pertinents
2. Remplissez le mot-clé et la catégorie
3. Cliquez "Générer fichier Excel"
4. Le fichier se téléchargera automatiquement

---

## 🔒 Confidentialité et Sécurité

- ✅ Toutes les données restent sur votre ordinateur
- ✅ Aucune donnée n'est envoyée ailleurs qu'à AliExpress
- ✅ Les résultats sont sauvegardés localement

---

## 📞 Support

**En cas de problème:**

1. Vérifiez d'abord la section "Problèmes Courants" ci-dessus
2. Redémarrez l'application
3. Redémarrez votre ordinateur
4. Si le problème persiste, contactez le support avec:
   - Une capture d'écran de l'erreur
   - La description du problème
   - Les étapes pour reproduire le problème

---

## 📝 Notes de Version

**Version 1.0**
- Recherche par image sur AliExpress
- Calcul de similarité avec CLIP
- Export Excel des résultats
- Historique automatique des recherches

---

**Bon scraping! 🚀**
