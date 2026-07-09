"""Exploration : trouver quelques fichiers d'articles et afficher le contenu d'un."""

from pathlib import Path

# Path("data/legi") représente le dossier extrait ;
# rglob cherche récursivement dans TOUS les sous-dossiers
dossier = Path("data/legi")

# On cherche les fichiers d'articles : ils commencent par LEGIARTI
fichiers_articles = list(dossier.rglob("LEGIARTI*.xml"))

print(f"Nombre de fichiers d'articles trouvés : {len(fichiers_articles)}")

# Affichons le contenu brut du premier, pour découvrir la structure
premier = fichiers_articles[0]
print(f"\n--- Contenu de {premier.name} ---\n")
print(premier.read_text(encoding="utf-8"))