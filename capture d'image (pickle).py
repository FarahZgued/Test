import cv2
import os

name = "farah"  # Remplace par ton prénom ou identifiant
output_dir = f"dataset/{name}"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

cam = cv2.VideoCapture(0)
cv2.namedWindow("Capture tes photos (Appuie sur 's' pour sauvegarder, 'q' pour quitter)")

img_counter = 1
while True:
    ret, frame = cam.read()
    if not ret:
        print("Erreur lors de la capture.")
        break

    # Flip horizontal de l'image
    frame = cv2.flip(frame, 1)

    cv2.imshow("Capture tes photos (Appuie sur 's')", frame)
    key = cv2.waitKey(1)

    if key % 256 == ord('s'):
        # Enregistrer l’image
        img_name = f"{output_dir}/{img_counter}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"[INFO] Image sauvegardée : {img_name}")
        img_counter += 1

    elif key % 256 == ord('q'):
        print("[INFO] Fermeture de la capture.")
        break

cam.release()
cv2.destroyAllWindows()
