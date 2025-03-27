import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_db():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read schema file
        with open(os.path.join(os.path.dirname(db_path), 'schema.sql'), 'r') as f:
            schema = f.read()
        
        # Execute schema
        cursor.executescript(schema)
        
        # Create default admin user
        username = 'admin'
        password = 'admin123'  # Change this in production!
        hashed_password = generate_password_hash(password)
        
        cursor.execute('INSERT OR REPLACE INTO admins (username, password) VALUES (?, ?)',
                      (username, hashed_password))
        
        # Commit changes
        conn.commit()
        print("Database initialized successfully!")
        print(f"Default admin credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()