import sqlite3

# Connect to the database
conn = sqlite3.connect("attendance_system.db")
cursor = conn.cursor()

# Fetch and display registered faces
print("\n✅ Registered Faces:")
cursor.execute("SELECT * FROM faces")
faces = cursor.fetchall()
for face in faces:
    print(f"ID: {face[0]}, Name: {face[1]}")

# Fetch and display attendance records
print("\n✅ Attendance Records:")
cursor.execute("SELECT * FROM attendance")
attendance = cursor.fetchall()
for record in attendance:
    print(f"ID: {record[0]}, Name: {record[1]}, Date: {record[2]}, Status: {record[3]}")

conn.close()
