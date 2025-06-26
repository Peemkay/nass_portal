import os
import sqlite3

def check_courses_columns():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    if not os.path.exists(db_path):
        print(f'Database file not found at {db_path}')
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("PRAGMA table_info(courses)")
    columns = cursor.fetchall()
    conn.close()

    print("Columns in courses table:")
    for col in columns:
        print(f" - {col[1]} (type: {col[2]})")

if __name__ == '__main__':
    check_courses_columns()
