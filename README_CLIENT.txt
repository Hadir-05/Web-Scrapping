================================================================================
                        ALIEXPRESS SCRAPER
                     Application de Recherche de Produits
================================================================================

VERSION : 1.0.0
DATE    : Novembre 2025

================================================================================
                            INSTALLATION
================================================================================

1. EXTRAIRE LES FICHIERS
   ----------------------
   - Clic droit sur le fichier .zip
   - Sélectionner "Extraire tout..."
   - Choisir un emplacement (ex: Bureau, Documents)
   - Cliquer sur "Extraire"

2. OUVRIR LE DOSSIER
   ------------------
   - Aller dans le dossier extrait
   - Vous devriez voir :
     * AliExpress_Scraper.exe  (l'application)
     * _internal/              (dossier de librairies)
     * app.py                  (fichier de configuration)
     * src/                    (dossier source)
     * README.txt              (ce fichier)

3. LANCER L'APPLICATION
   --------------------
   - Double-cliquer sur AliExpress_Scraper.exe
   - Attendre 5-10 secondes
   - Une fenêtre s'ouvre avec l'interface


⚠️  IMPORTANT : Tous les fichiers du dossier sont nécessaires !
    Ne déplacez PAS uniquement le fichier .exe


================================================================================
                          PREMIÈRE UTILISATION
================================================================================

SI WINDOWS DEFENDER BLOQUE L'APPLICATION :
------------------------------------------

Windows peut afficher : "Windows a protégé votre ordinateur"

C'est NORMAL pour les nouvelles applications.

SOLUTION :
1. Cliquer sur "Informations complémentaires"
2. Cliquer sur "Exécuter quand même"

L'application va démarrer et ne demandera plus l'autorisation.


DÉMARRAGE DE L'APPLICATION :
----------------------------

Quand vous double-cliquez sur l'exe, vous verrez :

1. Une fenêtre console brièvement (normal)
2. Puis une fenêtre avec l'interface graphique
3. L'application est prête à être utilisée !


================================================================================
                              UTILISATION
================================================================================

L'APPLICATION SE COMPOSE DE 3 ONGLETS :
---------------------------------------

1. RECHERCHE
   ---------
   - Entrer l'URL de recherche AliExpress
   - Choisir une image de référence :
     * Upload depuis votre ordinateur
     * OU copier l'URL d'une image en ligne
   - Ajuster le nombre de résultats souhaités
   - Cliquer sur "Lancer la recherche"
   - Attendre que les résultats s'affichent

2. RÉSULTATS DÉTAILLÉS
   -------------------
   - Voir tous les produits trouvés
   - Chaque produit affiche :
     * Image
     * Titre
     * Prix
     * Score de similarité
     * Lien vers AliExpress

3. EXPORTER
   --------
   - Télécharger les résultats en format :
     * Excel (.xlsx) avec produits sélectionnés
     * JSON (données brutes dans le dossier de recherche)
   - Les fichiers sont sauvegardés automatiquement

📁 DOSSIER DES RESULTATS :
-------------------------

Tous les résultats sont sauvegardés dans le dossier :
   RESULTATS/

Chaque recherche crée un nouveau dossier avec la date :
   RESULTATS/recherche_2025-11-10_14-30-25/

Dans chaque dossier vous trouverez :
   ✓ product_data.json     - Données des produits
   ✓ image_metadata.json   - Informations sur les images
   ✓ images/               - Toutes les images téléchargées
   ✓ *.xlsx (si exporté)   - Fichier Excel avec produits sélectionnés

Consultez RESULTATS/README.txt pour plus de détails.


CONSEILS D'UTILISATION :
------------------------

✓ Utilisez des images de bonne qualité (au moins 500x500 pixels)
✓ Les recherches peuvent prendre 1-3 minutes selon le nombre de résultats
✓ Ne fermez pas la fenêtre pendant une recherche en cours
✓ Les résultats sont triés par similarité (meilleur en premier)
✓ Tous vos résultats sont sauvegardés dans le dossier RESULTATS/


================================================================================
                         RÉSOLUTION DE PROBLÈMES
================================================================================

PROBLÈME : L'application ne démarre pas
SOLUTION :
  1. Vérifier que TOUS les fichiers sont extraits
  2. Vérifier que l'antivirus n'a pas bloqué l'application
  3. Essayer de désactiver temporairement l'antivirus
  4. Contacter le support technique

PROBLÈME : "Le port 8501 est déjà utilisé"
SOLUTION :
  1. Fermer toutes les fenêtres de l'application
  2. Ouvrir le Gestionnaire des tâches (Ctrl+Shift+Echap)
  3. Chercher "AliExpress_Scraper" et terminer le processus
  4. Relancer l'application

PROBLÈME : La recherche ne retourne aucun résultat
SOLUTION :
  1. Vérifier que l'URL AliExpress est correcte
  2. Vérifier que l'image de référence est valide
  3. Essayer avec moins de résultats (10-20)
  4. Vérifier votre connexion Internet

PROBLÈME : Les images ne s'affichent pas
SOLUTION :
  1. Vérifier votre connexion Internet
  2. Les images sont téléchargées depuis AliExpress
  3. Certaines images peuvent ne pas être disponibles
  4. Essayer de relancer la recherche


================================================================================
                          CONFIGURATION REQUISE
================================================================================

SYSTÈME D'EXPLOITATION :
  - Windows 10 ou supérieur (64 bits)
  - Windows 11 (recommandé)

MATÉRIEL :
  - Processeur : 2 GHz ou plus
  - RAM : 4 GB minimum (8 GB recommandé)
  - Espace disque : 3 GB libre
  - Connexion Internet : Requise

LOGICIELS :
  - Aucun logiciel supplémentaire requis
  - Tout est inclus dans l'application


================================================================================
                              SUPPORT
================================================================================

En cas de problème ou de question :

📧 Email   : [votre-email@example.com]
📞 Téléphone : [votre-numéro]
🌐 Site web : [votre-site-web]

Heures de support :
  Lundi - Vendredi : 9h00 - 18h00
  Samedi : 9h00 - 12h00
  Dimanche : Fermé


INFORMATIONS À FOURNIR EN CAS DE PROBLÈME :
-------------------------------------------
  - Version de Windows (Win + Pause)
  - Message d'erreur exact (capture d'écran)
  - Étapes pour reproduire le problème


================================================================================
                          INFORMATIONS LÉGALES
================================================================================

LICENCE :
  Cette application est fournie sous licence commerciale.
  Toute reproduction, distribution ou modification non autorisée
  est strictement interdite.

GARANTIE :
  L'application est fournie "telle quelle" sans garantie d'aucune sorte.
  L'éditeur ne peut être tenu responsable des dommages résultant
  de l'utilisation de cette application.

DONNÉES :
  Cette application ne collecte aucune donnée personnelle.
  Les recherches sont effectuées directement sur AliExpress.
  Aucune information n'est envoyée à des serveurs tiers.


================================================================================
                            NOTES DE VERSION
================================================================================

VERSION 1.0.0 (Novembre 2025)
  - Première version
  - Recherche de produits sur AliExpress
  - Similarité d'images avec IA
  - Export CSV et JSON
  - Interface graphique intuitive


================================================================================

              MERCI D'UTILISER ALIEXPRESS SCRAPER !

                    Bonne recherche de produits !

================================================================================
