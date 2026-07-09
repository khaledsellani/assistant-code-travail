# Compte rendu — Assistant Code du travail

## Difficultés rencontrées
- Volume de la base LEGI (archive >1 Go, 1,5 M de fichiers) : résolu
  par une extraction en flux filtrée sur l'identifiant du Code du travail
- Lecture de la structure XML LEGI (versions multiples d'un même
  article) : résolu par le filtre ETAT=VIGUEUR

## Décisions de conception
- Chunk = un article, préfixé thème/section (Q1), validé par un jeu
  de 5 questions : 5/5 dans le top-5
- Numéro d'article en métadonnées ET dans le texte embeddé (Q2)
- Garde-fous hors LLM : avertissement, sources et date affichés par
  le code, pas par le modèle

## Avec plus de temps
- Historique de conversation envoyé au LLM : l'interface web affiche
  les échanges précédents mais chaque question reste traitée
  indépendamment. Une question de suivi ("et pour un CDD ?") n'est
  donc pas comprise. Il faudrait inclure les derniers échanges dans
  le prompt.