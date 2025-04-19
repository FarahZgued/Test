import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 👉 Remplace ceci par le chemin exact vers ta clé JSON
# Exemple : "controle-acces-firebase-adminsdk-abcde.json"
chemin_vers_cle_json ="C:/Users/farah/OneDrive/Bureau/facial_recognition-main/facial_recognition-main/projet-pfe-ca585-firebase-adminsdk-fbsvc-cb203e9b55.json"

# 🔐 Initialiser Firebase avec la clé
cred = credentials.Certificate(chemin_vers_cle_json)
firebase_admin.initialize_app(cred)

# 🔥 Connexion à Firestore
db = firestore.client()

# 🧪 Envoi d'une donnée test
donnee_test = {
    "nom": "Test Employé",
    "type": "entrée",
    "timestamp": datetime.now().isoformat()
}

# 👉 Enregistrer dans la collection "pointage"
db.collection("pointage").add(donnee_test)

print("✅ Donnée envoyée avec succès à Firebase !")
