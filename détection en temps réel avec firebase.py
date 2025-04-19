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

# === Initialisation Firebase ===
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# === Chargement des encodages ===0
encodingsP = "encodings.pickle"
print("[INFO] Loading encodings...")
data = pickle.loads(open(encodingsP, "rb").read())

# === Démarrage du flux vidéo ===
print("[INFO] Starting video stream...")
vs = VideoStream(src=0, framerate=10).start()
time.sleep(2.0)
fps = FPS().start()

# === Variable pour éviter les doublons immédiats ===
last_detected_name = None

while True:
    frame = vs.read()
    if frame is None:
        print("[ERREUR] Impossible de lire une image depuis la caméra.")
        break

    frame = imutils.resize(frame, width=500)
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

        names.append(name)

        if name == "Unknown":
            print("Visage inconnu détecté.")
        else:
            utilisateur_ref = db.collection("utilisateurs").document(name)
            utilisateur = utilisateur_ref.get()

            if not utilisateur.exists:
                utilisateur_ref.set({
                    "autorisé": True,
                    "rôle": "employé",
                    "dernier_type": "Sortie"  # Pour que le premier enregistrement soit "Entrée"
                })
                print(f"{name} ajouté à Firebase.")

            # Ne pas enregistrer si c'est encore la même personne en boucle
            if name != last_detected_name:
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d %H:%M:%S")

                # Lire le dernier type depuis Firestore
                dernier_type = utilisateur.to_dict().get("dernier_type", "Sortie")
                nouveau_type = "Entrée" if dernier_type == "Sortie" else "Sortie"

                # Enregistrement du pointage
                db.collection("pointage").add({
                    "nom": name,
                    "date_heure": date_str,
                    "type": nouveau_type
                })

                print(f"[✅] {name} enregistré à {date_str} - {nouveau_type}")

                # Mise à jour du dernier type
                utilisateur_ref.update({
                    "dernier_type": nouveau_type
                })

                last_detected_name = name

    # === Affichage vidéo avec noms ===
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        print("[INFO] Fin du programme.")
        break

    fps.update()

# === Nettoyage ===
fps.stop()
print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()
