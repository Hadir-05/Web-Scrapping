# Instructions Git - Projet AliExpress Scraper

## 🔄 Configuration Initiale

### 1. Cloner le Projet (Première Fois)
```bash
git clone <URL_DU_REPO>
cd Web-Scrapping
```

### 2. Vérifier la Configuration Git
```bash
git config user.name
git config user.email

# Si besoin, configurer:
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"
```

---

## 📥 Synchroniser avec le Repo Distant (Pull)

### Récupérer les Dernières Modifications
```bash
# Vérifier votre branche actuelle
git branch

# Récupérer les modifications de la branche principale
git pull origin main

# OU récupérer les modifications de VOTRE branche de travail
git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

### Synchronisation Complète (Fetch + Merge)
```bash
# Récupérer toutes les branches distantes
git fetch origin

# Voir toutes les branches (locales et distantes)
git branch -a

# Fusionner les changements d'une branche spécifique
git merge origin/claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

---

## 📤 Envoyer vos Modifications (Push)

### Workflow Complet de Commit + Push

#### Étape 1 : Vérifier l'état des fichiers
```bash
git status
```

#### Étape 2 : Voir les modifications détaillées
```bash
# Voir les modifications non-staged
git diff

# Voir les modifications staged
git diff --staged
```

#### Étape 3 : Ajouter les fichiers modifiés
```bash
# Ajouter tous les fichiers modifiés
git add .

# OU ajouter des fichiers spécifiques
git add app.py src/aliexpress_scraper.py

# OU ajouter par type
git add *.py *.md
```

#### Étape 4 : Créer un commit
```bash
git commit -m "Description courte de vos modifications

Détails supplémentaires si nécessaire:
- Changement 1
- Changement 2
- Changement 3
"
```

#### Étape 5 : Pousser vers le repo distant
```bash
# Push vers votre branche de travail actuelle
git push -u origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# OU si la branche est déjà trackée
git push
```

---

## 🌿 Gestion des Branches

### Voir les Branches
```bash
# Branches locales
git branch

# Toutes les branches (locales + distantes)
git branch -a

# Branches distantes uniquement
git branch -r
```

### Changer de Branche
```bash
# Aller sur la branche principale
git checkout main

# Aller sur votre branche de travail
git checkout claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# Créer et aller sur une nouvelle branche
git checkout -b nouvelle-branche
```

### Mettre à Jour une Branche depuis main
```bash
# Aller sur votre branche
git checkout claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# Récupérer les dernières modifications de main
git pull origin main

# Résoudre les conflits si nécessaire, puis:
git add .
git commit -m "Merge main into working branch"
git push
```

---

## 🔍 Commandes Utiles de Vérification

### Historique des Commits
```bash
# Voir l'historique complet
git log

# Historique compact (1 ligne par commit)
git log --oneline

# Voir les 10 derniers commits
git log -10 --oneline

# Historique avec graphique
git log --graph --oneline --all
```

### Voir les Fichiers Modifiés dans un Commit
```bash
# Voir les fichiers du dernier commit
git show --name-only

# Voir les détails d'un commit spécifique
git show <commit-hash>

# Exemple:
git show 19410e6
```

### Comparer les Branches
```bash
# Voir les différences entre votre branche et main
git diff main..claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# Voir les commits qui sont dans votre branche mais pas dans main
git log main..claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

---

## 🆘 Résolution de Problèmes

### Annuler des Modifications Non-Commitées
```bash
# Annuler les modifications d'un fichier spécifique
git checkout -- app.py

# Annuler TOUTES les modifications non-staged
git checkout -- .

# Retirer un fichier du staging (après git add)
git reset HEAD app.py
```

### Annuler le Dernier Commit (AVANT push)
```bash
# Garder les modifications dans les fichiers
git reset --soft HEAD~1

# Annuler commit ET modifications
git reset --hard HEAD~1
```

### Récupérer après un Push Raté
```bash
# Si le push échoue, vérifier d'abord l'état
git status

# Récupérer les modifications distantes d'abord
git pull --rebase origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# Puis re-pousser
git push -u origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

