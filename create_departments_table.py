"""
Script to create the departments table in the database
"""

import os
import sqlite3

# Connect to the database
db_path = os.path.join('instance', 'nass_portal.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the departments table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    print("Creating departments table...")
    
    # Create the departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL DEFAULT 'fa-building',
        image_url TEXT,
        color TEXT NOT NULL DEFAULT 'primary',
        display_order INTEGER NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Insert default departments
    departments = [
        ('Communications Department', 'Responsible for all communication systems and networks within the Nigerian Army.', 'fa-satellite-dish', 'images/departments/communications.jpg', 'primary', 1),
        ('Signals Intelligence', 'Specializes in gathering intelligence through interception and analysis of signals.', 'fa-broadcast-tower', 'images/departments/signals-intelligence.jpg', 'danger', 2),
        ('Cyber Security', 'Protects military networks and systems from cyber threats and attacks.', 'fa-shield-alt', 'images/departments/cyber-security.jpg', 'success', 3),
        ('Electronic Warfare', 'Focuses on military actions involving the use of electromagnetic and directed energy.', 'fa-bolt', 'images/departments/electronic-warfare.jpg', 'warning', 4),
        ('Training & Doctrine', 'Develops and implements training programs and doctrines for signals personnel.', 'fa-chalkboard-teacher', 'images/departments/training.jpg', 'info', 5)
    ]
    
    cursor.executemany(
        'INSERT INTO departments (name, description, icon, image_url, color, display_order) VALUES (?, ?, ?, ?, ?, ?)',
        departments
    )
    
    # Commit the changes
    conn.commit()
    print("Departments table created and populated successfully!")
else:
    print("Departments table already exists.")

# Close the connection
conn.close()
