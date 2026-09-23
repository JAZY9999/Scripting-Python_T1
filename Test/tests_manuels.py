import csv
import os
import pprint
import re
import sys
from datetime import datetime

COLONNES = ["login", "prénom", "nom", "mdp hashé", "email",
            "date de création", "date d'éxpiration", "groupe",
            "nom du poste", "site", "actif", "tentatives_echec",
            "derniere_connexion", "doit_changer_mdp"]

GROUPES_VALIDES = {"super_admin", "admin", "utilisateur"}
SITES_VALIDES = {"Paris", "Marseille", "Rennes", "Grenoble"}


def charger (chemin="data/utilisateurs.csv"):
    utilisateurs =  {}


    if not os.path.exists(chemin):
         with open (chemin, "w", newline="", encoding="utf-8-sig") as f:
              ecrivain = csv.writer(f, delimiter=";")
              ecrivain.writerow(COLONNES)


    try:
         with open (chemin, newline="", encoding="utf-8-sig") as f:
              lecteur = csv.DictReader(f, delimiter=";")
              for ligne in lecteur:
                   utilisateurs[ligne["login"]] = ligne
    except PermissionError:
         print(f"Erreur vous n'avez pas les droit nécessaire pour intéragire avec ce fichier {chemin}")
         sys.exit(1)
    except (UnicodeDecodeError,csv.Error):
         print("Erreur de syntaxe")
         sys.exit(1)
    return utilisateurs


def sauvegarder(utilisateurs, chemin="data/utilisateurs.csv"):
     fichier_temporaire = chemin + ".temp"

     with open (fichier_temporaire, "w", newline="", encoding="utf-8-sig") as f:
          ecrivain = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
          ecrivain.writeheader()
          for utilisateur in utilisateurs.values():
               ecrivain.writerow(utilisateur)
     os.replace(fichier_temporaire, chemin)


def trouver_par_login(login):
     return utilisateurs.get(login)


def login_existe(login):
     return login in utilisateurs


def valider_utilisateur(utilisateur):
     for champ in COLONNES:
          if not str(utilisateur.get(champ, "")).strip():
               raise ValueError(f"le champ {champ} est vide")

     if utilisateur["groupe"] not in GROUPES_VALIDES:
          raise ValueError(f"groupe invalide : {utilisateur['groupe']}")

     if utilisateur["site"] not in SITES_VALIDES:
          raise ValueError(f"site invalide : {utilisateur['site']}")

     try:
          date_creation = datetime.strptime(utilisateur["date de création"], "%Y-%m-%d")
          date_expiration = datetime.strptime(utilisateur["date d'éxpiration"], "%Y-%m-%d")
     except ValueError:
          raise ValueError("dates pas au bon format (AAAA-MM-JJ)")

     if date_expiration <= date_creation:
          raise ValueError("la date d'expiration doit etre apres la date de creation")

     # le mdp doit deja etre hashe par securite.py, on verifie juste que ca ressemble a un hash
     if not re.fullmatch(r"[0-9a-fA-F]{32,}", utilisateur["mdp hashé"]):
          raise ValueError("le mot de passe n'a pas l'air hashe, jamais de mdp en clair ici")


def ajouter(utilisateur):
     login = utilisateur.get("login")
     if login_existe(login):
          raise ValueError(f"le login {login} existe deja")
     valider_utilisateur(utilisateur)
     utilisateurs[login] = utilisateur
     sauvegarder(utilisateurs)


def remplacer(utilisateur):
     login = utilisateur.get("login")
     if not login_existe(login):
          raise ValueError(f"le login {login} n'existe pas")
     valider_utilisateur(utilisateur)
     utilisateurs[login] = utilisateur
     sauvegarder(utilisateurs)


def retirer(login):
     if not login_existe(login):
          raise ValueError(f"le login {login} n'existe pas")
     del utilisateurs[login]
     sauvegarder(utilisateurs)


utilisateurs = charger()
#utilisateurs["ynoiret"]["tentatives_echec"] = "5"
sauvegarder(utilisateurs)

utilisateurs_recharges = charger()
pprint.pprint(utilisateurs_recharges)


# test ajout d'un nouvel utilisateur
nouveau = {
    "login": "test1", "prénom": "Test", "nom": "Un",
    "mdp hashé": "a" * 40, "email": "test1@americanhospital.fr",
    "date de création": "2026-01-01", "date d'éxpiration": "2027-01-01",
    "groupe": "utilisateur", "nom du poste": "Testeur", "site": "Paris",
    "actif": "oui", "tentatives_echec": "0",
    "derniere_connexion": "2026-09-23", "doit_changer_mdp": "non",
}
ajouter(nouveau)
print("ajout ok ?", login_existe("test1"))

# test doublon, doit planter
try:
    ajouter(nouveau)
except ValueError as e:
    print("erreur normale (doublon) :", e)

# test mdp en clair, doit planter
mauvais = dict(nouveau)
mauvais["login"] = "test2"
mauvais["mdp hashé"] = "motdepasse123"
try:
    ajouter(mauvais)
except ValueError as e:
    print("erreur normale (mdp pas hashe) :", e)

# test remplacer
modifie = dict(nouveau)
modifie["nom du poste"] = "Testeur Senior"
remplacer(modifie)
print("poste modifie :", trouver_par_login("test1")["nom du poste"])

# test retirer
retirer("test1")
print("test1 encore la ?", login_existe("test1"))