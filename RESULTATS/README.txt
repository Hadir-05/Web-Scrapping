=====================================================
   DOSSIER DES RESULTATS - WEB SCRAPING ALIEXPRESS
=====================================================

Ce dossier contient tous les résultats de vos recherches.

STRUCTURE DES DOSSIERS
----------------------

Chaque recherche crée un nouveau dossier avec la date et l'heure :
  RESULTATS/
  ├── recherche_2025-11-10_14-30-25/
  ├── recherche_2025-11-10_15-45-12/
  └── ...

CONTENU DE CHAQUE DOSSIER DE RECHERCHE
---------------------------------------

Chaque dossier contient :

1. product_data.json
   → Liste complète des produits trouvés avec leurs détails
   → Contient : titre, prix, URL, description, images, date

2. image_metadata.json
   → Métadonnées de toutes les images téléchargées
   → Mapping entre URLs en ligne et chemins locaux

3. images/
   → Dossier contenant toutes les images des produits
   → Images téléchargées depuis AliExpress

4. aliexpress_products_XXXXXXX.xlsx (si exporté)
   → Fichier Excel avec les produits sélectionnés
   → Colonnes : Date, URL, Catégorie, Nom, Mot-clé, Prix, Score

COMMENT UTILISER LES RESULTATS
-------------------------------

1. CONSULTER LES PRODUITS
   - Ouvrez l'application web (lancez app.py)
   - Les résultats sont affichés automatiquement
   - Vous pouvez voir les images et détails de chaque produit

2. EXPORTER EN EXCEL
   - Allez dans l'onglet "Export"
   - Sélectionnez les produits qui vous intéressent
   - Cliquez sur "Générer fichier Excel"
   - Le fichier sera téléchargé dans ce dossier

3. CONSULTER LES FICHIERS JSON
   - Utilisez un éditeur de texte ou JSON viewer
   - product_data.json : informations complètes
   - image_metadata.json : correspondance images

NOTES IMPORTANTES
-----------------

- Chaque recherche est indépendante et conservée
- Les images sont téléchargées localement pour éviter la perte de données
- Les scores CLIP indiquent la similarité avec votre image de recherche
  (plus le score est élevé, plus le produit est similaire)

BESOIN D'AIDE ?
---------------

Si vous avez des questions ou problèmes :
1. Consultez le fichier README_CLIENT.txt à la racine
2. Vérifiez que tous les fichiers sont présents
3. Contactez le support technique

Date de création : 2025-11-10
Version : 1.0
