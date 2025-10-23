"""
Script pour créer des modèles PyTorch mock pour la démo
"""
import torch
import torch.nn as nn

class MockKeywordModel(nn.Module):
    """Modèle mock pour recherche par mots-clés"""
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 128)

    def encode(self, text):
        """Encode un texte en embeddings"""
        # Mock: retourne des embeddings aléatoires
        return torch.randn(1, 128)

    def forward(self, x):
        return self.linear(x)


class MockImageModel(nn.Module):
    """Modèle mock pour recherche par image"""
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, 3)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(64, 128)

    def extract_features(self, image):
        """Extrait les features d'une image"""
        # Mock: retourne des features aléatoires
        return torch.randn(1, 128)

    def forward(self, x):
        x = self.conv(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


# Créer et sauvegarder les modèles mock
print("🔄 Création des modèles mock...")

# Modèle keyword
keyword_model = MockKeywordModel()
keyword_model.eval()
torch.save(keyword_model, 'models/keyword_search.pth')
print("✅ keyword_search.pth créé")

# Modèle image
image_model = MockImageModel()
image_model.eval()
torch.save(image_model, 'models/image_similarity.pth')
print("✅ image_similarity.pth créé")

print("\n🎉 Modèles mock créés avec succès!")
print("📝 Note: Ce sont des modèles de démonstration")
print("   Remplacez-les par vos vrais modèles .pth plus tard")
