import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import mysql.connector
import hashlib
import os
import face_recognition
import datetime

# Fungsi untuk memeriksa login
def check_login(username, password):
    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mahasiswa"
        )
        cursor = db_connection.cursor()
        query = "SELECT password FROM mahasiswa_log WHERE nama = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        db_connection.close()

        if result is None:
            return False
        stored_password = result[0]
        hashed_input_password = hashlib.md5(password.encode()).hexdigest()
        return hashed_input_password == stored_password
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

# Fungsi untuk memuat wajah yang dikenal
def load_known_faces(directory="C:\\project3\\images"):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)

    return known_face_encodings, known_face_names

# Fungsi untuk mencatat absen
def rekap_absen(nama):
    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mahasiswa"
        )
        cursor = db_connection.cursor()
        tanggal = datetime.date.today()
        waktu = datetime.datetime.now().time()
        query = "INSERT INTO rekap_absen (nama, tanggal, waktu) VALUES (%s, %s, %s)"
        cursor.execute(query, (nama, tanggal, waktu))
        db_connection.commit()
        db_connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Fungsi untuk mendeteksi wajah
def detect_faces(frame):
    rgb_frame = frame[:, :, ::-1]  # Ubah dari BGR ke RGB
    face_locations = face_recognition.face_locations(rgb_frame)
    for top, right, bottom, left in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    return frame

# Fungsi untuk mendeteksi mata dan alis mata
def detect_eyes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return frame

# Fungsi untuk mendeteksi dan menampilkan gambar
def detect_and_show():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    known_face_encodings, known_face_names = load_known_faces("C:\\project3\\images")

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame ke format RGB
            frame = detect_faces(frame)  # Deteksi wajah
            frame = detect_eyes(frame)  # Deteksi mata dan alis mata
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.config(image=imgtk)
            detect_and_recognize_face(frame, known_face_encodings, known_face_names)  # Mendeteksi dan mengenali wajah
            camera_label.after(10, update_frame)

    update_frame()

# Fungsi untuk mendeteksi dan mengenali wajah
def detect_and_recognize_face(frame, known_face_encodings, known_face_names):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

            # Hitung presentase kecocokan
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                best_name = known_face_names[best_match_index]
                best_distance = face_distances[best_match_index]
                percentage = (1 - best_distance) * 100
                messagebox.showinfo("Pengenalan Wajah", f"Wajah terdeteksi: {best_name}, Persentase: {percentage:.2f}%")
                rekap_absen(best_name)  # Catat absen
                show_absen_gui()  # Tampilkan GUI absen

# Fungsi untuk menangani login
def handle_login():
    username = entry_username.get()
    password = entry_password.get()
    if check_login(username, password):
        messagebox.showinfo("Login Success", "Login berhasil!")
        show_camera_with_background()
    else:
        messagebox.showerror("Login Failed", "Username atau password salah.")

# Fungsi untuk menampilkan kamera dengan latar belakang gambar
def show_camera_with_background():
    try:
        # Path ke file gambar
        image_path = "Gambar.png"
        # Buka gambar
        image = Image.open(image_path)
        image = image.resize((640, 480)) 
        photo = ImageTk.PhotoImage(image)
        # Tampilkan gambar di label sebagai latar belakang
        background_label = tk.Label(root, image=photo)
        background_label.image = photo  # Simpan referensi gambar
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Tampilkan frame dari kamera di atas latar belakang
        global camera_label
        camera_label = tk.Label(root)
        camera_label.place(x=0, y=0, relwidth=1, relheight=1)

        detect_and_show()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menampilkan gambar: {e}")

# Fungsi untuk menampilkan GUI absen harian
def show_absen_gui():
    absen_window = tk.Toplevel()
    absen_window.title("Absen Harian")
    absen_window.geometry("300x200")

    tk.Label(absen_window, text="Absen Harian", font=('Helvetica', 16)).pack(pady=20)
    tk.Label(absen_window, text="Absen telah berhasil!", font=('Helvetica', 12)).pack(pady=10)
    btn_close = tk.Button(absen_window, text="Tutup", command=absen_window.destroy)
    btn_close.pack(pady=20)


# Buat jendela utama
root = tk.Tk()
root.title("Aplikasi Pengenalan Wajah")
root.geometry("640x508")

# Logo kampus
logo_image = Image.open("Logo.png")
logo_image = logo_image.resize((150, 150))
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(root, image=logo_photo)
logo_label.pack(pady=10)

# Form login
frame_login = tk.Frame(root)
frame_login.pack(pady=10)

label_username = tk.Label(frame_login, text="Username")
label_username.grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame_login)
entry_username.grid(row=0, column=1, padx=5, pady=5)

label_password = tk.Label(frame_login, text="Password")
label_password.grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame_login, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# Tombol login
login_button = tk.Button(root, text="Login", command=handle_login)
login_button.pack(pady=10)

# Bind tombol Enter ke fungsi handle_login
root.bind('<Return>', lambda event: handle_login())

# Mulai loop utama
root.mainloop()
