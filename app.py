"""Interface web Streamlit — réutilise le pipeline de repondre.py."""

import os
import chromadb
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from repondre import (
    rechercher, construire_contexte, generer,
    DOSSIER_BASE, NOM_COLLECTION, DATE_CORPUS, AVERTISSEMENT,
)

load_dotenv()
SEUIL_CONFIANCE = 18.0   # le même seuil calibré que la CLI



@st.cache_resource
def charger_ressources():
    client = chromadb.PersistentClient(path=DOSSIER_BASE)
    collection = client.get_collection(NOM_COLLECTION)
    modele = SentenceTransformer(collection.metadata["modele_embedding"])
    client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return collection, modele, client_groq


collection, modele_embedding, client_groq = charger_ressources()

# --- La page ---
st.title("⚖️ Assistant Code du travail")
st.caption(f"Base LEGI à jour au {DATE_CORPUS} — RAG sans framework")

question = st.text_input("Votre question sur le droit du travail :")

if question:
    with st.spinner("Recherche dans le Code du travail..."):
        resultats = rechercher(collection, modele_embedding, question)
        meilleure_dist = resultats["distances"][0][0]

        if meilleure_dist > SEUIL_CONFIANCE:
            st.warning(
                f"Confiance faible (distance {meilleure_dist:.1f} > seuil "
                f"{SEUIL_CONFIANCE}) : la question semble éloignée du Code du travail."
            )

        contexte = construire_contexte(resultats)
        reponse = generer(client_groq, contexte, question)

    st.markdown(reponse)

    with st.expander("📚 Articles consultés"):
        for meta, dist in zip(resultats["metadatas"][0], resultats["distances"][0]):
            st.write(f"**{meta['numero']}** — {meta['theme']} (distance {dist:.1f})")

    st.info(AVERTISSEMENT)