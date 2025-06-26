import sqlite3
import os

def fix_courses_schema():
    """Add missing columns to courses table"""
    db_path = 'database.db'
    
    if not os.path.exists(db_path):
        print(f'Database file not found at {db_path}')
        return
    
    conn = sqlite3.connect(db_path)
    
    # List of columns to add
    columns_to_add = [
        ('level', 'TEXT'),
        ('department', 'TEXT'),
        ('start_date', 'TEXT'),
        ('end_date', 'TEXT'),
        ('registration_deadline', 'TEXT'),
        ('max_students', 'INTEGER'),
        ('is_active', 'BOOLEAN DEFAULT 1'),
        ('quarter', 'TEXT'),
        ('year', 'INTEGER'),
        ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    ]
    
    for column_name, column_type in columns_to_add:
        try:
            conn.execute(f'ALTER TABLE courses ADD COLUMN {column_name} {column_type}')
            print(f'Added {column_name} column')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'{column_name} column already exists')
            else:
                print(f'Error adding {column_name} column: {e}')
    
    conn.commit()
    conn.close()
    print('Schema update completed')

if __name__ == '__main__':
    fix_courses_schema()
