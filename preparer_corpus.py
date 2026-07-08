"""Jalon 1 : construit le corpus JSON à partir des fichiers XML du Code du travail.

Pour chaque article : on ne garde que les versions en vigueur,
appartenant aux thèmes du projet, avec texte nettoyé et métadonnées.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

DOSSIER_XML = Path("data/legi")
FICHIER_SORTIE = "data/corpus.json"
DATE_CORPUS = "2025-07-13"  # date de l'archive LEGI téléchargée

# Nos thèmes : pour chaque chapitre du code (ex: L3121), le thème associé.
# Les plages viennent du tableau du sujet.
def attribuer_theme(numero):
    """Retourne le thème d'un article d'après son numéro, ou None si hors sujet."""
    # On ne garde que les articles législatifs (qui commencent par L)
    if not numero or not numero.startswith("L"):
        return None
    try:
        # "L3121-1" -> chapitre 3121, suffixe 1
        partie_chapitre = numero[1:].split("-")[0]
        chapitre = int(partie_chapitre)
        suffixe = int(numero.split("-")[1]) if "-" in numero else 0
    except ValueError:
        return None  # numéros exotiques (ex: "L124-1 bis"), on ignore

    if chapitre == 3121:
        return "Durée du travail et heures supplémentaires"
    if chapitre == 3141:
        return "Congés payés"
    if 1231 <= chapitre <= 1237:
        # Cas particulier : la rupture conventionnelle est L1237-11 à L1237-19
        if chapitre == 1237 and 11 <= suffixe <= 19:
            return "Rupture conventionnelle"
        return "Licenciement"
    if 1221 <= chapitre <= 1248:
        return "Contrat de travail (CDI, CDD)"
    if 3231 <= chapitre <= 3232:
        return "Salaire minimum (SMIC)"
    if 1152 <= chapitre <= 1155:
        return "Harcèlement et discrimination"
    return None  # article hors de nos thèmes


def extraire_article(chemin_fichier):
    """Lit un fichier XML d'article et retourne un dictionnaire, ou None si à ignorer."""
    arbre = ET.parse(chemin_fichier)
    racine = arbre.getroot()

    # .findtext cherche une balise et retourne son texte
    etat = racine.findtext(".//ETAT")
    if etat != "VIGUEUR":
        return None  # ancienne version ou article abrogé -> on ignore

    numero = racine.findtext(".//NUM")
    theme = attribuer_theme(numero)
    if theme is None:
        return None  # hors de nos thèmes -> on ignore

    # Le texte : on prend tout le contenu de CONTENU, débarrassé des balises <p> etc.
    # itertext() récupère uniquement le texte, en ignorant les balises
    bloc = racine.find(".//BLOC_TEXTUEL/CONTENU")
    if bloc is None:
        return None
    texte = " ".join(morceau.strip() for morceau in bloc.itertext())
    texte = " ".join(texte.split())  # supprime espaces multiples et sauts de ligne
    if not texte:
        return None  # article vide

    # La section : le dernier TITRE_TM du CONTEXTE (le niveau le plus précis du plan)
    titres = [t.text.strip() for t in racine.findall(".//CONTEXTE//TITRE_TM") if t.text]
    section = titres[-1] if titres else ""

    return {
        "id": racine.findtext(".//META_COMMUN/ID"),
        "numero": numero,
        "theme": theme,
        "section": section,
        "texte": texte,
        "date_debut": racine.findtext(".//DATE_DEBUT"),
        "source": f"Code du travail (base LEGI du {DATE_CORPUS})",
    }


# --- Programme principal ---
corpus = []
fichiers = list(DOSSIER_XML.rglob("LEGIARTI*.xml"))
print(f"{len(fichiers)} fichiers d'articles à examiner...")

for i, fichier in enumerate(fichiers):
    article = extraire_article(fichier)
    if article is not None:
        corpus.append(article)
    if (i + 1) % 5000 == 0:
        print(f"  {i + 1} fichiers examinés, {len(corpus)} articles retenus")

# Sauvegarde en JSON (indent=2 pour un fichier lisible, ensure_ascii=False pour les accents)
with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
    json.dump(corpus, f, indent=2, ensure_ascii=False)

print(f"\nTerminé ! {len(corpus)} articles sauvegardés dans {FICHIER_SORTIE}")

# Petit bilan par thème
from collections import Counter
compte = Counter(article["theme"] for article in corpus)
for theme, nombre in compte.most_common():
    print(f"  {theme} : {nombre} articles")