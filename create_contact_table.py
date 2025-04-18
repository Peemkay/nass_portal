"""
Script to create the contact_messages table in the database
"""

import os
import sqlite3

# Connect to the database
db_path = os.path.join('instance', 'nass_portal.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the contact_messages table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_messages'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    print("Creating contact_messages table...")
    
    # Create the contact_messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Commit the changes
    conn.commit()
    print("contact_messages table created successfully!")
else:
    print("contact_messages table already exists.")

# Close the connection
conn.close()
