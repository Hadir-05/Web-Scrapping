# 🔒 Guide d'Obfuscation Manuelle avec PyArmor 7.x

## 🎯 Objectif

Obfusquer le code pour le distribuer au client sans exposer le code source.

---

## 📋 Prérequis

### Installer PyArmor 7.x

```bash
# Désinstaller PyArmor 8 si installé
pip uninstall pyarmor -y

# Installer PyArmor 7.7.4 (version gratuite)
pip install pyarmor==7.7.4

# Vérifier
pyarmor --version
# Doit afficher: PyArmor 7.7.4
```

---

## 🛠️ Méthode 1 : Script Automatique avec Debug

```bash
python build_obfuscated_debug.py
```

Ce script :
- ✅ Vérifie la version de PyArmor
- ✅ Obfusque automatiquement
- ✅ Affiche les erreurs clairement
- ✅ Essaie plusieurs méthodes

---

## 🛠️ Méthode 2 : Manuelle (Si le script échoue)

### Étape 1 : Créer le Dossier de Distribution

```bash
# Créer le dossier
mkdir distribution_client
cd distribution_client

# Créer la structure
mkdir src
```

### Étape 2 : Copier les Fichiers Non-Python

```bash
# Depuis le dossier distribution_client
# Copier les fichiers de configuration
cp ../requirements.txt .
cp ../Lancer_Application.bat .
cp ../Lancer_Application.sh .
cp ../LISEZ-MOI.txt .
cp ../GUIDE_INSTALLATION_CLIENT.md .
```

### Étape 3 : Copier et Obfusquer app.py

```bash
# Copier app.py
cp ../app.py .

# Obfusquer sur place
pyarmor obfuscate --in-place app.py
```

**Vérification :**
```bash
# Vérifier que app.py existe et est obfusqué
cat app.py | head -20
# Vous devriez voir du code crypté au début
```

### Étape 4 : Obfusquer le Dossier src/

**Option A : Tout obfusquer en une fois**

```bash
# Depuis distribution_client/
cd ..
pyarmor obfuscate --output distribution_client/src --recursive src/*.py
```

**Option B : Obfusquer fichier par fichier** (plus fiable)

```bash
# Copier d'abord tous les fichiers
cp -r ../src/* src/

# Obfusquer chaque fichier Python
cd src

# Trouver tous les .py et les obfusquer
find . -name "*.py" -type f | while read file; do
    echo "Obfuscation de $file..."
    pyarmor obfuscate --in-place "$file"
done

cd ..
```

**Sur Windows (PowerShell) :**

```powershell
# Copier les fichiers
Copy-Item -Recurse ..\src\* src\

# Obfusquer chaque fichier
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    Write-Host "Obfuscation de $($_.FullName)..."
    pyarmor obfuscate --in-place $_.FullName
}
```

### Étape 5 : Vérifier le Résultat

```bash
# Lister le contenu
ls -la
# Vous devriez voir:
# - app.py (obfusqué)
# - src/ (avec fichiers .py obfusqués)
# - requirements.txt
# - Lancer_Application.bat
# - etc.

# Compter les fichiers Python
find . -name "*.py" | wc -l
# Doit correspondre au nombre original
```

### Étape 6 : Tester

```bash
# Depuis distribution_client/
python app.py
# OU
python Lancer_Application.bat
```

**Si ça marche → ✅ Obfuscation réussie !**

### Étape 7 : Créer le ZIP

```bash
# Revenir au dossier parent
cd ..

# Créer le ZIP
zip -r AliExpress_Scraper_Client.zip distribution_client/

# OU sur Windows (PowerShell)
Compress-Archive -Path distribution_client -Destination AliExpress_Scraper_Client.zip
```

---

## 🔍 Debugging : Problèmes Fréquents

### Problème 1 : "pyarmor : commande introuvable"

**Solution :**
```bash
pip install pyarmor==7.7.4
```

### Problème 2 : "RuntimeError: unauthorized use of script (1:1137)"

**Cause :** Vous avez PyArmor 8.x au lieu de 7.x

