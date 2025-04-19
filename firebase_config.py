import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDWGnijH4CmZuzSiV9BSoobKELaEmn_4oo",
    "authDomain": "projet-pfe-ca585.firebaseapp.com",
    "projectId": "projet-pfe-ca585",
    "storageBucket": "projet-pfe-ca585.appspot.com",
    "messagingSenderId": "937368243752",
    "appId": "1:937368243752:web:5ff468552f23f20f07af1d",
    "measurementId": "G-ZN98296M98",
    "databaseURL": ""  # Laisse vide ou ajoute-le si tu l’as
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
