import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("C:\Utilisateurs\farah\Téléchargements\firebase_key.json")
firebase_admin.initialize_app(cred)
print("Connexion à Firebase réussie ✅")