**Solution :**
```bash
pip uninstall pyarmor -y
pip install pyarmor==7.7.4
# Puis réobfusquer
```

### Problème 3 : app.py n'est pas créé

**Solution :** Utiliser la méthode manuelle (copier puis obfusquer sur place)

```bash
cp app.py distribution_client/
cd distribution_client
pyarmor obfuscate --in-place app.py
```

### Problème 4 : "ModuleNotFoundError: No module named 'src'"

**Cause :** Le dossier src/ n'a pas été obfusqué ou copié

**Solution :**
```bash
# Vérifier que src/ existe
ls -la distribution_client/src/

# Si vide ou manquant, copier et obfusquer
cp -r src distribution_client/
cd distribution_client/src
find . -name "*.py" | while read f; do pyarmor obfuscate --in-place "$f"; done
```

### Problème 5 : Le code obfusqué ne fonctionne pas

**Solutions à essayer :**

1. **Ajouter `pytransform/` au package**
   ```bash
   # PyArmor crée un dossier pytransform/ nécessaire
   # S'assurer qu'il est dans distribution_client/
   ls distribution_client/pytransform/
   ```

2. **Utiliser `--no-cross-protection`**
   ```bash
   pyarmor obfuscate --no-cross-protection --in-place app.py
   ```

3. **Réinitialiser PyArmor**
   ```bash
   pyarmor init
   # Puis réessayer l'obfuscation
   ```

---

## 📊 Vérification Finale

Avant de distribuer, vérifier :

- [ ] PyArmor 7.7.4 installé (PAS 8.x)
- [ ] `distribution_client/app.py` existe et est obfusqué
- [ ] `distribution_client/src/` existe avec fichiers .py obfusqués
- [ ] `distribution_client/pytransform/` existe (dossier PyArmor)
- [ ] `distribution_client/Lancer_Application.bat` existe
- [ ] `distribution_client/requirements.txt` existe
- [ ] Test : `python app.py` fonctionne dans distribution_client/
- [ ] Test : Une recherche fonctionne normalement
- [ ] ZIP créé et testé sur une autre machine

---

## 🎯 Alternative : Sans Obfuscation

Si l'obfuscation pose trop de problèmes, considérez :

### Option A : PyInstaller (.exe)

```bash
pip install pyinstaller
python build_exe_simple.py
```

**Avantages :**
- ✅ Code compilé (meilleure protection qu'obfuscation)
- ✅ Pas de problème de licence

**Inconvénients :**
- ⚠️ Package lourd (500MB-2GB)
- ⚠️ Peut échouer avec Streamlit

### Option B : Streamlit Cloud

Le code reste sur VOTRE serveur, le client accède via un lien.

**Avantages :**
- ✅✅✅ Sécurité maximale (code jamais chez le client)
- ✅ Gratuit
- ✅ Simple

**Inconvénients :**
- ⚠️ Nécessite Internet

---

## 📝 Résumé des Commandes

```bash
# 1. Installer PyArmor 7.x
pip uninstall pyarmor -y
pip install pyarmor==7.7.4

# 2. Créer la structure
mkdir distribution_client
cd distribution_client
mkdir src

# 3. Copier les fichiers de config
cp ../requirements.txt .
cp ../Lancer_Application.bat .
cp ../LISEZ-MOI.txt .

# 4. Obfusquer app.py
cp ../app.py .
pyarmor obfuscate --in-place app.py

# 5. Copier et obfusquer src/
cp -r ../src/* src/
cd src
find . -name "*.py" -exec pyarmor obfuscate --in-place {} \;
cd ..

# 6. Tester
python app.py

# 7. Créer le ZIP
cd ..
zip -r Client.zip distribution_client/
```

---

## 🆘 Support

Si rien ne fonctionne, contactez-moi avec :
- Version de PyArmor : `pyarmor --version`
- Version de Python : `python --version`
- Messages d'erreur complets
- Sortie de : `ls -la distribution_client/`

---

**Date de création :** 2025-11-06
**Version :** 1.0.0
