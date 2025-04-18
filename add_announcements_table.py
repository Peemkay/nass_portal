import sqlite3
import os
from datetime import datetime
from nass_portal import create_app

def add_announcements_table():
    """Add announcements table to the database"""
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
            
            # Check if announcements table already exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='announcements'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("Creating announcements table...")
                
                # Create the announcements table
                cursor.execute('''
                CREATE TABLE announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    display_order INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
                ''')
                
                # Insert default announcements
                default_announcements = [
                    ('Q2 Course Registration Open', 'Registration for the second quarter courses is now open. Apply before the deadline to secure your spot.', None, 1, 1, datetime.now(), datetime.now()),
                    ('New Advanced Cybersecurity Course', 'We are introducing a new advanced cybersecurity course for officers starting next quarter.', None, 1, 2, datetime.now(), datetime.now()),
                    ('Graduation Ceremony', 'The graduation ceremony for Q1 courses will be held on May 5th, 2025 at the main parade ground.', None, 1, 3, datetime.now(), datetime.now())
                ]
                
                cursor.executemany(
                    'INSERT INTO announcements (title, content, image_url, is_active, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    default_announcements
                )
                
                conn.commit()
                print("Announcements table created and populated successfully!")
            else:
                print("Announcements table already exists.")
            
            # Close the connection
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    add_announcements_table()
