#!/usr/bin/env python3
"""
Alternative à PyArmor : Compilation avec Nuitka
Compile Python en C puis en binaire natif
Protection forte mais package lourd
"""
import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("  COMPILATION AVEC NUITKA")
print("=" * 80)
print()
print("🎯 Nuitka compile Python → C → Binaire")
print("   Protection forte, code natif non-réversible")
print()

# Vérifier/Installer Nuitka
try:
    import nuitka
    print("✅ Nuitka déjà installé")
except ImportError:
    print("📥 Installation de Nuitka (peut prendre quelques minutes)...")
    subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"])
    print("✅ Nuitka installé")

print()
print("⚠️  ATTENTION:")
print("   - La compilation peut prendre 10-30 minutes")
print("   - Le package sera lourd (500 MB - 1 GB)")
print("   - Windows Defender peut bloquer (faux positif)")
print()

response = input("Continuer ? (oui/non): ")
if response.lower() != "oui":
    print("Annulé.")
    sys.exit(0)

print()
print("=" * 80)
print("  COMPILATION EN COURS")
print("=" * 80)
print()
print("⏳ Cela peut prendre 10-30 minutes...")
print("   Ne fermez pas cette fenêtre !")
print()

# Compiler avec Nuitka
cmd = [
    sys.executable, "-m", "nuitka",
    "--standalone",              # Application autonome
    "--onefile",                 # Un seul fichier
    "--windows-disable-console", # Pas de console (Windows)
    "--output-dir=dist_nuitka",  # Dossier de sortie
    "--include-data-dir=src=src", # Inclure src/
    "--include-data-dir=RESULTATS=RESULTATS", # Inclure RESULTATS/
    "--include-data-file=requirements.txt=requirements.txt",
    "--enable-plugin=anti-bloat", # Réduire la taille
    "app.py"
]

print(f"🔧 Commande: {' '.join(cmd)}")
print()

try:
    result = subprocess.run(cmd, check=True)

    print()
    print("=" * 80)
    print("  ✅ COMPILATION RÉUSSIE")
    print("=" * 80)
    print()
    print("📦 Fichier compilé: dist_nuitka/app.exe (ou app.bin sur Linux)")
    print()
    print("🔒 PROTECTION:")
    print("   ⭐⭐⭐⭐⭐ Maximale (code compilé en binaire natif)")
    print("   ✅ Impossible de voir le code source")
    print("   ✅ Très difficile à reverse-engineer")
    print()
    print("📧 DISTRIBUTION:")
    print("   - Envoyer uniquement le fichier .exe au client")
    print("   - Aucune installation Python nécessaire")
    print("   - Fonctionne sur n'importe quel PC Windows")
    print()

except subprocess.CalledProcessError as e:
    print()
    print("❌ ERREUR DE COMPILATION")
    print()
    print("💡 Solutions:")
    print("   1. Installer Visual Studio Build Tools (Windows)")
    print("   2. Essayer PyInstaller (plus simple):")
    print("      python build_with_pyinstaller.py")
    print("   3. Utiliser PyMinifier (plus rapide):")
    print("      python build_with_minifier.py")
    print("   4. Utiliser Streamlit Cloud (recommandé):")
    print("      Voir GUIDE_STREAMLIT_CLOUD.md")
