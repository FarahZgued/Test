import cv2
import face_recognition
import datetime
import firebase_admin
from firebase_admin import credentials, storage

# Initialise Firebase avec les bons paramètres
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")  # ← ton chemin
firebase_admin.initialize_app(cred, {
    'storageBucket': 'projet-pfe-ca585.appspot.com'  # ✅ CORRIGÉ ICI
})

# Capture de la caméra
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
if not ret:
    print("Erreur de capture")
    cap.release()
    exit()

# Convertir en RGB
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Détection du visage
face_locations = face_recognition.face_locations(rgb)

if face_locations:
    top, right, bottom, left = face_locations[0]  # premier visage détecté
    face_image = frame[top:bottom, left:right]

    # Nom du fichier basé sur l'heure actuelle
    now = datetime.datetime.now()
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}.jpg"

    # Sauvegarde locale
    cv2.imwrite(filename, face_image)

    # Envoi vers Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"photos/{filename}")  # dossier "photos" dans Firebase
    blob.upload_from_filename(filename)

    print(f"✅ Image envoyée à Firebase Storage : photos/{filename}")
else:
    print("❌ Aucun visage détecté.")

cap.release()
cv2.destroyAllWindows()
