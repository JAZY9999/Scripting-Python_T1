import csv
import os
import pprint


COLONNES = ["login", "prénom", "nom", "mdp hashé", "email",
            "date de création", "date d'éxpiration", "groupe",
            "nom du poste", "site", "actif", "tentatives_echec",
            "derniere_connexion", "doit_changer_mdp"]


def charger (chemin="data/utilisateurs.csv"):
    utilisateurs =  {}


    if not os.path.exists(chemin):
         with open (chemin, "w", newline="", encoding="utf-8-sig") as f:
              ecrivain = csv.writer(f, delimiter=";")
              ecrivain.writerow(COLONNES)


    with open (chemin, newline="", encoding="utf-8-sig") as f:
               lecteur = csv.DictReader(f, delimiter=";")
               for ligne in lecteur:
                utilisateurs[ligne["login"]] = ligne
    return utilisateurs


















pprint.pprint(charger())