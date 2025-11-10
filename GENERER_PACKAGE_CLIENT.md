# 📦 Guide: Générer le Package Client Protégé

## 🎯 Objectif

Créer un package avec le code **obfusqué/protégé** prêt pour distribution au client.

---

## ⚡ Méthode Rapide (Recommandée)

### 1. Installer PyArmor 7.x

```bash
# Désinstaller les anciennes versions
pip uninstall pyarmor -y

# Installer PyArmor 7.7.4 (version gratuite sans restrictions)
pip install pyarmor==7.7.4

# Vérifier l'installation
pyarmor --version
# Doit afficher: PyArmor 7.7.4
```

### 2. Exécuter le Script Automatique

```bash
# Lancer le script de build
python build_distribution_client.py
```

### 3. Résultat

Le script va :
- ✅ Obfusquer tout le code (app.py + src/)
- ✅ Copier les fichiers nécessaires
- ✅ Créer le dossier RESULTATS/ avec documentation
- ✅ Générer un ZIP prêt à distribuer

**Fichiers générés :**
- `PACKAGE_CLIENT/` → Dossier avec code protégé
- `AliExpress_Scraper_v1.0.0_YYYYMMDD.zip` → Archive prête à envoyer

---

## 📋 Contenu du Package Client

```
PACKAGE_CLIENT/
├── app.py                          ← Code obfusqué (non-lisible)
├── src/                            ← Tout le code obfusqué
│   ├── scraper/
│   ├── image_search/
│   ├── models/
│   └── ...
├── pytransform/                    ← Runtime PyArmor (ajouté automatiquement)
├── RESULTATS/                      ← Dossier pour les résultats
│   ├── README.txt                  ← Guide pour le client
│   └── .gitkeep
├── requirements.txt                ← Dépendances
├── Lancer_Application.bat          ← Lanceur Windows
├── Lancer_Application.sh           ← Lanceur Linux/Mac
├── LISEZ-MOI.txt                   ← Guide rapide
├── README_CLIENT.txt               ← Documentation complète
└── GUIDE_INSTALLATION_CLIENT.md    ← Guide d'installation

```

---

## 🧪 Tester Avant Distribution

### 1. Tester Localement

```bash
# Aller dans le dossier généré
cd PACKAGE_CLIENT

# Installer les dépendances (dans un nouvel environnement)
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate
pip install -r requirements.txt

# Lancer l'application
python app.py
```

### 2. Vérifications

- [ ] L'application démarre correctement
- [ ] L'interface web s'affiche
- [ ] Vous pouvez uploader une image
- [ ] Une recherche fonctionne
- [ ] Les résultats s'affichent
- [ ] L'export Excel fonctionne
- [ ] Les résultats sont dans RESULTATS/

### 3. Vérifier que le Code est Protégé

```bash
# Ouvrir app.py et vérifier qu'il est obfusqué
cat PACKAGE_CLIENT/app.py | head -20

# Vous devez voir du code crypté comme :
# from pytransform import pyarmor_runtime
# pyarmor_runtime()
# __pyarmor__(__name__, ...)
```

Si vous voyez du code normal/lisible → Le code n'est PAS protégé !

---

## 📧 Distribuer au Client

### Option 1 : Email Direct (si < 25 MB)

```
Objet: 📦 Livraison - AliExpress Scraper v1.0.0

Bonjour [Nom du client],

Veuillez trouver ci-joint l'application AliExpress Scraper.

📥 INSTALLATION (3 étapes):

1. Installer Python 3.10+
   → https://www.python.org/downloads/
   ⚠️ Cocher "Add Python to PATH"

2. Extraire le fichier ZIP

3. Double-cliquer sur "Lancer_Application.bat"

📖 Documentation complète dans LISEZ-MOI.txt

✅ Le code est protégé et non-modifiable
✅ Tous les résultats seront dans le dossier RESULTATS/

Support: [votre-email]

Cordialement,
[Votre Nom]
```

