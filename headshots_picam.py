import cv2

# Ouvre la caméra (src=0 pour la caméra par défaut)
camera = cv2.VideoCapture(0)

while True:
    # Capture un cadre de la caméra
    ret, frame = camera.read()

    if not ret:
        print("Impossible de lire la caméra")
        break

    # Affiche l'image capturée
    cv2.imshow("Frame", frame)

    # Si la touche 'q' est pressée, quitte la boucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libère la caméra et ferme les fenêtres ouvertes
camera.release()
cv2.destroyAllWindows()
