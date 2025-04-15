import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'instance', 'nass_portal.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the students table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students';")
table_exists = cursor.fetchone()

print(f"Database path: {db_path}")

if table_exists:
    # Query to check the structure of the students table
    cursor.execute("PRAGMA table_info(students);")
    columns = cursor.fetchall()

    # Print the columns
    print("Students table exists. Columns:")
    for column in columns:
        print(f"{column[0]}: {column[1]} ({column[2]}) {'NOT NULL' if column[3] else 'NULL'} {'PRIMARY KEY' if column[5] else ''}")
else:
    print("Students table does not exist!")

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nAvailable tables:")
    for table in tables:
        print(table[0])

# Close the connection
conn.close()
