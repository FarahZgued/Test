import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialiser Firebase
chemin_vers_cle_json = "C:/Users/farah/OneDrive/Bureau/facial_recognition-main/facial_recognition-main/projet-pfe-ca585-firebase-adminsdk-fbsvc-cb203e9b55.json"
cred = credentials.Certificate(chemin_vers_cle_json)
firebase_admin.initialize_app(cred)

# Accès à Firestore
db = firestore.client()

# Identifiant de l'employé (par exemple, cela viendrait de ta détection faciale)
id_employe = "EMP001"  # à remplacer par l'ID de l'employé détecté

# Vérifier si l'employé a déjà enregistré une "entrée"
pointages_ref = db.collection("pointage")
pointage_exist = pointages_ref.where("id_employe", "==", id_employe).order_by("date_heure", direction=firestore.Query.DESCENDING).limit(1).stream()

# Si l'employé n'a pas encore de pointage, c'est son "entrée"
try:
    dernier_pointage = next(pointage_exist)  # Si on trouve un pointage existant
    type_pointage = "sortie"  # Si un pointage existe déjà, on suppose que c'est une "sortie"
except StopIteration:
    type_pointage = "entrée"  # Si aucune entrée n'existe, c'est une "entrée"

# Ajouter le pointage avec le type calculé
donnee_pointage = {
    "nom": "farah zgued",
    "id_employe": id_employe,
    "date_heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "type": type_pointage
}

# Envoi dans Firestore
db.collection("pointage").add(donnee_pointage)
print(f"✅ Pointage ajouté avec succès pour {id_employe} ({type_pointage})!")
