"""Extrait les fichiers XML du Code du travail depuis l'archive LEGI."""

import tarfile

# Le chemin vers l'archive téléchargée
ARCHIVE = "data/Freemium_legi_global_20250713-140000.tar.gz"

# L'identifiant unique du Code du travail dans la base LEGI
CODE_TRAVAIL_ID = "LEGITEXT000006072050"

# Où déposer les fichiers extraits
DESTINATION = "data/"

compteur = 0

# On ouvre l'archive en mode "flux" (r|gz) : on la lit du début à la fin
# sans jamais la décompresser entièrement sur le disque
with tarfile.open(ARCHIVE, mode="r|gz") as archive:
    for membre in archive:                      # chaque "membre" = un fichier dans l'archive
        if CODE_TRAVAIL_ID in membre.name:      # son chemin contient-il l'ID du Code du travail ?
            archive.extract(membre, DESTINATION)  # oui -> on l'extrait dans data/
            compteur += 1
            if compteur % 1000 == 0:            # petit message tous les 1000 fichiers
                print(f"{compteur} fichiers extraits...")

print(f"Terminé ! {compteur} fichiers du Code du travail extraits dans {DESTINATION}")