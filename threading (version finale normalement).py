import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import auth  # Pyrebase auth
import face_recognition
import cv2
import pickle
from PIL import Image, ImageTk

# --- Initialisation Firebase ---
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Chargement des encodages de visages ---
encodingsP = "encodings.pickle"
data = pickle.loads(open(encodingsP, "rb").read())

# --- Variables globales ---
utilisateur_email = ""
utilisateur_nom = ""
admin_courant = False
last_actions = {}  # Dictionnaire pour suivre l'état de chaque personne (Entrée ou Sortie)
webcam_window = None
webcam_label = None

# --- Fenêtre principale ---
fenetre = tk.Tk()
fenetre.title("Système de pointage")
fenetre.geometry("900x600")

# --- Frames ---
frame_accueil = tk.Frame(fenetre)
frame_login = tk.Frame(fenetre)
frame_pointage = tk.Frame(fenetre)

# --- Accueil ---
tk.Label(frame_accueil, text="Bienvenue", font=("Helvetica", 18)).pack(pady=30)
tk.Button(frame_accueil, text="Administrateur", width=20, command=lambda: ouvrir_login("admin")).pack(pady=10)
tk.Button(frame_accueil, text="Utilisateur", width=20, command=lambda: ouvrir_login("user")).pack(pady=10)
frame_accueil.pack(fill="both", expand=True)

# --- Login ---
tk.Label(frame_login, text="Connexion", font=("Helvetica", 16)).pack(pady=20)
tk.Label(frame_login, text="Email :").pack()
entry_email = tk.Entry(frame_login)
entry_email.pack(pady=5)
tk.Label(frame_login, text="Mot de passe :").pack()
entry_mdp = tk.Entry(frame_login, show="*")
entry_mdp.pack(pady=5)
label_erreur = tk.Label(frame_login, text="", fg="red")
label_erreur.pack()
tk.Button(frame_login, text="Se connecter", command=lambda: verifier_login()).pack(pady=15)
tk.Button(frame_login, text="Retour", command=lambda: changer_frame(frame_accueil)).pack()

# --- Pointage ---
tk.Label(frame_pointage, text="Nom de l'employé :").pack(pady=5)
champ_nom = tk.Entry(frame_pointage)
champ_nom.pack(pady=5)
frame_boutons = tk.Frame(frame_pointage)
frame_boutons.pack(pady=10)
tk.Button(frame_boutons, text="Entrée", bg="lightgreen", width=15, command=lambda: envoyer_pointage("Entrée")).grid(row=0, column=0, padx=10)
tk.Button(frame_boutons, text="Sortie", bg="lightblue", width=15, command=lambda: envoyer_pointage("Sortie")).grid(row=0, column=1, padx=10)

# Filtres
tk.Label(frame_pointage, text="Filtrer par nom :").pack()
champ_filtre_nom = tk.Entry(frame_pointage)
champ_filtre_nom.pack()
tk.Label(frame_pointage, text="Filtrer par date (YYYY-MM-DD) :").pack()
champ_filtre_date = tk.Entry(frame_pointage)
champ_filtre_date.pack()
tk.Button(frame_pointage, text="Rechercher", command=lambda: lire_donnees(admin_courant)).pack(pady=5)

# Tableau
colonnes = ("Nom", "Date et heure", "Type")
tree = ttk.Treeview(frame_pointage, columns=colonnes, show="headings")
for col in colonnes:
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(pady=10, fill=tk.BOTH, expand=True)

# --- Fonctions ---
def changer_frame(frame):
    frame_accueil.pack_forget()
    frame_login.pack_forget()
    frame_pointage.pack_forget()
    frame.pack(fill="both", expand=True)

def ouvrir_login(role):
    changer_frame(frame_login)

def verifier_login():
    global utilisateur_email, utilisateur_nom, admin_courant
    email = entry_email.get()
    mdp = entry_mdp.get()
    try:
        user = auth.sign_in_with_email_and_password(email, mdp)
        utilisateur_email = email
        utilisateur_nom = email.split("@")[0].lower()
        admin_courant = "admin" in email
        champ_nom.delete(0, tk.END)
        champ_nom.insert(0, utilisateur_nom)
        changer_frame(frame_pointage)
        lire_donnees(admin_courant)
        ouvrir_fenetre_webcam()
    except:
        label_erreur.config(text="Email ou mot de passe incorrect.")

def envoyer_pointage(type_pointage):
    nom = champ_nom.get()
    if nom.strip() == "":
        return
    now = datetime.now()
    donnees = {
        "nom": nom.lower(),
        "date_heure": now.strftime("%Y-%m-%d %H:%M:%S"),
        "type": type_pointage
    }
    db.collection("pointage").add(donnees)
    lire_donnees(admin_courant)

def lire_donnees(admin=False):
    for item in tree.get_children():
        tree.delete(item)
    filtre_nom = champ_filtre_nom.get().lower()
    filtre_date = champ_filtre_date.get()
    docs = db.collection("pointage").order_by("date_heure").stream()
    for doc in docs:
        data = doc.to_dict()
        nom = data.get("nom", "").lower()
        date_heure = data.get("date_heure", "")
        type_p = data.get("type", "")
        if not admin and nom != utilisateur_nom:
            continue
        if filtre_nom and filtre_nom not in nom:
            continue
        if filtre_date and not date_heure.startswith(filtre_date):
            continue
        tree.insert("", "end", values=(data["nom"], date_heure, type_p))

def ouvrir_fenetre_webcam():
    global webcam_window, webcam_label
    if webcam_window and tk.Toplevel.winfo_exists(webcam_window):
        return
    webcam_window = tk.Toplevel()
    webcam_window.title("Caméra - Reconnaissance faciale")
    webcam_window.geometry("520x350")
    webcam_label = tk.Label(webcam_window)
    webcam_label.pack()
    threading.Thread(target=afficher_webcam, daemon=True).start()

def afficher_webcam():
    vs = cv2.VideoCapture(0)
    currently_visible = set()

    def get_last_action(name):
        return last_actions.get(name, "Sortie")

    def update():
        nonlocal currently_visible
        if not vs.isOpened() or not webcam_label.winfo_exists():
            return
        ret, frame = vs.read()
        if not ret:
            return
        rgb = cv2.cvtColor(cv2.resize(frame, (500, 300)), cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        new_visible = set()
        maj_effectuee = False  # <-- Nouvelle variable pour éviter les appels inutiles

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
            new_visible.add(name)
            if name != "Unknown" and name not in currently_visible:
                now = datetime.now()
                current_action = get_last_action(name)
                new_action = "Entrée" if current_action == "Sortie" else "Sortie"
                last_actions[name] = new_action
                db.collection("pointage").add({
                    "nom": name,
                    "date_heure": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": new_action
                })
                lire_donnees(admin_courant)
                print(f"[✅] {name} détecté à {now.strftime('%H:%M:%S')} → {new_action}")
                maj_effectuee = True  # Marque qu’une mise à jour est nécessaire

        if maj_effectuee:
            fenetre.after(0, lire_donnees, admin_courant)  # Actualise automatiquement l’interface

        currently_visible = new_visible

        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(rgb, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(rgb, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
        webcam_label.imgtk = imgtk
        webcam_label.configure(image=imgtk)
        webcam_label.after(10, update)

    update()


# --- Lancement ---
changer_frame(frame_accueil)
fenetre.mainloop()
