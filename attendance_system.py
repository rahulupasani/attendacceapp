import cv2
import sqlite3
import json
import datetime
import pandas as pd
import numpy as np
from deepface import DeepFace
import customtkinter as ctk  # Improved GUI library
from tkinter import messagebox
from mtcnn import MTCNN
from numpy.linalg import norm
import os

# ✅ Initialize database
conn = sqlite3.connect('attendance_system.db', check_same_thread=False)
cursor = conn.cursor()

# ✅ Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    encoding TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER, 
                    name TEXT, 
                    date TEXT, 
                    in_time TEXT, 
                    out_time TEXT,
                    UNIQUE(id, date))''')

conn.commit()

# ✅ Function to compare face encodings using Cosine Similarity
def is_face_registered(new_encoding):
    cursor.execute("SELECT id, encoding FROM faces")
    rows = cursor.fetchall()

    for row in rows:
        stored_encoding = json.loads(row[1])  # Convert stored JSON string back to list
        cosine_distance = np.dot(stored_encoding, new_encoding) / (norm(stored_encoding) * norm(new_encoding))  # Cosine similarity
        
        if cosine_distance > 0.6:  # Closer to 1 = better match
            return row[0]  # Return registered face ID

    return None  # No match found

# ✅ MTCNN-based Face Detection
def detect_faces(frame):
    detector = MTCNN()
    faces = detector.detect_faces(frame)

    if faces:
        x, y, w, h = faces[0]['box']
        return [(x, y, w, h)]
    return []

# ✅ Function to register a new face
def register_face():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = detect_faces(frame)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            encoding = DeepFace.represent(face, model_name='VGG-Face', enforce_detection=False)[0]['embedding']

            if is_face_registered(encoding):
                messagebox.showwarning("Warning", "⚠ Face already registered! Try marking attendance instead.")
                cap.release()
                return

            name = ctk.CTkInputDialog(text="Enter your name for registration:", title="Face Registration").get_input()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty!")
                cap.release()
                return

            encoding_str = json.dumps(encoding)  # Store encoding as JSON string
            cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, encoding_str))
            conn.commit()
            messagebox.showinfo("Success", f"✅ {name} registered successfully!")

            cap.release()
            return

        cv2.imshow('Register Face', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ✅ Function to mark attendance
def mark_attendance():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = detect_faces(frame)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            encoding = DeepFace.represent(face, model_name='VGG-Face', enforce_detection=False)[0]['embedding']
            face_id = is_face_registered(encoding)

            if face_id is None:
                messagebox.showerror("Error", "⚠ Face not recognized! Please register first.")
                cap.release()
                return

            cursor.execute("SELECT name FROM faces WHERE id = ?", (face_id,))
            name = cursor.fetchone()[0]

            today = datetime.date.today().strftime('%Y-%m-%d')
            current_time = datetime.datetime.now().strftime('%H:%M:%S')

            cursor.execute("SELECT in_time, out_time FROM attendance WHERE id = ? AND date = ?", (face_id, today))
            record = cursor.fetchone()

            if record is None:
                cursor.execute("INSERT INTO attendance (id, name, date, in_time, out_time) VALUES (?, ?, ?, ?, ?)",
                               (face_id, name, today, current_time, None))
                conn.commit()
                messagebox.showinfo("Success", f"✅ Attendance marked for {name} as 'IN' at {current_time}.")
            
            elif record[0] is not None and record[1] is None:
                cursor.execute("UPDATE attendance SET out_time = ? WHERE id = ? AND date = ?",
                               (current_time, face_id, today))
                conn.commit()
                messagebox.showinfo("Success", f"✅ Attendance marked for {name} as 'OUT' at {current_time}.")
            
            else:
                messagebox.showwarning("Warning", "⚠ Attendance already recorded for today!")

            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow('Mark Attendance', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ✅ Function to clear the database
def clear_database():
    confirmation = messagebox.askquestion("Confirm", "⚠ This will DELETE ALL data! Continue?")
    if confirmation == "yes":
        cursor.execute("DELETE FROM faces")
        cursor.execute("DELETE FROM attendance")
        conn.commit()
        messagebox.showinfo("Success", "✅ Database cleared successfully!")

# ✅ Function to exit the application
def exit_application():
    conn.close()
    root.quit()

# ✅ Create GUI using CustomTkinter (Modern UI)
ctk.set_appearance_mode("dark")  # Dark Mode
ctk.set_default_color_theme("blue")  # Theme Color

root = ctk.CTk()
root.title("Face Recognition Attendance System")
root.geometry("400x500")

label = ctk.CTkLabel(root, text="📌 Choose an option:", font=("Arial", 16))
label.pack(pady=10)

btn_register = ctk.CTkButton(root, text="📝 Register Face", font=("Arial", 14), command=register_face)
btn_register.pack(pady=5)

btn_attendance = ctk.CTkButton(root, text="📋 Mark Attendance", font=("Arial", 14), command=mark_attendance)
btn_attendance.pack(pady=5)

btn_clear_db = ctk.CTkButton(root, text="🗑 Clear Database", font=("Arial", 14), fg_color="red", command=clear_database)
btn_clear_db.pack(pady=5)

btn_exit = ctk.CTkButton(root, text="❌ Exit", font=("Arial", 14), fg_color="gray", command=exit_application)
btn_exit.pack(pady=5)

root.mainloop()
