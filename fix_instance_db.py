import sqlite3
import os

def fix_instance_database():
    """Add missing columns to courses table in the correct database"""
    db_path = 'instance/nass_portal.db'
    
    if not os.path.exists(db_path):
        print(f'Database file not found at {db_path}')
        return
    
    conn = sqlite3.connect(db_path)
    
    # First check current columns
    cursor = conn.execute('PRAGMA table_info(courses)')
    columns = cursor.fetchall()
    print('Current columns in courses table:')
    for col in columns:
        print(f' - {col[1]} (type: {col[2]})')
    
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
    
    print('\nAdding missing columns...')
    for column_name, column_type in columns_to_add:
        try:
            conn.execute(f'ALTER TABLE courses ADD COLUMN {column_name} {column_type}')
            print(f'✓ Added {column_name} column')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'✓ {column_name} column already exists')
            else:
                print(f'✗ Error adding {column_name} column: {e}')
    
    conn.commit()
    
    # Verify the update
    cursor = conn.execute('PRAGMA table_info(courses)')
    columns = cursor.fetchall()
    print('\nUpdated columns in courses table:')
    for col in columns:
        print(f' - {col[1]} (type: {col[2]})')
    
    conn.close()
    print('\nSchema update completed for instance/nass_portal.db')

if __name__ == '__main__':
    fix_instance_database()
