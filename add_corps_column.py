import sqlite3
import os

def add_corps_column():
    """Add corps column to students table if it doesn't exist"""
    # List all files in current directory
    print("Current directory:", os.getcwd())
    print("Files in current directory:", os.listdir())

    # List files in nass_portal directory
    if os.path.exists('nass_portal'):
        print("Files in nass_portal directory:", os.listdir('nass_portal'))

    # Try different database paths
    possible_paths = [
        os.path.join('nass_portal', 'database.db'),
        os.path.join('instance', 'database.db'),
        'database.db',
        os.path.join('nass_portal', 'instance', 'database.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at {db_path}")
            break

    if not db_path:
        print("Database file not found in any of the expected locations")
        return

    print(f"Using database at {db_path}")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if corps column already exists
        print("Checking if corps column exists...")
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {columns}")

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
    add_corps_column()
