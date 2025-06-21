import sqlite3

# ✅ Connect to the database
conn = sqlite3.connect("attendance_system.db")
cursor = conn.cursor()

# ✅ Function to clear all data from the database
def clear_database():
    confirmation = input("⚠ WARNING: This will DELETE ALL data. Type 'yes' to confirm: ")
    
    if confirmation.lower() == 'yes':
        cursor.execute("DELETE FROM faces")  # Clear registered faces
        cursor.execute("DELETE FROM attendance")  # Clear attendance records
        conn.commit()
        print("✅ Database cleared successfully!")
    else:
        print("❌ Operation canceled.")

# ✅ Run the function
clear_database()

# ✅ Close the database connection
conn.close()