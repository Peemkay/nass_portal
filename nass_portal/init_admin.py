import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_admin():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create admins table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Default credentials (change these in production!)
    username = 'admin'
    password = 'admin123'
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    try:
        # Check if admin user exists
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        if not cursor.fetchone():
            # Insert admin user with hashed password
            cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)',
                          (username, hashed_password))
            print("Admin user created successfully")
        else:
            # Update existing admin password
            cursor.execute('UPDATE admins SET password = ? WHERE username = ?',
                          (hashed_password, username))
            print("Admin password updated successfully")
        
        conn.commit()
        print(f"Admin username: {username}")
        print(f"Admin password: {password}")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_admin()