### Forcer un Push (⚠️ ATTENTION)
```bash
# À utiliser UNIQUEMENT si vous êtes sûr
git push --force origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

---

## 📋 Workflow Quotidien Recommandé

### Début de Journée
```bash
# 1. Vérifier votre branche
git branch

# 2. Récupérer les dernières modifications
git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# 3. Voir l'état du projet
git status
```

### Pendant le Développement
```bash
# Sauvegarder régulièrement (toutes les 30-60 min)
git add .
git commit -m "Description du travail effectué"

# Pousser à la fin de chaque session de travail
git push
```

### Fin de Journée
```bash
# 1. Vérifier qu'il n'y a rien d'oublié
git status

# 2. Commit final
git add .
git commit -m "Travail du jour: [résumé]"

# 3. Push final
git push -u origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

---

## 🎯 Commandes Spécifiques pour ce Projet

### Récupérer Tous les Fichiers Docker
```bash
git pull origin claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz

# Vérifier que les fichiers Docker sont présents
ls -la | grep -E "(Dockerfile|docker-compose|\.docker)"
```

### Voir l'Historique des Déploiements
```bash
# Voir tous les commits liés au déploiement
git log --oneline --grep="deploy\|PyInstaller\|Docker"

# Voir les fichiers de déploiement créés
git log --oneline --name-only | grep -E "(Dockerfile|build_|README_|GUIDE_)"
```

### Retourner à un État Spécifique
```bash
# Voir l'historique
git log --oneline

# Créer une nouvelle branche à partir d'un commit spécifique
git checkout -b branche-test <commit-hash>

# Exemple pour revenir au commit du Docker:
git checkout -b test-docker 19410e6
```

---

## 📊 État Actuel du Projet

### Branche de Travail
```
claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz
```

### Derniers Commits
```
19410e6 - Add complete Docker containerization system for local deployment
b16bc04 - Add comprehensive final summary of entire project
aab379f - Add complete PyInstaller build system for executable distribution
93f6d7b - Add comprehensive deployment and security guide
```

### Fichiers Importants Créés
- **Déploiement**: `DEPLOIEMENT_SECURISATION.md`
- **PyInstaller**: `build_executable.py`, `AliExpress_Scraper.spec`, `README_UTILISATEUR.md`, `GUIDE_COMPILATION.md`
- **Docker**: `Dockerfile`, `docker-compose.yml`, `build_docker.sh`, `save_docker.sh`, `run_docker.sh`, `README_DOCKER.md`, `GUIDE_DOCKER.md`
- **Documentation**: `CHANGEMENTS_RESUME.md`, `RESUME_FINAL.md`

---

## ✅ Checklist Avant Chaque Push

- [ ] `git status` - Vérifier les fichiers modifiés
- [ ] `git diff` - Vérifier les modifications
- [ ] `git add .` - Ajouter les fichiers
- [ ] `git commit -m "message"` - Créer un commit descriptif
- [ ] `git pull origin <branche>` - Récupérer les modifications distantes
- [ ] `git push -u origin <branche>` - Pousser vos modifications

---

## 🔗 Ressources Utiles

### Aide Git
```bash
# Aide générale
git --help

# Aide sur une commande spécifique
git pull --help
git push --help
git commit --help
```

### Configuration Avancée
```bash
# Voir toute la configuration
git config --list

# Sauvegarder les credentials (éviter de retaper le mot de passe)
git config credential.helper store

# Définir l'éditeur par défaut
git config --global core.editor "nano"
```

---

## 📞 Support

En cas de problème avec Git:
1. Vérifier `git status`
2. Lire le message d'erreur complet
3. Essayer `git pull` avant de `push`
4. Consulter ce guide pour la commande appropriée
5. En dernier recours: créer une nouvelle branche et recommencer

**⚠️ IMPORTANT**: Ne JAMAIS utiliser `git push --force` sans comprendre les conséquences!

---

**Date de création**: 2025-11-06
**Projet**: AliExpress Scraper avec Streamlit + Crawlee
**Branche principale**: `claude/rebuild-repo-from-scratch-011CUnfUeYm5HTQ3ToQ9tZZz`
