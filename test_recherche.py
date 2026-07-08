"""Test jalon 2 : recharge la base SANS réindexer et fait des recherches."""

import chromadb
from sentence_transformers import SentenceTransformer

DOSSIER_BASE = "chroma_db"
NOM_COLLECTION = "code_travail"

# 1. Recharger la base existante (aucun corpus.json, aucun add() : on recharge, c'est tout)
client = chromadb.PersistentClient(path=DOSSIER_BASE)
collection = client.get_collection(NOM_COLLECTION)   # get_ : erreur si absente, c'est voulu
print(f"Base rechargée : {collection.count()} chunks")

# 2. Relire le nom du modèle depuis les métadonnées de la base (voilà pourquoi on l'a tracé !)
nom_modele = collection.metadata["modele_embedding"]
print(f"Modèle d'embedding tracé dans la base : {nom_modele}")
modele = SentenceTransformer(nom_modele)

# 3. Poser quelques questions
questions = [
    "Combien de jours de congés payés par an ?",
    "Quelle est la durée légale du travail ?",
    "Comment fonctionne la rupture conventionnelle ?",
]

for question in questions:
    print("\n" + "=" * 70)
    print(f"QUESTION : {question}")
    # On encode la question avec LE MÊME modèle, puis on cherche les 3 plus proches
    vecteur = modele.encode(question).tolist()
    resultats = collection.query(query_embeddings=[vecteur], n_results=3)
    # resultats contient des listes parallèles : metadatas, documents, distances
    for meta, doc, dist in zip(
        resultats["metadatas"][0], resultats["documents"][0], resultats["distances"][0]
    ):
        print(f"\n  → {meta['numero']}  ({meta['theme']})  distance={dist:.3f}")