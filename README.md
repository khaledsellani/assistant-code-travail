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