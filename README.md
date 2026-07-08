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