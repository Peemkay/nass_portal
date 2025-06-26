import os
import sqlite3
import getpass
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_db():
    """Initialize the database with schema and default data."""
    print("\n=== Database Initialization ===")

    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'nass_portal.sqlite')

    # Create instance directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to the database
    conn = sqlite3.connect(db_path)

    try:
        # Read schema file
        with open('nass_portal/schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute schema
        conn.executescript(schema_sql)

        # Read schema updates
        with open('nass_portal/schema_updates.sql', 'r') as f:
            updates_sql = f.read()

        # Execute updates
        conn.executescript(updates_sql)

        # Commit changes
        conn.commit()

        # Create admin user
        create_admin_user(conn)

        # Create default registration quarters
        create_registration_quarters(conn)

        print("\nDatabase initialized successfully.")
        print("You can now run the application with 'python run.py'")

    except Exception as e:
        print(f"\nError during initialization: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_admin_user(conn):
    """Create an admin user with secure password."""
    print("\n=== Admin User Creation ===")
    print("You need to create an admin user to access the admin dashboard.")

    while True:
        username = input("Enter admin username: ").strip()
        if not username:
            print("Username cannot be empty. Please try again.")
            continue

        # Check if username already exists
        cursor = conn.cursor()
        existing_user = cursor.execute(
            "SELECT id FROM admins WHERE username = ?", (username,)
        ).fetchone()

        if existing_user:
            print(f"Username '{username}' already exists. Please choose another username.")
            continue

        break

    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters long. Please try again.")
            continue

        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            continue

        break

    # Hash the password
    password_hash = generate_password_hash(password)

    # Insert admin user
    cursor.execute(
        "INSERT INTO admins (username, password, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.now())
    )

    conn.commit()
    print(f"\nAdmin user '{username}' created successfully.")

def create_registration_quarters(conn):
    """Create default registration quarters for the current year."""
    current_year = datetime.now().year
    next_year = current_year + 1

    print(f"\n=== Creating Registration Quarters for {current_year}/{next_year} ===")

    quarters = [
        {
            'name': f'Quarter 1 ({current_year})',
            'start_date': f'{current_year}-01-01',
            'end_date': f'{current_year}-03-31',
            'registration_deadline': f'{current_year}-01-15',
            'is_active': 0,
            'year': current_year
        },
        {
            'name': f'Quarter 2 ({current_year})',
            'start_date': f'{current_year}-04-01',
            'end_date': f'{current_year}-06-30',
            'registration_deadline': f'{current_year}-04-15',
            'is_active': 0,
            'year': current_year
        },
        {
            'name': f'Quarter 3 ({current_year})',
            'start_date': f'{current_year}-07-01',
            'end_date': f'{current_year}-09-30',
            'registration_deadline': f'{current_year}-07-15',
            'is_active': 0,
            'year': current_year
        },
        {
            'name': f'Quarter 4 ({current_year})',
            'start_date': f'{current_year}-10-01',
            'end_date': f'{current_year}-12-31',
            'registration_deadline': f'{current_year}-10-15',
            'is_active': 0,
            'year': current_year
        },
        {
            'name': f'Quarter 1 ({next_year})',
            'start_date': f'{next_year}-01-01',
            'end_date': f'{next_year}-03-31',
            'registration_deadline': f'{next_year}-01-15',
            'is_active': 0,
            'year': next_year
        }
    ]

    cursor = conn.cursor()

    # Set the current or upcoming quarter as active
    now = datetime.now()
    for quarter in quarters:
        start_date = datetime.strptime(quarter['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(quarter['end_date'], '%Y-%m-%d')

        if start_date <= now <= end_date:
            quarter['is_active'] = 1
            break
    else:
        # If no current quarter, set the next upcoming quarter as active
        for quarter in quarters:
            start_date = datetime.strptime(quarter['start_date'], '%Y-%m-%d')
            if start_date > now:
                quarter['is_active'] = 1
                break

    # Insert quarters
    for quarter in quarters:
        cursor.execute(
            "INSERT OR IGNORE INTO registration_quarters "
            "(name, start_date, end_date, registration_deadline, is_active, year, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                quarter['name'],
                quarter['start_date'],
                quarter['end_date'],
                quarter['registration_deadline'],
                quarter['is_active'],
                quarter['year'],
                datetime.now(),
                datetime.now()
            )
        )

    conn.commit()
    print("Registration quarters created successfully.")

if __name__ == '__main__':
    print("=== Nigerian Army School of Signals Portal Initialization ===")
    print("This script will initialize the database and create necessary data.")
    print("WARNING: This will reset the database if it already exists.")

    confirm = input("Do you want to continue? (y/n): ").lower()
    if confirm != 'y':
        print("Initialization cancelled.")
        sys.exit(0)

    init_db()