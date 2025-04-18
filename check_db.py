import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/nass_portal.db')
cursor = conn.cursor()

# Check if document_requirements table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_requirements'")
result = cursor.fetchone()
print(f"Document requirements table exists: {result is not None}")

if result is not None:
    # Check the contents of the document_requirements table
    cursor.execute("SELECT * FROM document_requirements")
    requirements = cursor.fetchall()
    print(f"Number of document requirements: {len(requirements)}")
    
    # Print the column names
    cursor.execute("PRAGMA table_info(document_requirements)")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

# Close the connection
conn.close()
