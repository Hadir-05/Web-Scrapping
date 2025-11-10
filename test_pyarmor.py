#!/usr/bin/env python3
"""
Script de diagnostic pour tester PyArmor
"""
import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("  DIAGNOSTIC PYARMOR")
print("=" * 80)
print()

# Test 1: Version
print("1️⃣ Version de PyArmor:")
try:
    result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
    print(f"   Sortie: {result.stdout}")
    print(f"   Erreurs: {result.stderr}")
    print(f"   Code retour: {result.returncode}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()

# Test 2: Obfuscation simple
print("2️⃣ Test d'obfuscation simple:")
print("   Création d'un fichier test.py...")

test_file = Path("test_simple.py")
test_file.write_text("""
def hello():
    print("Hello World")

if __name__ == "__main__":
    hello()
""")

print("   ✅ Fichier créé")
print()
print("   Tentative d'obfuscation...")

try:
    result = subprocess.run([
        "pyarmor", "obfuscate", "--output", "test_obf", "test_simple.py"
    ], capture_output=True, text=True, timeout=30)

    print(f"   Code retour: {result.returncode}")
    print(f"   Stdout: {result.stdout[:200]}")
    print(f"   Stderr: {result.stderr[:200]}")

    # Vérifier le résultat
    obf_file = Path("test_obf/test_simple.py")
    pytransform = Path("test_obf/pytransform")

    if obf_file.exists():
        print("   ✅ Fichier obfusqué créé")

        # Lire le contenu
        content = obf_file.read_text()
        if "pyarmor" in content.lower() or "__pyarmor__" in content:
            print("   ✅ Le fichier est obfusqué")
        else:
            print("   ❌ Le fichier n'est PAS obfusqué")
            print(f"   Aperçu: {content[:200]}")
    else:
        print("   ❌ Fichier obfusqué non créé")

    if pytransform.exists():
        print("   ✅ Dossier pytransform/ créé")
    else:
        print("   ❌ Dossier pytransform/ manquant")

except subprocess.TimeoutExpired:
    print("   ❌ Timeout (>30s)")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()

# Test 3: Installation de PyArmor
print("3️⃣ Vérification de l'installation:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "show", "pyarmor"],
                          capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()
print("=" * 80)
print("  DIAGNOSTIC TERMINÉ")
print("=" * 80)
print()

# Nettoyer
if test_file.exists():
    test_file.unlink()

print("💡 RECOMMANDATIONS:")
print()

# Analyser les résultats
if Path("test_obf/pytransform").exists():
    print("✅ PyArmor fonctionne correctement")
    print("   Le problème vient d'ailleurs dans le script de build")
else:
    print("❌ PyArmor ne fonctionne PAS")
    print()
    print("Solutions recommandées:")
    print()
    print("1️⃣ RÉINSTALLER PyArmor 7.7.4:")
    print("   pip uninstall pyarmor -y")
    print("   pip install pyarmor==7.7.4")
    print()
    print("2️⃣ UTILISER STREAMLIT CLOUD (Recommandé):")
    print("   - Protection maximale (code reste sur votre serveur)")
    print("   - Gratuit et simple")
    print("   - Le client accède via navigateur")
    print("   → https://streamlit.io/cloud")
    print()
    print("3️⃣ UTILISER PYINSTALLER (.exe):")
    print("   pip install pyinstaller")
    print("   pyinstaller --onefile app.py")
    print("   (Package lourd mais code compilé)")
    print()
    print("4️⃣ DISTRIBUER SANS PROTECTION:")
    print("   python build_simple_sans_obfuscation.py")
    print("   (Avec contrat/NDA uniquement)")
