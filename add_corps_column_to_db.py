import sqlite3
import os

def add_corps_column_to_db():
    """Add corps column to students table in the database"""
    # Find the database file
    db_paths = [
        'database.db',
        os.path.join('nass_portal', 'database.db'),
        os.path.join('instance', 'database.db')
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found")
        return
    
    print(f"Using database at {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if corps column already exists
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'corps' not in columns:
            print("Adding 'corps' column to students table...")
            cursor.execute("ALTER TABLE students ADD COLUMN corps TEXT")
            conn.commit()
            print("Column added successfully!")
        else:
            print("Corps column already exists.")
        
        # Close the connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    add_corps_column_to_db()
