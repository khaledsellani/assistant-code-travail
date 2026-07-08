"""Jalon 2 : chunking + embeddings + base vectorielle persistante."""

import json
import chromadb
from sentence_transformers import SentenceTransformer

CORPUS = "data/corpus.json"
DOSSIER_BASE = "chroma_db"          # là où la base sera sauvegardée
NOM_COLLECTION = "code_travail"
MODELE_EMBEDDING = "paraphrase-multilingual-MiniLM-L12-v2"  # multilingue, léger

# 1. Charger le corpus
with open(CORPUS, encoding="utf-8") as f:
    corpus = json.load(f)
print(f"{len(corpus)} articles chargés")

# 2. Construire les chunks : notre stratégie Q1
#    un chunk = un article, texte préfixé par numéro + thème + section
textes = []
metadonnees = []
ids = []
for article in corpus:
    prefixe = f"[Article {article['numero']}] {article['theme']} — {article['section']}"
    textes.append(f"{prefixe}\n{article['texte']}")
    metadonnees.append({
        "numero": article["numero"],
        "theme": article["theme"],
        "section": article["section"],
        "date_debut": article["date_debut"],
        "source": article["source"],
    })
    ids.append(article["id"])

# 3. Calculer les embeddings
print(f"Chargement du modèle {MODELE_EMBEDDING}...")
modele = SentenceTransformer(MODELE_EMBEDDING)
print("Calcul des embeddings (une barre de progression va s'afficher)...")
embeddings = modele.encode(textes, show_progress_bar=True)

# 4. Créer la base persistante et y ranger les chunks
client = chromadb.PersistentClient(path=DOSSIER_BASE)
# Si la collection existe déjà (réindexation volontaire), on la remplace
if NOM_COLLECTION in [c.name for c in client.list_collections()]:
    client.delete_collection(NOM_COLLECTION)
collection = client.create_collection(
    name=NOM_COLLECTION,
    # On trace le nom du modèle DANS la base, comme exigé par le sujet :
    metadata={"modele_embedding": MODELE_EMBEDDING, "date_corpus": "2025-07-13"},
)
collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=textes,
    metadatas=metadonnees,
)
print(f"Base créée : {collection.count()} chunks dans {DOSSIER_BASE}/")