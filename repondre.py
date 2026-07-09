"""Jalon 4 : recherche + génération avec citations via Groq."""

import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()  # charge GROQ_API_KEY depuis .env

DOSSIER_BASE = "chroma_db"
NOM_COLLECTION = "code_travail"
TOP_K = 5
MODELE_LLM = "llama-3.3-70b-versatile"
DATE_CORPUS = "13 juillet 2025"

AVERTISSEMENT = (
    "⚖️  Cet assistant ne fournit pas de conseil juridique. Consultez un avocat "
    "ou l'inspection du travail pour votre situation personnelle."
)

PROMPT_SYSTEME = f"""Tu es un assistant documentaire sur le Code du travail français.
Tu réponds UNIQUEMENT à partir des articles fournis dans le contexte.

Règles impératives :
1. Chaque affirmation doit citer le numéro d'article qui la fonde, ex : (art. L3121-27).
2. Tu ne cites JAMAIS un numéro d'article absent du contexte fourni.
3. Si le contexte ne permet pas de répondre, tu réponds exactement :
   "Je ne trouve pas cette information dans ma base."
4. Si la règle varie selon la taille de l'entreprise ou la convention collective,
   tu donnes la règle générale ET tu signales explicitement cette variation.
5. Si la question demande d'évaluer une situation personnelle (ex : "mon licenciement
   est-il abusif ?"), tu donnes les règles générales applicables mais tu refuses de te
   prononcer sur le cas particulier et tu renvoies vers un avocat ou l'inspection du travail.
6. Ta base date du {DATE_CORPUS} : si la question porte sur une évolution récente,
   signale que ta base peut être obsolète.
Réponds en français, de façon claire et concise."""


def rechercher(collection, modele_embedding, question):
    """Retourne les TOP_K chunks les plus proches de la question."""
    vecteur = modele_embedding.encode(question).tolist()
    return collection.query(query_embeddings=[vecteur], n_results=TOP_K)


def construire_contexte(resultats):
    """Assemble les chunks en un contexte numéroté par article (choix Q2)."""
    blocs = []
    for meta, doc in zip(resultats["metadatas"][0], resultats["documents"][0]):
        blocs.append(f"[Article {meta['numero']}]\n{doc}")
    return "\n\n---\n\n".join(blocs)


def generer(client_groq, contexte, question):
    """Appelle le LLM avec le contexte et la question."""
    reponse = client_groq.chat.completions.create(
        model=MODELE_LLM,
        temperature=0.1,   # basse : on veut du factuel, pas de la créativité
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": f"Contexte :\n\n{contexte}\n\nQuestion : {question}"},
        ],
    )
    return reponse.choices[0].message.content


# --- Programme principal (version test : une question) ---
if __name__ == "__main__":
    client = chromadb.PersistentClient(path=DOSSIER_BASE)
    collection = client.get_collection(NOM_COLLECTION)
    modele_embedding = SentenceTransformer(collection.metadata["modele_embedding"])
    client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])

    question = "Quelle est la durée légale du travail par semaine ?"
    print(f"QUESTION : {question}\n")

    resultats = rechercher(collection, modele_embedding, question)
    contexte = construire_contexte(resultats)
    reponse = generer(client_groq, contexte, question)

    print(reponse)
    # Sources affichées PAR LE CODE, depuis les métadonnées (choix Q2) :
    numeros = [meta["numero"] for meta in resultats["metadatas"][0]]
    print(f"\n📚 Articles consultés : {', '.join(numeros)}")
    print(f"📅 Base à jour au {DATE_CORPUS}")
    print(f"\n{AVERTISSEMENT}")