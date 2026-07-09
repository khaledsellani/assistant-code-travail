"""Jalon 5 : boucle interactive en ligne de commande."""

import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# On réutilise les fonctions et constantes du jalon 4
from repondre import (
    rechercher, construire_contexte, generer,
    DOSSIER_BASE, NOM_COLLECTION, DATE_CORPUS, AVERTISSEMENT,
)

load_dotenv()

print("Chargement de l'assistant...")
client = chromadb.PersistentClient(path=DOSSIER_BASE)
collection = client.get_collection(NOM_COLLECTION)
modele_embedding = SentenceTransformer(collection.metadata["modele_embedding"])
client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])

print("\n" + "=" * 60)
print("  Assistant Code du travail — base au", DATE_CORPUS)
print("  Posez votre question, ou tapez 'quitter' pour sortir.")
print("=" * 60)

while True:
    question = input("\n❓ Votre question : ").strip()

    if question.lower() in ("quitter", "exit", "q"):
        print("Au revoir !")
        break
    if not question:
        continue  # entrée vide -> on redemande

    resultats = rechercher(collection, modele_embedding, question)
    contexte = construire_contexte(resultats)
    reponse = generer(client_groq, contexte, question)

    print(f"\n{reponse}")
    numeros = [meta["numero"] for meta in resultats["metadatas"][0]]
    print(f"\n📚 Articles consultés : {', '.join(numeros)}")
    print(f"📅 Base à jour au {DATE_CORPUS}")
    print(f"\n{AVERTISSEMENT}")