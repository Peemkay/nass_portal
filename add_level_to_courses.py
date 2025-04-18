import sqlite3
import os
from nass_portal import create_app

def add_level_to_courses():
    """Add level field to courses table"""
    app = create_app()
    
    with app.app_context():
        # Get the path to the database file
        db_path = os.path.join('instance', 'database.db')
        
        if not os.path.exists(db_path):
            print(f"Database file not found at {db_path}")
            return
        
        print(f"Using database at {db_path}")
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if level column already exists
            cursor.execute("PRAGMA table_info(courses)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'level' not in column_names:
                print("Adding level column to courses table...")
                
                # Add the level column
                cursor.execute('ALTER TABLE courses ADD COLUMN level TEXT DEFAULT "General"')
                conn.commit()
                print("Level column added successfully!")
            else:
                print("Level column already exists.")
            
            # Close the connection
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    add_level_to_courses()
