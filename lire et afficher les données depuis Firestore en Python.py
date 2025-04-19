import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
# Remplace le chemin par celui de ta clé JSON Firebase
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")

firebase_admin.initialize_app(cred)

# Initialiser Firestore
db = firestore.client()
# Récupérer toutes les données de la collection 'pointage'
pointages_ref = db.collection("pointage")
docs = pointages_ref.stream()

# Afficher chaque pointage
for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
# Récupérer les pointages d'une journée spécifique
jour_specifique = "2025-04-06"  # Par exemple, format 'YYYY-MM-DD'
pointages_par_jour = pointages_ref.where("date", "==", jour_specifique).stream()

print(f"Pointages pour le {jour_specifique} :")
for doc in pointages_par_jour:
    print(f"{doc.id} => {doc.to_dict()}")
# Filtrer par nom d'employé
nom_employe = "Farah"
pointages_par_employe = pointages_ref.where("nom", "==", nom_employe).stream()

print(f"Pointages pour {nom_employe} :")
for doc in pointages_par_employe:
    print(f"{doc.id} => {doc.to_dict()}")
# Exemple : Filtrer par date et afficher les pointages
def afficher_pointages(par_jour=None, par_employe=None):
    pointages_ref = db.collection("pointage")
    
    if par_jour:
        pointages_ref = pointages_ref.where("date", "==", par_jour)
    if par_employe:
        pointages_ref = pointages_ref.where("nom", "==", par_employe)
    
    pointages = pointages_ref.stream()
    
    for doc in pointages:
        print(f"{doc.id} => {doc.to_dict()}")

# Exemple d'utilisation :
# Afficher tout l'historique
afficher_pointages()

# Afficher pointages pour un jour spécifique
afficher_pointages(par_jour="2025-04-06")

# Afficher pointages pour un employé spécifique
afficher_pointages(par_employe="Farah")
