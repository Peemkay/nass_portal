import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# SQL commands to create tables
sql_commands = """
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO admins (username, password) VALUES ('admin', 'password');  -- default admin user. CHANGE THIS PASSWORD.
"""

# Execute the SQL commands
cursor.executescript(sql_commands)

# Commit changes and close the connection
conn.commit()
conn.close()
