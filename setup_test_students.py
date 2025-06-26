import sqlite3
from werkzeug.security import generate_password_hash

def setup_test_students():
    """Set up test student accounts with email and password"""
    
    # Connect to database
    conn = sqlite3.connect('instance/nass_portal.db')
    
    # Check existing students
    cursor = conn.execute('SELECT id, service_number, email, is_portal_registered FROM students')
    students = cursor.fetchall()
    
    print('Current students in database:')
    for student in students:
        print(f'  ID: {student[0]}, Service Number: {student[1]}, Email: {student[2]}, Portal Registered: {student[3]}')
    
    # Update students to have email and password for testing
    if students:
        # Set up first student with test credentials
        test_email = 'student1@nass.edu.ng'
        test_password = 'password123'
        password_hash = generate_password_hash(test_password)
        
        conn.execute(
            'UPDATE students SET email = ?, password = ?, is_portal_registered = 1 WHERE id = ?',
            (test_email, password_hash, students[0][0])
        )
        
        if len(students) > 1:
            # Set up second student with test credentials
            test_email2 = 'student2@nass.edu.ng'
            test_password2 = 'password456'
            password_hash2 = generate_password_hash(test_password2)
            
            conn.execute(
                'UPDATE students SET email = ?, password = ?, is_portal_registered = 1 WHERE id = ?',
                (test_email2, password_hash2, students[1][0])
            )
        
        conn.commit()
        print('\nTest credentials set up:')
        print(f'  Student 1: {test_email} / {test_password}')
        if len(students) > 1:
            print(f'  Student 2: {test_email2} / {test_password2}')
    else:
        print('No students found in database')
    
    conn.close()
    print('\nStudents updated successfully!')

if __name__ == '__main__':
    setup_test_students()
