# Assistant Code du travail (RAG)

Projet M2 MD5 — Assistant juridique répondant aux questions
sur le droit du travail français avec citation des articles.

## Constitution du corpus (option B)

Le corpus est extrait de la base LEGI officielle (archive
`Freemium_legi_global_20250713` téléchargée sur echanges.dila.gouv.fr,
référencée sur data.gouv.fr), au format XML.

Pipeline de préparation :
1. `extraire_code_travail.py` : extrait de l'archive les 59 755 fichiers
   du Code du travail (identifiant LEGITEXT000006072050).
2. `preparer_corpus.py` : parcourt les 41 815 fichiers d'articles, ne
   conserve que les versions en vigueur (balise ETAT = VIGUEUR),
   appartenant aux thèmes du projet, nettoie le texte (suppression des
   balises HTML via itertext, normalisation des espaces) et produit
   `data/corpus.json` : 592 articles, 7 thèmes, avec métadonnées
   (numéro, thème, section, date d'entrée en vigueur, source).
3. `controle_qualite.py` : relecture de 10 articles aléatoires.

## Questions de réflexion

### Q3 — Fraîcheur du corpus

Le droit du travail évolue en permanence. Notre corpus est figé à la
date de l'archive LEGI : le 13 juillet 2025. Cette date est stockée
dans le champ `source` de chaque document, et sera rappelée dans
chaque réponse de l'assistant afin que l'utilisateur sache que les
évolutions postérieures (lois, ordonnances) ne sont pas prises en
compte. L'avertissement invite à vérifier sur legifrance.gouv.fr pour
toute disposition récente. Pour mettre à jour le corpus, il suffit de
télécharger une archive LEGI plus récente et de relancer le pipeline.


### Q1 — Granularité du chunking

Un chunk = un article. Les articles du Code du travail sont courts et
autonomes, c'est la découpe naturelle. Ça donne une recherche précise
et une citation directe : le chunk trouvé est l'article à citer.
Regrouper par section garderait plus de contexte, mais les chunks
seraient longs, la recherche moins précise, et on ne saurait pas quel
article citer dans le lot.

On ajoute quand même un peu d'hybride : le texte embeddé est préfixé
du thème et de la section de l'article. Ça redonne du contexte sans
perdre la précision. Par contre les renvois entre articles ("au sens
de l'article L. 1234-5") ne sont pas gérés. En pratique le top-k
ramène souvent les articles voisins ensemble, donc ça limite le
problème.


### Q2 — Traçabilité du numéro d'article

Le numéro est stocké aux deux endroits. En métadonnées pour avoir une
version fiable qu'on affiche à l'utilisateur. Dans le texte embeddé
pour qu'une question du genre "que dit L3121-1 ?" puisse matcher.

Pour éviter que le LLM invente des numéros : chaque chunk du prompt
est présenté comme "[Article L3121-1] texte...", le numéro venant des
métadonnées, et le prompt interdit de citer un numéro absent du
contexte. Surtout, le code affiche lui-même la liste des articles
sources depuis les métadonnées, sans dépendre de ce que le LLM écrit.



### Q4 — Réponses conditionnelles

Beaucoup de réponses dépendent de la taille de l'entreprise ou de la
convention collective. En ligne de commande, poser des questions de
clarification alourdit vite l'échange. On choisit donc la réponse
générale assortie de réserves : le prompt demande au LLM de signaler
explicitement quand une règle varie (effectif, convention collective)
et de donner la règle générale du Code avec ses conditions.


### Q5 — Frontière du conseil juridique

Une question d'information ("combien de jours de congés ?") a sa
réponse dans le Code : on répond en citant. Une question
d'interprétation ("mon licenciement est-il abusif ?") demande
d'appliquer le droit à un cas personnel : c'est du conseil juridique.
Le prompt demande au LLM de donner les règles générales qui
s'appliquent, sans se prononcer sur le cas de la personne, et de
renvoyer vers un avocat ou l'inspection du travail. L'avertissement
juridique est de toute façon ajouté par le code à chaque réponse.



## Installation

```bash
git clone https://github.com/khaledsellani/assistant-code-travail.git
cd assistant-code-travail
python -m venv venv
venv\Scripts\activate        # Windows (source venv/bin/activate sous Linux/Mac)
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine sur le modèle de `.env.example`,
avec une clé API Groq (gratuite sur console.groq.com).

## Construction de la base (une seule fois)

1. Télécharger l'archive LEGI `Freemium_legi_global_*.tar.gz` depuis
   echanges.dila.gouv.fr/OPENDATA/LEGI/ et la placer dans `data/`
   (adapter le nom du fichier dans `extraire_code_travail.py`).
2. `python extraire_code_travail.py` — extrait le Code du travail
3. `python preparer_corpus.py` — produit `data/corpus.json`
4. `python indexer.py` — construit la base vectorielle `chroma_db/`

## Lancement

```bash
python assistant.py
```

La base est rechargée depuis le disque sans réindexation.
Scripts de vérification : `controle_qualite.py` (relecture du corpus),
`evaluer_retrieval.py` (5 questions de référence, score 5/5).


## Amélioration (jalon 6) : score de confiance

Le seuil a été calibré en comparant la distance du meilleur chunk sur
5 questions du domaine (7,5 à 17,4) et 5 questions hors domaine (18,6
à 33,5). Seuil retenu : 18,0. Une question du domaine formulée très
familièrement ("Le CDD peut-il être renouvelé ?", 17,4) montre que la
frontière est étroite : l'alerte n'est donc pas bloquante, elle
signale seulement une confiance faible. Les distances sont affichées
à côté de chaque article source.