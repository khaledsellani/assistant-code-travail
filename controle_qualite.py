"""Contrôle qualité du jalon 1 : affiche 10 articles au hasard pour relecture."""

import json
import random

with open("data/corpus.json", encoding="utf-8") as f:
    corpus = json.load(f)

print(f"Corpus : {len(corpus)} articles\n")

# random.sample tire 10 éléments au hasard, sans doublon
for article in random.sample(corpus, 10):
    print("=" * 70)
    print(f"Article {article['numero']}  |  Thème : {article['theme']}")
    print(f"Section : {article['section']}")
    print(f"En vigueur depuis : {article['date_debut']}")
    print("-" * 70)
    # On affiche les 400 premiers caractères du texte
    print(article["texte"][:400] + ("..." if len(article["texte"]) > 400 else ""))
    print()