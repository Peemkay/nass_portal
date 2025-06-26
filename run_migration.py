import os
import sys
import sqlite3

def run_migration():
    # Get the database path
    db_path = os.path.join('instance', 'nass_portal.sqlite')
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Read the migration script
    migration_path = os.path.join('nass_portal', 'schema_student_portal.sql')
    with open(migration_path, 'r') as f:
        migration_script = f.read()
    
    # Execute the migration
    try:
        conn.executescript(migration_script)
        conn.commit()
        print("Migration completed successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error executing migration: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
