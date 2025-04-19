import firebase_admin
from firebase_admin import credentials, firestore
import face_recognition
import cv2
import imutils
import pickle
import time
from imutils.video import VideoStream
from imutils.video import FPS
from datetime import datetime

# Initialisation de Firebase
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")  # Remplace par ton fichier de clé
firebase_admin.initialize_app(cred)

# Initialisation de Firestore
db = firestore.client()

# Charger les visages et leurs encodages
print("[INFO] Loading encodings + face detector...")
data = pickle.loads(open("encodings.pickle", "rb").read())

# Initialisation du flux vidéo (src=0 pour la webcam par défaut)
print("[INFO] Starting video stream...")
vs = VideoStream(src=0, framerate=10).start()
time.sleep(2.0)

# Démarrer le compteur de FPS
fps = FPS().start()

# Variables pour stocker les dernières informations de pointage
last_logged_name = None
last_logged_time = time.time()

# Fonction pour calculer la différence de temps en heures et minutes
def calc_time_worked(entry_time, exit_time):
    # Convertir les chaînes de caractères en objets datetime
    entry_time = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
    exit_time = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S")
    
    # Calculer la différence entre l'heure d'entrée et l'heure de sortie
    time_worked = exit_time - entry_time
    
    # Convertir la différence en heures et minutes
    hours_worked = time_worked.seconds // 3600
    minutes_worked = (time_worked.seconds % 3600) // 60
    
    return hours_worked, minutes_worked

# Main loop
while True:
    # Lire une frame depuis le flux vidéo
    frame = vs.read()

    # Vérifier si la frame a été correctement lue
    if frame is None:
        print("[ERREUR] Impossible de lire une image depuis la caméra.")
        break

    # Redimensionner la frame pour accélérer le traitement
    frame = imutils.resize(frame, width=500)

    # Détecter les visages et calculer les encodages
    boxes = face_recognition.face_locations(frame)
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)

            if last_logged_name != name:
                last_logged_name = name
                print(f"Employé détecté: {name}")

        names.append(name)

        # === Enregistrer l'entrée ou la sortie ===
        if name == "Unknown":
            print("Visage inconnu détecté.")
        else:
            # Recherche de l'utilisateur dans la base de données
            utilisateur_ref = db.collection("utilisateurs").document(name)
            utilisateur = utilisateur_ref.get()

            # Si l'utilisateur n'existe pas, l'ajouter à Firebase
            if not utilisateur.exists:
                utilisateur_ref.set({
                    "autorisé": True,  # L'utilisateur est autorisé par défaut
                    "rôle": "employé"  # Rôle : employé ou admin
                })
                print(f"{name} ajouté à la base de données Firebase.")

            # Calcul de l'heure de pointage
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Enregistrer l'entrée ou la sortie de la personne
            if name != last_logged_name or (time.time() - last_logged_time > 5):  # Seulement si 5 secondes sont passées
                # Vérification si l'utilisateur a déjà une entrée enregistrée
                pointage_type = "Entrée"  # Par défaut, c'est une entrée

                # On cherche si l'utilisateur a déjà une entrée enregistrée
                pointage_ref = db.collection("pointage").where("nom", "==", name).order_by("date_heure", direction=firestore.Query.DESCENDING).limit(1).get()

                if pointage_ref:
                    last_pointage = pointage_ref[0].to_dict()
                    # Si l'utilisateur a une entrée, on le marque comme Sortie
                    if last_pointage["type"] == "Entrée":
                        pointage_type = "Sortie"

                        # Calculer les heures de travail (entrée + sortie)
                        entry_time = last_pointage["date_heure"]
                        exit_time = date_str
                        hours_worked, minutes_worked = calc_time_worked(entry_time, exit_time)
                        print(f"[INFO] Durée du travail de {name}: {hours_worked} heures et {minutes_worked} minutes.")

                # Enregistrement de l'événement dans Firestore
                db.collection("pointage").add({
                    "nom": name,
                    "date_heure": date_str,  # Garde le format tuple pour la date
                    "type": pointage_type  # Type d'action : Entrée ou Sortie
                })

                print(f"[✅] {name} enregistré à {date_str} - {pointage_type}")

                # Mettre à jour les dernières informations de pointage
                last_logged_name = name
                last_logged_time = time.time()

    # Dessiner les rectangles et les noms
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Afficher la frame
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    # Quitter la boucle lorsque 'q' est pressée
    if key == ord("q"):
        break

    # Mettre à jour le FPS
    fps.update()

# Nettoyage
fps.stop()
print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()
