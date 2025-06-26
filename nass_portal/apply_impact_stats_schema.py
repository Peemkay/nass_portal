import os
import sqlite3

def apply_impact_stats_schema():
    """Apply the impact stats schema to the database."""
    print("Applying impact stats schema...")

    # Get the database path from the app config
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'nass_portal.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read the schema file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema', 'impact_stats.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()

    # Execute the schema
    cursor.executescript(schema)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Impact stats schema applied successfully!")

if __name__ == '__main__':
    apply_impact_stats_schema()
