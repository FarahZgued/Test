import cv2

cap = cv2.VideoCapture(0)  # essaie avec 1 ou 2 si 0 ne fonctionne pas

if not cap.isOpened():
    print("❌ Impossible d'ouvrir la caméra.")
else:
    print("✅ Caméra détectée.")
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    cap.release()
