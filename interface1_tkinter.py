import tkinter as tk
from tkinter import ttk, messagebox
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime

# 🔐 Connexion Firebase
cred = credentials.Certificate("C:/Users/farah/Downloads/firebase_key.json")
initialize_app(cred)
db = firestore.client()

# 🖼️ Fenêtre principale
fenetre = tk.Tk()
fenetre.title("Historique de pointage")
fenetre.geometry("750x500")

# 🔎 Zone de filtre
frame_filtres = tk.Frame(fenetre)
frame_filtres.pack(pady=10)

# Champ Nom
tk.Label(frame_filtres, text="Nom:").grid(row=0, column=0, padx=5)
entry_nom = tk.Entry(frame_filtres)
entry_nom.grid(row=0, column=1, padx=5)

# Champ Date
tk.Label(frame_filtres, text="Date (AAAA-MM-JJ):").grid(row=0, column=2, padx=5)
entry_date = tk.Entry(frame_filtres)
entry_date.grid(row=0, column=3, padx=5)

# 🗂️ Frame du tableau + Scrollbar
frame_tableau = tk.Frame(fenetre)
frame_tableau.pack(fill="both", expand=True, padx=10, pady=10)

# Scrollbar verticale
scrollbar = tk.Scrollbar(frame_tableau)
scrollbar.pack(side="right", fill="y")

# Tableau (Treeview)
tree = ttk.Treeview(frame_tableau, columns=("Nom", "Date/Heure", "Type"), show="headings", yscrollcommand=scrollbar.set)
tree.heading("Nom", text="Nom")
tree.heading("Date/Heure", text="Date/Heure")
tree.heading("Type", text="Type")
tree.pack(expand=True, fill="both")
scrollbar.config(command=tree.yview)

# 📌 Afficher toutes les données
def lire_donnees():
    tree.delete(*tree.get_children())
    try:
        docs = db.collection("pointage").stream()
        for doc in docs:
            data = doc.to_dict()
            nom = data.get("nom", "—")
            date_heure = data.get("date_heure", "—")
            type_pointage = data.get("type", "—")
            tree.insert("", "end", values=(nom, date_heure, type_pointage))
        # Nettoyage des filtres
        entry_nom.delete(0, tk.END)
        entry_date.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer les données :\n{e}")

# 🔍 Appliquer les filtres
def filtrer():
    nom_filtre = entry_nom.get().strip().lower()
    date_filtre = entry_date.get().strip()
    tree.delete(*tree.get_children())

    try:
        docs = db.collection("pointage").stream()
        for doc in docs:
            data = doc.to_dict()
            nom = data.get("nom", "").lower()
            date_heure = data.get("date_heure", "")
            type_pointage = data.get("type", "—")

            # Extraire la date
            date_extrait = date_heure.split(" ")[0] if " " in date_heure else ""

            if (not nom_filtre or nom_filtre in nom) and (not date_filtre or date_filtre == date_extrait):
                tree.insert("", "end", values=(data.get("nom", "—"), date_heure, type_pointage))

        if not tree.get_children():
            messagebox.showinfo("Aucun résultat", "Aucune donnée ne correspond aux filtres.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur de filtrage :\n{e}")

# 🔘 Boutons
frame_boutons = tk.Frame(fenetre)
frame_boutons.pack(pady=5)

tk.Button(frame_boutons, text="Afficher tout", command=lire_donnees).pack(side="left", padx=5)
tk.Button(frame_boutons, text="Filtrer", command=filtrer).pack(side="left", padx=5)
tk.Button(frame_boutons, text="Actualiser", command=lire_donnees).pack(side="left", padx=5)

# 🔄 Charger automatiquement les données au démarrage
lire_donnees()

# 🔁 Lancement de l'interface
fenetre.mainloop()
