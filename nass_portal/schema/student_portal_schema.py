"""
Schema updates for student portal functionality
"""

import sqlite3
from flask import current_app
from ..db import get_db

def apply_student_portal_schema():
    """Apply schema updates for student portal functionality"""
    db = get_db()
    
    try:
        # Check if is_portal_registered column exists in students table
        cursor = db.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_portal_registered' not in columns:
            current_app.logger.info("Adding is_portal_registered column to students table")
            db.execute("ALTER TABLE students ADD COLUMN is_portal_registered INTEGER DEFAULT 0")
        
        if 'email' not in columns:
            current_app.logger.info("Adding email column to students table")
            db.execute("ALTER TABLE students ADD COLUMN email TEXT")
        
        if 'phone' not in columns:
            current_app.logger.info("Adding phone column to students table")
            db.execute("ALTER TABLE students ADD COLUMN phone TEXT")
        
        if 'account_status' not in columns:
            current_app.logger.info("Adding account_status column to students table")
            db.execute("ALTER TABLE students ADD COLUMN account_status TEXT DEFAULT 'active'")
        
        if 'last_login' not in columns:
            current_app.logger.info("Adding last_login column to students table")
            db.execute("ALTER TABLE students ADD COLUMN last_login TIMESTAMP")
        
        # Create student_portal_users table if it doesn't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS student_portal_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                email TEXT,
                phone TEXT,
                password TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        """)
        
        # Create student_login_history table if it doesn't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS student_login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        """)
        
        # Create student_courses table if it doesn't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS student_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                status TEXT DEFAULT 'registered',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_date TIMESTAMP,
                grade TEXT,
                remarks TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        """)
        
        # Create certificates table if it doesn't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                file_path TEXT,
                issue_date TIMESTAMP,
                certificate_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        """)
        
        # Create document_requirements table if it doesn't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS document_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_required INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default document requirements if table is empty
        requirements = db.execute("SELECT COUNT(*) as count FROM document_requirements").fetchone()
        if requirements['count'] == 0:
            db.execute("""
                INSERT INTO document_requirements (name, description, is_required, display_order)
                VALUES 
                ('Passport Photograph', 'Recent passport photograph', 1, 1),
                ('Birth Certificate', 'Birth certificate or age declaration', 1, 2),
                ('Educational Certificate', 'Highest educational qualification', 1, 3),
                ('Military ID Card', 'Military identification card', 1, 4),
                ('Posting Letter', 'Current posting letter', 0, 5),
                ('Medical Report', 'Recent medical report', 0, 6)
            """)
        
        db.commit()
        current_app.logger.info("Student portal schema applied successfully")
        return True
    except sqlite3.Error as e:
        db.rollback()
        current_app.logger.error(f"Error applying student portal schema: {str(e)}")
        return False
