# 🐍 Guide : Installer Python 3.10 pour PyArmor

## 🎯 Problème

Vous avez **Python 3.13.9** mais PyArmor 7.7.4 ne supporte que **Python 3.10 maximum**.

## ✅ Solution

Installer **Python 3.10 en parallèle** sans toucher à votre Python 3.13.

---

## 📋 Installation Étape par Étape

### Étape 1 : Télécharger Python 3.10.11

**Lien direct :** https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

1. Télécharger le fichier
2. Lancer l'installateur

### Étape 2 : Installation Personnalisée

⚠️ **TRÈS IMPORTANT** : Configuration spéciale

1. ✅ **Cocher** : "Add python.exe to PATH"
2. Cliquer sur **"Customize installation"**
3. Page "Optional Features" : Tout cocher, cliquer **Next**
4. Page "Advanced Options" :
   - ✅ Cocher "Install for all users"
   - **⚠️ IMPORTANT** : Changer "Customize install location" vers :
     ```
     C:\Python310
     ```
5. Cliquer **Install**

### Étape 3 : Vérification

Ouvrir un **nouveau** PowerShell et taper :

```powershell
C:\Python310\python.exe --version
```

Doit afficher : `Python 3.10.11`

---

## 🚀 Utilisation Automatique

J'ai créé un script qui fait TOUT automatiquement :

### 1. Lancer le Setup

```powershell
.\setup_pyarmor_python310.bat
```

Ce script va :
- ✅ Vérifier que Python 3.10 est installé
- ✅ Créer un environnement virtuel avec Python 3.10
- ✅ Installer toutes les dépendances
- ✅ Installer PyArmor 7.7.4
- ✅ Tester que PyArmor fonctionne

### 2. Générer le Package Obfusqué

```powershell
# L'environnement Python 3.10 est déjà activé
python build_pyarmor_final.py
```

---

## 🎯 Résultat Attendu

```
================================================================================
  SUCCES: ENVIRONNEMENT PRET
================================================================================

Vous pouvez maintenant utiliser PyArmor:

   python build_pyarmor_final.py

L'environnement Python 3.10 est active dans ce terminal.
```

---

## 📦 Après la Génération

Vous obtiendrez :
- `PACKAGE_CLIENT_PYARMOR/` → Dossier avec code obfusqué
- `AliExpress_Scraper_PYARMOR_v1.0.0_YYYYMMDD.zip` → Archive pour le client

---

## 🔧 Utilisation Quotidienne

### Pour utiliser PyArmor (à chaque fois)

```powershell
# Activer l'environnement Python 3.10
.\venv_py310\Scripts\Activate.ps1

# Utiliser PyArmor
python build_pyarmor_final.py

# Désactiver quand terminé
deactivate
```

### Pour vos autres projets (Python 3.13)

```powershell
# Utiliser normalement
python votre_script.py
```

Les deux versions cohabitent sans problème !

---

## ❓ FAQ

### Q : Est-ce que ça va casser mon Python 3.13 ?

**Non.** Les deux versions sont totalement indépendantes.

### Q : Comment je sais quelle version j'utilise ?

```powershell
python --version
# Affiche la version par défaut (3.13)

C:\Python310\python.exe --version
# Affiche toujours 3.10
```

### Q : Je dois faire ça à chaque fois ?

**Non.** Une fois l'environnement créé (`venv_py310`), vous n'avez qu'à :
```powershell
.\venv_py310\Scripts\Activate.ps1
python build_pyarmor_final.py
```

### Q : Puis-je désinstaller Python 3.10 après ?

**Oui**, mais vous devrez le réinstaller si vous voulez utiliser PyArmor à nouveau.

---

## 🆘 Problèmes Courants

### Problème 1 : "python n'est pas reconnu"

**Solution :** Utilisez le chemin complet
```powershell
C:\Python310\python.exe -m venv venv_py310
```

### Problème 2 : "Impossible d'exécuter des scripts"

**Solution :** Autoriser les scripts PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problème 3 : "setup_pyarmor_python310.bat ne trouve pas Python 3.10"

**Solution :** Vérifier que Python 3.10 est bien dans `C:\Python310`
```powershell
dir C:\Python310
```

Si pas là, réinstaller Python 3.10 avec le bon chemin.

---

## 📊 Récapitulatif

```
┌─────────────────────────────────────────────────────────────┐
│                    INSTALLATION                             │
├─────────────────────────────────────────────────────────────┤
│ 1. Télécharger Python 3.10.11                               │
│ 2. Installer dans C:\Python310                              │
│ 3. Lancer setup_pyarmor_python310.bat                       │
├─────────────────────────────────────────────────────────────┤
│                    UTILISATION                              │
├─────────────────────────────────────────────────────────────┤
│ 1. .\venv_py310\Scripts\Activate.ps1                        │
│ 2. python build_pyarmor_final.py                            │
│ 3. Envoyer le ZIP au client                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Avantages de Cette Approche

- ✅ Python 3.13 intact (vos autres projets)
- ✅ Python 3.10 pour PyArmor uniquement
- ✅ Automatisation complète (scripts)
- ✅ Pas de conflits entre versions
- ✅ Facile à désinstaller si besoin

---

**Date :** 2025-11-10
**Version :** 1.0
