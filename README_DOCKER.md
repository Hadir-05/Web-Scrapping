# 🐳 AliExpress Scraper - Guide Docker

## 📦 Installation et Utilisation avec Docker

---

## 🎯 Qu'est-ce que Docker?

Docker est une plateforme qui permet d'exécuter des applications dans des conteneurs isolés.
**Avantage pour vous:** Aucune installation compliquée! Juste Docker et vous êtes prêt.

---

## 📥 Installation de Docker

### Windows & Mac

1. Téléchargez **Docker Desktop:**
   - https://www.docker.com/products/docker-desktop

2. Installez Docker Desktop (suivez l'assistant d'installation)

3. Lancez Docker Desktop

4. Attendez que Docker démarre (l'icône Docker dans la barre des tâches devient verte)

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Démarrer Docker
sudo systemctl start docker
sudo systemctl enable docker

# Ajouter votre utilisateur au groupe docker (pour éviter sudo)
sudo usermod -aG docker $USER
# Redémarrez votre session après cette commande
```

---

## 🚀 Lancement de l'Application

### Méthode Rapide (Recommandée)

1. **Décompressez** les fichiers que vous avez reçus

2. **Ouvrez un terminal** dans le dossier décompressé
   - Windows: Clic droit → "Ouvrir dans le terminal" ou "Git Bash Here"
   - Mac: Applications → Utilitaires → Terminal, puis `cd` vers le dossier
   - Linux: Clic droit → "Ouvrir dans le terminal"

3. **Lancez le script:**
   ```bash
   # Windows (Git Bash ou WSL)
   ./run_docker.sh

   # Ou sur Windows PowerShell:
   bash run_docker.sh

   # Mac/Linux
   ./run_docker.sh
   ```

4. **Attendez** 10-30 secondes

5. **Ouvrez votre navigateur** sur: http://localhost:8501

**C'est tout!** 🎉

---

## 📂 Où Sont Mes Résultats?

Les résultats sont sauvegardés dans le **même dossier** où vous avez lancé l'application:

```
votre-dossier/
├── run_docker.sh
├── output_recherche1/     ← Résultats recherche 1
│   ├── product_data.json
│   ├── image_metadata.json
│   └── images/
│       ├── product_001/
│       └── ...
│
├── output_recherche2/     ← Résultats recherche 2
└── ...
```

**Les fichiers restent sur VOTRE ordinateur**, même quand vous arrêtez Docker!

---

## 🎮 Commandes Utiles

### Voir si l'Application Tourne

```bash
docker ps
```

Vous devriez voir `aliexpress_scraper` dans la liste.

### Voir les Logs (Debug)

```bash
docker logs -f aliexpress_scraper
```

Appuyez sur `Ctrl+C` pour quitter les logs.

### Arrêter l'Application

```bash
docker stop aliexpress_scraper
```

### Redémarrer l'Application

```bash
docker restart aliexpress_scraper
```

### Relancer Complètement

```bash
# Arrêter et supprimer
docker stop aliexpress_scraper
docker rm aliexpress_scraper

# Relancer
./run_docker.sh
```

---

## 📖 Utilisation de l'Application

### 1. Accéder à l'Application

Ouvrez votre navigateur sur: **http://localhost:8501**

### 2. Upload d'Image

1. Cliquez sur "Browse files"
2. Sélectionnez une image de produit
3. L'image s'affiche à gauche

### 3. Configuration

**Dans la barre latérale:**
- Nombre de produits: 10-200 (commencez avec 10 pour tester)
- Le dossier de résultats s'affichera (ex: `output_recherche1`)

### 4. Lancer la Recherche

1. Cliquez sur "🔍 Rechercher sur AliExpress"
2. Attendez 2-10 minutes
3. Les résultats s'afficheront

### 5. Voir les Résultats

**3 onglets:**
- **Recherche:** Top 6 produits similaires
- **Résultats Détaillés:** Tous les produits avec images
- **Export:** Sélection + export Excel

---

## ❓ Problèmes Courants

### Le Script run_docker.sh Ne Lance Pas

**Windows:**
```powershell
# Si vous n'avez pas Git Bash, utilisez:
docker run -d --name aliexpress_scraper -p 8501:8501 aliexpress-scraper:latest

# Puis ouvrez: http://localhost:8501
```

### "Port 8501 Already in Use"

```bash
# Arrêter l'ancien container
docker stop aliexpress_scraper
docker rm aliexpress_scraper

# Relancer
./run_docker.sh
```

### "Cannot Connect to Docker Daemon"

**Solution:**
1. Assurez-vous que Docker Desktop est lancé (Windows/Mac)
2. Ou démarrez le service Docker (Linux):
   ```bash
   sudo systemctl start docker
   ```

### Le Navigateur N'Affiche Rien

1. Attendez 30 secondes supplémentaires
2. Vérifiez les logs:
   ```bash
   docker logs aliexpress_scraper
   ```
3. Assurez-vous que le container tourne:
   ```bash
   docker ps
   ```

### L'Application Est Très Lente

C'est normal! Le scraping prend du temps:
- 10 produits: 2-5 minutes
- 50 produits: 5-10 minutes
- 200 produits: 10-20 minutes

### Images Pas Encore Téléchargées

Les images avec l'icône 🌐 viennent d'internet (pas encore téléchargées localement).
**Attendez** que le téléchargement se termine.

---

## 🔧 Paramètres Avancés

### Changer le Port

Si le port 8501 est utilisé, modifiez dans `run_docker.sh`:

```bash
# Ligne PORT=8501
PORT=8502  # Ou n'importe quel port libre
```

Puis accédez sur: http://localhost:8502

### Limiter les Ressources

```bash
docker run -d \
    --name aliexpress_scraper \
    -p 8501:8501 \
    --memory="4g" \
    --cpus="2" \
    aliexpress-scraper:latest
```

### Utiliser docker-compose (Avancé)

Si vous avez le fichier `docker-compose.yml`:

```bash
# Lancer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f
```

---

## 💾 Sauvegarde et Nettoyage

### Sauvegarder Vos Résultats

Vos résultats sont dans les dossiers `output_recherche*`.
**Copiez-les** ailleurs pour les garder avant de supprimer le container.

### Nettoyer Docker

```bash
# Arrêter et supprimer le container
docker stop aliexpress_scraper
docker rm aliexpress_scraper

# Supprimer l'image (libère ~2-3GB)
docker rmi aliexpress-scraper:latest

# Nettoyer tout Docker (ATTENTION: supprime TOUT)
docker system prune -a
```

---

## 🔒 Sécurité et Confidentialité

- ✅ Toutes les données restent sur votre ordinateur
- ✅ Aucune donnée n'est envoyée ailleurs qu'à AliExpress
- ✅ Le container est isolé de votre système
- ✅ Le code source est protégé dans l'image Docker

---

## 📞 Besoin d'Aide?

### Vérifications de Base

1. Docker Desktop est lancé?
2. Vous êtes dans le bon dossier?
3. Les fichiers `run_docker.sh` et `aliexpress-scraper-docker.tar` sont présents?
4. Vous avez attendu 30 secondes après le lancement?

### Support

Si le problème persiste:

1. Collectez ces informations:
   ```bash
   docker --version
   docker ps
   docker logs aliexpress_scraper
   ```

2. Faites une capture d'écran de l'erreur

3. Contactez le support avec ces infos

---

## 🎓 Résumé des Étapes

**Installation (une fois):**
1. Installer Docker Desktop
2. Lancer Docker Desktop

**Utilisation (à chaque fois):**
1. Ouvrir terminal dans le dossier
2. Lancer: `./run_docker.sh`
3. Ouvrir: http://localhost:8501
4. Utiliser l'application
5. Résultats dans `output_recherche*/`

**Arrêt:**
```bash
docker stop aliexpress_scraper
```

---

**Bon scraping avec Docker! 🐳🚀**
