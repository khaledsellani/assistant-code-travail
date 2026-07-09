"""Interface web Streamlit en mode chat — réutilise le pipeline de repondre.py."""

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
SEUIL_CONFIANCE = 18.0

@st.cache_resource(show_spinner="Chargement du modèle et de la base (première fois uniquement)...")
def charger_ressources():
    client = chromadb.PersistentClient(path=DOSSIER_BASE)
    collection = client.get_collection(NOM_COLLECTION)
    modele = SentenceTransformer(collection.metadata["modele_embedding"])
    client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return collection, modele, client_groq


collection, modele_embedding, client_groq = charger_ressources()

# --- Barre latérale : les infos du projet ---
with st.sidebar:
    st.header("⚖️ À propos")
    st.write(f"**Corpus :** Code du travail, base LEGI du {DATE_CORPUS}")
    st.write(f"**Articles indexés :** {collection.count()}")
    st.write("**Thèmes :** durée du travail, congés payés, contrat de travail, "
             "licenciement, rupture conventionnelle, SMIC, harcèlement")
    st.write(f"**Seuil de confiance :** {SEUIL_CONFIANCE}")
    st.divider()
    st.caption(AVERTISSEMENT)

st.title("⚖️ Assistant Code du travail")

# --- Initialisation de l'historique (première exécution seulement) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Ré-affichage de tout l'historique à chaque exécution ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Articles consultés"):
                st.write(message["sources"])

# --- Saisie utilisateur ---
question = st.chat_input("Posez votre question sur le droit du travail...")

if question:
    # 1. Afficher et mémoriser la question
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # 2. Pipeline RAG (le même que la CLI)
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans le Code du travail..."):
            resultats = rechercher(collection, modele_embedding, question)
            meilleure_dist = resultats["distances"][0][0]

            if meilleure_dist > SEUIL_CONFIANCE:
                st.warning(f"Confiance faible (distance {meilleure_dist:.1f} > "
                           f"seuil {SEUIL_CONFIANCE}) : question éloignée du Code du travail.")

            contexte = construire_contexte(resultats)
            reponse = generer(client_groq, contexte, question)

        st.markdown(reponse)
        sources = ", ".join(
            f"{meta['numero']} (d={dist:.1f})"
            for meta, dist in zip(resultats["metadatas"][0], resultats["distances"][0])
        )
        with st.expander("📚 Articles consultés"):
            st.write(sources)
        st.caption(f"📅 Base au {DATE_CORPUS} — {AVERTISSEMENT}")

    # 3. Mémoriser la réponse (avec ses sources) pour les ré-affichages
    st.session_state.messages.append(
        {"role": "assistant", "content": reponse, "sources": sources}
    )