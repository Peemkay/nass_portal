import os
import sqlite3
import glob

# Check for Flask session files
session_files = glob.glob('flask_session/*')
if session_files:
    for file in session_files:
        try:
            os.remove(file)
            print(f"Removed session file: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")
else:
    print("No Flask session files found.")

# Check for session cookies in the database
try:
    # Connect to the database
    conn = sqlite3.connect('instance/nass_portal.db')
    cursor = conn.cursor()

    # Update the admin_logged_in status in the sessions table if it exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM sessions")
        conn.commit()
        print("Sessions table cleared.")
    else:
        print("No sessions table found in the database.")

    # Close the connection
    conn.close()
except Exception as e:
    print(f"Error accessing the database: {e}")

print("\nSession data has been cleared. Please restart the application.")
