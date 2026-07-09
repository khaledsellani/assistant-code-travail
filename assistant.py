"""Jalon 5 + 6 : boucle interactive avec score de confiance."""

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

SEUIL_CONFIANCE = 18.0  

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

    # --- Jalon 6 : score de confiance ---
    meilleure_dist = resultats["distances"][0][0]
    if meilleure_dist > SEUIL_CONFIANCE:
        print(f"\n⚠️  Confiance faible (distance {meilleure_dist:.1f} > seuil "
              f"{SEUIL_CONFIANCE}) : la question semble éloignée du Code du "
              f"travail, la réponse est à prendre avec précaution.")

    contexte = construire_contexte(resultats)
    reponse = generer(client_groq, contexte, question)

    print(f"\n{reponse}")

    # Sources avec leur distance (transparence du retrieval)
    numeros = [
        f"{meta['numero']} (d={dist:.1f})"
        for meta, dist in zip(resultats["metadatas"][0], resultats["distances"][0])
    ]
    print(f"\n📚 Articles consultés : {', '.join(numeros)}")
    print(f"📅 Base à jour au {DATE_CORPUS}")
    print(f"\n{AVERTISSEMENT}")