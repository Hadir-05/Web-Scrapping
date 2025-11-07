"""
Utilitaires pour gérer l'affichage sur Windows
"""

def safe_print(message: str):
    """
    Print avec gestion des erreurs d'encodage Windows

    Windows utilise cp1252 par défaut qui ne supporte pas les emojis Unicode.
    Cette fonction gère gracieusement ces erreurs.

    Args:
        message: Le message à afficher
    """
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback pour Windows avec encodage limité
        try:
            # Retirer les caractères non-ASCII
            ascii_message = message.encode('ascii', 'ignore').decode('ascii')
            print(ascii_message)
        except:
            # Si même ça échoue, ne rien faire
            pass
