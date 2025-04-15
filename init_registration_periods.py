"""
Initialize registration periods in the database
"""

import sqlite3
from datetime import datetime

def init_registration_periods():
    """Initialize registration periods in the database"""
    conn = sqlite3.connect('instance/nass_portal.sqlite')
    conn.row_factory = sqlite3.Row
    
    # Check if registration_periods table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registration_periods'")
    if not cursor.fetchone():
        print("Creating registration_periods table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        ''')
    
    # Check if there are any registration periods
    cursor.execute("SELECT COUNT(*) as count FROM registration_periods")
    count = cursor.fetchone()['count']
    
    if count == 0:
        print("Adding default registration periods...")
        current_year = datetime.now().year
        
        # Insert default registration periods
        cursor.execute('''
        INSERT INTO registration_periods (quarter, year, start_date, end_date, is_active, description)
        VALUES
        (?, ?, ?, ?, ?, ?),
        (?, ?, ?, ?, ?, ?),
        (?, ?, ?, ?, ?, ?)
        ''', (
            'first', current_year, f'{current_year}-01-01', f'{current_year}-04-30', 1, 'First Quarter Registration Period',
            'second', current_year, f'{current_year}-05-01', f'{current_year}-08-31', 0, 'Second Quarter Registration Period',
            'third', current_year, f'{current_year}-09-01', f'{current_year}-12-31', 0, 'Third Quarter Registration Period'
        ))
        
        conn.commit()
        print(f"Added {cursor.rowcount} registration periods for {current_year}")
    else:
        print(f"Found {count} existing registration periods")
    
    # Display all registration periods
    cursor.execute("SELECT * FROM registration_periods")
    periods = cursor.fetchall()
    
    print("\nCurrent Registration Periods:")
    print("-" * 80)
    for period in periods:
        status = "ACTIVE" if period['is_active'] else "INACTIVE"
        print(f"{period['quarter'].title()} Quarter {period['year']}: {period['start_date']} to {period['end_date']} - {status}")
    print("-" * 80)
    
    conn.close()

if __name__ == "__main__":
    init_registration_periods()
