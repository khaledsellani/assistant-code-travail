"""Jalon 6 : calibration du seuil de confiance.

On compare les distances obtenues pour des questions DANS le domaine
vs des questions HORS domaine, pour choisir un seuil entre les deux.
"""

import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("code_travail")
modele = SentenceTransformer(collection.metadata["modele_embedding"])

QUESTIONS_DANS_DOMAINE = [
    "Combien de jours de congés payés par an ?",
    "Quelle est la durée légale du travail ?",
    "Quel est le délai de rétractation d'une rupture conventionnelle ?",
    "Qu'est-ce que le harcèlement moral ?",
    "Le CDD peut-il être renouvelé ?",
]
QUESTIONS_HORS_DOMAINE = [
    "Quelle est la capitale de l'Australie ?",
    "Comment faire une tarte aux pommes ?",
    "Qui a gagné la coupe du monde 1998 ?",
    "Comment fonctionne un moteur électrique ?",
    "Quel temps fera-t-il demain ?",
]

def meilleure_distance(question):
    vecteur = modele.encode(question).tolist()
    resultats = collection.query(query_embeddings=[vecteur], n_results=1)
    return resultats["distances"][0][0]

print("Questions DANS le domaine :")
for q in QUESTIONS_DANS_DOMAINE:
    print(f"  {meilleure_distance(q):7.3f}  {q}")

print("\nQuestions HORS domaine :")
for q in QUESTIONS_HORS_DOMAINE:
    print(f"  {meilleure_distance(q):7.3f}  {q}")