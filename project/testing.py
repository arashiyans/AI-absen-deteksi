import cv2

# Load Haar Cascade Classifier untuk mata dan wajah
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
eyebrow_cascade = cv2.CascadeClassifier('C:\project')  #classifier percobaan

# Fungsi untuk mendeteksi dan menggambar persegi di sekitar mata dan alis
def detect_and_display(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        
        eyebrows = eyebrow_cascade.detectMultiScale(roi_gray)
        for (bx, by, bw, bh) in eyebrows:
            cv2.rectangle(roi_color, (bx, by), (bx+bw, by+bh), (0, 0, 255), 2)
    
    return frame

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_and_display(frame)
    
    cv2.imshow('Eye and Eyebrow Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
