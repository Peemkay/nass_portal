"""
Script to update the departments table with the new departments
"""

import os
import sqlite3
import sys

def main():
    # Connect to the database
    db_path = os.path.join('instance', 'nass_portal.db')
    print(f"Connecting to database at {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # First, delete all existing departments
        print("Deleting existing departments...")
        cursor.execute("DELETE FROM departments")

        # Reset the auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='departments'")

        # Define the new departments
        departments = [
            ('CCD - Combat Communication Department', 'Responsible for tactical and operational communication systems in combat environments.', 'fa-satellite-dish', 'images/departments/combat-communications.jpg', 'primary', 1),
            ('ED - Engineering Department', 'Handles the engineering aspects of communication systems including design, installation, and maintenance.', 'fa-tools', 'images/departments/engineering.jpg', 'danger', 2),
            ('TSD - Technical System Department', 'Manages technical systems and equipment for military communications infrastructure.', 'fa-cogs', 'images/departments/technical-systems.jpg', 'success', 3),
            ('ICTD - Information and Communication Technology Department', 'Focuses on information technology, software development, and digital communications.', 'fa-laptop-code', 'images/departments/ict.jpg', 'info', 4),
            ('RDT&ED - Research Development Trial & Evaluation Department', 'Conducts research, development, testing, and evaluation of new communication technologies.', 'fa-flask', 'images/departments/research.jpg', 'warning', 5),
            ('ATSA - Army Training Support Centre', 'Provides training support and educational resources for signals personnel.', 'fa-chalkboard-teacher', 'images/departments/training-support.jpg', 'secondary', 6)
        ]

        # Insert the new departments
        print("Inserting new departments...")
        cursor.executemany(
            'INSERT INTO departments (name, description, icon, image_url, color, display_order, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)',
            departments
        )

        # Commit the changes
        conn.commit()
        print("Departments updated successfully!")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
