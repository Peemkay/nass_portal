import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Query to check the structure of the students table
cursor.execute("PRAGMA table_info(students);")
columns = cursor.fetchall()

# Print the columns
for column in columns:
    print(column)

# Close the connection
conn.close()
