"""
Script to update the student schema to ensure the is_portal_registered column exists
"""

import os
import sqlite3
import sys
from nass_portal import create_app

# Add verbose output
print("Starting student schema update script...")

def update_student_schema():
    """Update the student schema to ensure the is_portal_registered column exists"""
    app = create_app()

    with app.app_context():
        # Get the database path from the app config
        db_path = app.config['DATABASE']

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the students table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        if not cursor.fetchone():
            print("Students table does not exist. Please run the init-db command first.")
            conn.close()
            return

        # Check if the is_portal_registered column exists
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Add missing columns if they don't exist
        missing_columns = []

        if 'is_portal_registered' not in column_names:
            missing_columns.append(('is_portal_registered', 'BOOLEAN DEFAULT 0'))

        if 'password' not in column_names:
            missing_columns.append(('password', 'TEXT'))

        if 'email' not in column_names:
            missing_columns.append(('email', 'TEXT'))

        if 'phone' not in column_names:
            missing_columns.append(('phone', 'TEXT'))

        if 'account_status' not in column_names:
            missing_columns.append(('account_status', 'TEXT DEFAULT "active"'))

        if 'last_login' not in column_names:
            missing_columns.append(('last_login', 'TIMESTAMP'))

        if 'reset_token' not in column_names:
            missing_columns.append(('reset_token', 'TEXT'))

        if 'reset_token_expiry' not in column_names:
            missing_columns.append(('reset_token_expiry', 'TIMESTAMP'))

        # Add the missing columns
        for column_name, column_type in missing_columns:
            try:
                cursor.execute(f"ALTER TABLE students ADD COLUMN {column_name} {column_type}")
                print(f"Added column {column_name} to students table")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")

        # Create student_notifications table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        )
        """)
        print("Created student_notifications table if it didn't exist")

        # Create student_login_history table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        )
        """)
        print("Created student_login_history table if it didn't exist")

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_notifications_student_id ON student_notifications(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_login_history_student_id ON student_login_history(student_id)")

        # Commit the changes
        conn.commit()
        conn.close()

        print("Student schema updated successfully")

if __name__ == "__main__":
    update_student_schema()
