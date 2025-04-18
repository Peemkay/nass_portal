"""
Script to apply the maintenance schema updates to the database
"""

import os
import sqlite3

def apply_maintenance_schema():
    # Connect to the database
    db_path = os.path.join('instance', 'nass_portal.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read the maintenance schema SQL
        with open(os.path.join('nass_portal', 'maintenance_schema.sql'), 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema SQL
        cursor.executescript(schema_sql)
        conn.commit()
        
        print("Maintenance schema applied successfully!")
        return True
    except Exception as e:
        print(f"Error applying maintenance schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    apply_maintenance_schema()
