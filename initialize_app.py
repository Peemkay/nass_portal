import os
import sqlite3
from werkzeug.security import generate_password_hash

def init_all():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          'nass_portal', 'database.db')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read schema file
        schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
        with open(schema_path, 'r') as f:
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
        print(f"Error during initialization: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_all()