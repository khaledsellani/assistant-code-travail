"""Jalon 3 : valide le retrieval sur des questions dont on connaît l'article attendu.

Pour chaque question, on vérifie que l'article attendu remonte dans le top-k.
Ce jeu de questions servira ensuite de jeu d'évaluation du projet.
"""

import chromadb
from sentence_transformers import SentenceTransformer

DOSSIER_BASE = "chroma_db"
NOM_COLLECTION = "code_travail"
TOP_K = 5   # on regarde les 5 premiers résultats

# Notre jeu d'évaluation : (question, article attendu)
JEU_DE_TEST = [
    ("Combien de jours de congés payés par an ?", "L3141-3"),
    ("Quelle est la durée légale du travail par semaine ?", "L3121-27"),
    ("Quel est le délai de rétractation pour une rupture conventionnelle ?", "L1237-13"),
    ("Qu'est-ce que le harcèlement moral ?", "L1152-1"),
    ("Une période d'essai peut-elle être renouvelée ?", "L1221-21"),
]

# Recharger la base et le modèle tracé
client = chromadb.PersistentClient(path=DOSSIER_BASE)
collection = client.get_collection(NOM_COLLECTION)
modele = SentenceTransformer(collection.metadata["modele_embedding"])
print(f"Base : {collection.count()} chunks | top-k = {TOP_K}\n")

reussites = 0
for question, article_attendu in JEU_DE_TEST:
    vecteur = modele.encode(question).tolist()
    resultats = collection.query(query_embeddings=[vecteur], n_results=TOP_K)
    numeros_trouves = [meta["numero"] for meta in resultats["metadatas"][0]]

    trouve = article_attendu in numeros_trouves
    if trouve:
        reussites += 1
        # .index() donne la position (0 = premier), on affiche en rang humain (1 = premier)
        rang = numeros_trouves.index(article_attendu) + 1
        print(f"✅ '{question}'")
        print(f"   {article_attendu} trouvé au rang {rang}/{TOP_K}")
    else:
        print(f"❌ '{question}'")
        print(f"   {article_attendu} ABSENT du top-{TOP_K}. Trouvés : {numeros_trouves}")
    print()

print(f"Score : {reussites}/{len(JEU_DE_TEST)} articles attendus dans le top-{TOP_K}")