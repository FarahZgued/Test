import tkinter as tk
from tkinter import ttk
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialisation Firebase
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")

  # ← Remplace par ton vrai chemin si nécessaire
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fonction d’envoi
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
    lire_donnees()  # Rafraîchir l'affichage

# Lecture des données depuis Firestore
def lire_donnees():
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

        if filtre_nom and filtre_nom not in nom:
            continue
        if filtre_date and not date_heure.startswith(filtre_date):
            continue

        tree.insert("", "end", values=(data["nom"], date_heure, type_p))

# Interface Tkinter
fenetre = tk.Tk()
fenetre.title("Système de pointage")
fenetre.geometry("700x500")

# Champ nom
tk.Label(fenetre, text="Nom de l'employé :").pack(pady=5)
champ_nom = tk.Entry(fenetre)
champ_nom.pack(pady=5)

# Boutons
frame_boutons = tk.Frame(fenetre)
frame_boutons.pack(pady=10)

btn_entree = tk.Button(frame_boutons, text="Entrée", bg="lightgreen", width=15, command=lambda: envoyer_pointage("entrée"))
btn_sortie = tk.Button(frame_boutons, text="Sortie", bg="lightblue", width=15, command=lambda: envoyer_pointage("sortie"))

btn_entree.grid(row=0, column=0, padx=10)
btn_sortie.grid(row=0, column=1, padx=10)

# Filtres
tk.Label(fenetre, text="Filtrer par nom :").pack()
champ_filtre_nom = tk.Entry(fenetre)
champ_filtre_nom.pack()

tk.Label(fenetre, text="Filtrer par date (YYYY-MM-DD) :").pack()
champ_filtre_date = tk.Entry(fenetre)
champ_filtre_date.pack()

tk.Button(fenetre, text="Rechercher", command=lire_donnees).pack(pady=5)

# Tableau
colonnes = ("Nom", "Date et heure", "Type")
tree = ttk.Treeview(fenetre, columns=colonnes, show="headings")
for col in colonnes:
    tree.heading(col, text=col)
    tree.column(col, width=200)

tree.pack(pady=10, fill=tk.BOTH, expand=True)

# Lancement
lire_donnees()
fenetre.mainloop()
