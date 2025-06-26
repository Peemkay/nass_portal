"""
Modified script to apply schema updates directly to the SQLite database without Flask app context
"""

import os
import sqlite3

def apply_schema_updates():
    """Apply schema updates from schema_updates.sql"""
    # Assume the database file is at instance/nass_portal.db relative to this script
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    schema_updates_path = os.path.join(os.path.dirname(__file__), 'schema_updates.sql')

    if not os.path.exists(schema_updates_path):
        print('Schema updates file not found.')
        return

    if not os.path.exists(db_path):
        print(f'Database file not found at {db_path}')
        return

    with open(schema_updates_path, 'r') as f:
        schema_updates = f.read()

    conn = sqlite3.connect(db_path)
    statements = schema_updates.split(';')

    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                conn.execute(statement)
                conn.commit()
                print(f'Successfully executed: {statement[:50]}...')
            except Exception as e:
                conn.rollback()
                print(f'Error executing statement: {e}')
                print(f'Statement: {statement}')

    conn.close()
    print('Schema updates applied successfully.')

if __name__ == '__main__':
    apply_schema_updates()
