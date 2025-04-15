import os
import sqlite3
from werkzeug.security import generate_password_hash

def init_all():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'nass_portal.db')

    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop existing tables
        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('DROP TABLE IF EXISTS admins')
        cursor.execute('DROP TABLE IF EXISTS courses')

        # Create students table with the correct structure
        cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_number TEXT NOT NULL,
            rank TEXT NOT NULL,
            surname TEXT NOT NULL,
            other_names TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            current_unit TEXT NOT NULL,
            date_of_commission TEXT NOT NULL,
            years_in_service INTEGER NOT NULL,
            passport_photo TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        ''')

        # Create admins table
        cursor.execute('''
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create courses table
        cursor.execute('''
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            duration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create indexes for better query performance
        cursor.execute('CREATE INDEX idx_students_service_number ON students(service_number)')
        cursor.execute('CREATE INDEX idx_students_surname ON students(surname)')
        cursor.execute('CREATE INDEX idx_students_rank ON students(rank)')
        cursor.execute('CREATE INDEX idx_students_current_unit ON students(current_unit)')

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