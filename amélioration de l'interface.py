import tkinter as tk
from tkinter import ttk
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import auth  # Pyrebase auth

# --- Firebase Admin Init (pour Firestore) ---
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Fenêtre principale ---
fenetre = tk.Tk()
fenetre.title("Système de pointage")
fenetre.geometry("700x500")

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
tk.Button(frame_boutons, text="Entrée", bg="lightgreen", width=15, command=lambda: envoyer_pointage("entrée")).grid(row=0, column=0, padx=10)
tk.Button(frame_boutons, text="Sortie", bg="lightblue", width=15, command=lambda: envoyer_pointage("sortie")).grid(row=0, column=1, padx=10)

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

# --- Variables globales ---
utilisateur_email = ""
admin_courant = False

def changer_frame(frame):
    frame_accueil.pack_forget()
    frame_login.pack_forget()
    frame_pointage.pack_forget()
    frame.pack(fill="both", expand=True)

def ouvrir_login(role):
    changer_frame(frame_login)

def verifier_login():
    global utilisateur_email, admin_courant
    email = entry_email.get()
    mdp = entry_mdp.get()
    try:
        user = auth.sign_in_with_email_and_password(email, mdp)
        utilisateur_email = email
        admin_courant = "admin" in email
        changer_frame(frame_pointage)
        lire_donnees(admin_courant)
    except:
        label_erreur.config(text="Email ou mot de passe incorrect.")

def envoyer_pointage(type_pointage):
    nom = champ_nom.get()
    if nom.strip() == "":
        return
    now = datetime.now()
    donnees = {
        "nom": nom,
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
        if not admin and nom != utilisateur_email.split("@")[0].lower():
            continue
        if filtre_nom and filtre_nom not in nom:
            continue
        if filtre_date and not date_heure.startswith(filtre_date):
            continue
        tree.insert("", "end", values=(data["nom"], date_heure, type_p))

# Lancement
changer_frame(frame_accueil)
fenetre.mainloop()