### Option 2 : WeTransfer / Google Drive

Si le fichier est trop gros pour email :

1. Upload sur WeTransfer/Drive/Dropbox
2. Générer un lien de partage
3. Envoyer le lien par email

### Option 3 : Clé USB

1. Copier `AliExpress_Scraper_v1.0.0_YYYYMMDD.zip` sur une clé
2. Ajouter un fichier texte avec instructions
3. Remettre en main propre

---

## 🔧 Options Avancées

### Modifier la Version

Éditer `build_distribution_client.py` :

```python
VERSION = "1.0.0"  # Changer ici
```

### Ajouter des Fichiers au Package

Éditer `build_distribution_client.py` :

```python
FILES_TO_INCLUDE = [
    "requirements.txt",
    "Lancer_Application.bat",
    # Ajouter ici vos fichiers
    "mon_fichier.txt",
]
```

### Exclure Certains Fichiers

Le script exclut automatiquement :
- `.git/`
- `__pycache__/`
- `*.pyc`
- `venv/`, `env/`
- `output_recherche*/` (anciens résultats)

---

## ❓ Problèmes Fréquents

### Problème 1: "pyarmor: command not found"

**Solution:**
```bash
pip install pyarmor==7.7.4
```

### Problème 2: "RuntimeError: unauthorized use of script"

**Cause:** Vous avez PyArmor 8.x au lieu de 7.x

**Solution:**
```bash
pip uninstall pyarmor -y
pip install pyarmor==7.7.4
```

Puis relancer le script.

### Problème 3: Le code n'est pas obfusqué

**Vérification:**
```bash
cat PACKAGE_CLIENT/app.py | head -5
```

Si vous voyez du code Python normal, l'obfuscation a échoué.

**Solution:**
- Vérifier la version de PyArmor: `pyarmor --version`
- Réinstaller PyArmor 7.7.4
- Supprimer `PACKAGE_CLIENT/` et relancer

### Problème 4: "ModuleNotFoundError: No module named 'pytransform'"

**Cause:** Le dossier `pytransform/` n'a pas été créé

**Solution:**
```bash
# Vérifier qu'il existe
ls PACKAGE_CLIENT/pytransform/

# Si absent, relancer l'obfuscation
```

---

## 📊 Checklist Finale

Avant d'envoyer au client :

- [ ] PyArmor 7.7.4 installé
- [ ] Script `build_distribution_client.py` exécuté avec succès
- [ ] ZIP créé : `AliExpress_Scraper_v1.0.0_YYYYMMDD.zip`
- [ ] Code vérifié comme obfusqué (non-lisible)
- [ ] Application testée dans `PACKAGE_CLIENT/`
- [ ] Une recherche complète testée
- [ ] Export Excel testé
- [ ] Dossier `RESULTATS/` présent avec README
- [ ] Tous les fichiers de documentation présents
- [ ] Taille du ZIP < 50 MB (idéalement < 25 MB)

---

## 🎯 Résumé

**Pour Créer le Package:**

1. `pip install pyarmor==7.7.4`
2. `python build_distribution_client.py`
3. Tester `PACKAGE_CLIENT/`
4. Envoyer `AliExpress_Scraper_v1.0.0_YYYYMMDD.zip`

**Le Client Reçoit:**

- ✅ Code protégé (non-lisible)
- ✅ Application prête à utiliser
- ✅ Documentation complète
- ✅ Dossier RESULTATS/ pour sauvegardes
- ✅ Support inclus

**C'est tout ! Simple et professionnel.** ✅

---

## 📞 Support

En cas de problème avec la génération du package :

1. Vérifier PyArmor: `pyarmor --version` (doit être 7.x)
2. Consulter `OBFUSCATION_MANUELLE.md` pour méthode manuelle
3. Vérifier les logs du script pour les erreurs

---

**Date de création:** 2025-11-10
**Version:** 1.0.0
