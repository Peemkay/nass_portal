"""
Admin routes for certificate management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file
import os
import zipfile
import io
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from .db import get_db

admin_certificates_bp = Blueprint('admin_certificates', __name__, url_prefix='/admin/certificates')

# Allowed file extensions for certificates
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_certificates_bp.route('/')
def index():
    """Certificate management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get database connection
    db = get_db()
    
    # Get filter parameters
    course_id = request.args.get('course_id')
    student_search = request.args.get('student_search')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Build query
    query = '''
        SELECT c.*, s.surname, s.other_names, s.service_number, s.passport_photo as student_photo,
               co.name as course_name, co.quarter, co.year, co.department
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        JOIN courses co ON c.course_id = co.id
        WHERE 1=1
    '''
    count_query = '''
        SELECT COUNT(*) as count
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        JOIN courses co ON c.course_id = co.id
        WHERE 1=1
    '''
    params = []
    
    if course_id:
        query += ' AND c.course_id = ?'
        count_query += ' AND c.course_id = ?'
        params.append(course_id)
    
    if student_search:
        query += ' AND (s.surname LIKE ? OR s.other_names LIKE ? OR s.service_number LIKE ?)'
        count_query += ' AND (s.surname LIKE ? OR s.other_names LIKE ? OR s.service_number LIKE ?)'
        search_term = f'%{student_search}%'
        params.extend([search_term, search_term, search_term])
    
    query += ' ORDER BY c.issue_date DESC LIMIT ? OFFSET ?'
    
    # Get total count
    total_count = db.execute(count_query, params).fetchone()['count']
    
    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get certificates
    certificates = db.execute(query, params + [per_page, offset]).fetchall()
    
    # Get all courses for filter
    all_courses = db.execute('SELECT id, name, quarter, year FROM courses ORDER BY year DESC, quarter DESC, name').fetchall()
    
    # Get completed courses for upload
    completed_courses = db.execute('''
        SELECT id, name, quarter, year 
        FROM courses 
        WHERE end_date < date('now') 
        ORDER BY year DESC, quarter DESC, name
    ''').fetchall()
    
    # Get students for upload
    students = db.execute('SELECT id, service_number, rank, surname, other_names FROM students ORDER BY surname, other_names').fetchall()
    
    # Create pagination object
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'pages': total_pages
    }
    
    return render_template('admin/certificates.html',
                           certificates=certificates,
                           all_courses=all_courses,
                           completed_courses=completed_courses,
                           students=students,
                           pagination=pagination)

@admin_certificates_bp.route('/upload', methods=['POST'])
def upload_certificate():
    """Upload a certificate for a student"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        # Get form data
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        certificate_number = request.form.get('certificate_number')
        issue_date = request.form.get('issue_date')
        
        # Validate required fields
        if not student_id or not course_id or not certificate_number or not issue_date:
            flash('All fields are required', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        # Check if certificate file was uploaded
        if 'certificate_file' not in request.files:
            flash('Certificate file is required', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        certificate_file = request.files['certificate_file']
        
        if certificate_file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        if not allowed_file(certificate_file.filename):
            flash('Invalid file type. Allowed types: pdf, jpg, jpeg, png', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # Check if student exists
            student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
            if not student:
                flash('Student not found', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Check if course exists
            course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
            if not course:
                flash('Course not found', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Check if certificate already exists
            existing_cert = db.execute(
                'SELECT * FROM certificates WHERE student_id = ? AND course_id = ?',
                (student_id, course_id)
            ).fetchone()
            
            if existing_cert:
                flash('Certificate already exists for this student and course', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Save certificate file
            filename = secure_filename(f"{student['service_number']}_{course['name'].replace(' ', '_')}_{uuid.uuid4().hex}.{certificate_file.filename.rsplit('.', 1)[1].lower()}")
            
            # Ensure the upload directory exists
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'certificates')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            certificate_file.save(file_path)
            
            # Insert certificate record
            db.execute('''
                INSERT INTO certificates (
                    student_id, course_id, certificate_file, issue_date, certificate_number
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                student_id, course_id, filename, issue_date, certificate_number
            ))
            
            # Update student course status to completed
            db.execute('''
                UPDATE student_courses 
                SET status = 'completed', completion_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND course_id = ?
            ''', (
                issue_date, student_id, course_id
            ))
            
            db.commit()
            
            # Send email notification
            try:
                from .email import send_certificate_issued_email
                student_dict = dict(student)
                course_dict = dict(course)
                certificate_dict = {
                    'certificate_number': certificate_number,
                    'issue_date': issue_date,
                    'certificate_file': filename
                }
                send_certificate_issued_email(student_dict, course_dict, certificate_dict)
            except Exception as e:
                current_app.logger.error(f"Error sending certificate email: {str(e)}")
            
            flash('Certificate uploaded successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error uploading certificate: {str(e)}")
            flash(f'Error uploading certificate: {str(e)}', 'error')
        
        return redirect(url_for('admin_certificates.index'))

@admin_certificates_bp.route('/bulk-upload', methods=['POST'])
def bulk_upload_certificates():
    """Bulk upload certificates for a course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        # Get form data
        course_id = request.form.get('course_id')
        issue_date = request.form.get('issue_date')
        
        # Validate required fields
        if not course_id or not issue_date:
            flash('Course and issue date are required', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        # Check if certificate zip file was uploaded
        if 'certificate_zip' not in request.files:
            flash('Certificate ZIP file is required', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        certificate_zip = request.files['certificate_zip']
        
        if certificate_zip.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        if not certificate_zip.filename.endswith('.zip'):
            flash('Invalid file type. Only ZIP files are allowed', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # Check if course exists
            course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
            if not course:
                flash('Course not found', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Get students registered for this course
            students = db.execute('''
                SELECT s.* FROM students s
                JOIN student_courses sc ON s.id = sc.student_id
                WHERE sc.course_id = ?
            ''', (course_id,)).fetchall()
            
            if not students:
                flash('No students found for this course', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Create a mapping of service numbers to student IDs
            student_map = {student['service_number']: student['id'] for student in students}
            
            # Ensure the upload directory exists
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'certificates')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Process the ZIP file
            success_count = 0
            error_count = 0
            
            with zipfile.ZipFile(certificate_zip) as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.filename.endswith('/'):  # Skip directories
                        continue
                    
                    # Extract service number from filename (e.g., NA12345.pdf)
                    filename = os.path.basename(file_info.filename)
                    service_number = os.path.splitext(filename)[0]
                    
                    # Check if we have a student with this service number
                    if service_number not in student_map:
                        current_app.logger.warning(f"No student found with service number {service_number}")
                        error_count += 1
                        continue
                    
                    student_id = student_map[service_number]
                    
                    # Check if certificate already exists
                    existing_cert = db.execute(
                        'SELECT * FROM certificates WHERE student_id = ? AND course_id = ?',
                        (student_id, course_id)
                    ).fetchone()
                    
                    if existing_cert:
                        current_app.logger.warning(f"Certificate already exists for student {service_number}")
                        error_count += 1
                        continue
                    
                    # Generate a unique filename
                    new_filename = f"{service_number}_{course['name'].replace(' ', '_')}_{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
                    
                    # Extract and save the file
                    with zip_file.open(file_info) as source, open(os.path.join(upload_dir, new_filename), 'wb') as target:
                        target.write(source.read())
                    
                    # Generate certificate number
                    certificate_number = f"NASS/{course['year']}/{course['quarter'].replace(' ', '')}/{service_number}"
                    
                    # Insert certificate record
                    db.execute('''
                        INSERT INTO certificates (
                            student_id, course_id, certificate_file, issue_date, certificate_number
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        student_id, course_id, new_filename, issue_date, certificate_number
                    ))
                    
                    # Update student course status to completed
                    db.execute('''
                        UPDATE student_courses 
                        SET status = 'completed', completion_date = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE student_id = ? AND course_id = ?
                    ''', (
                        issue_date, student_id, course_id
                    ))
                    
                    success_count += 1
                    
                    # Send email notification
                    try:
                        from .email import send_certificate_issued_email
                        student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
                        student_dict = dict(student)
                        course_dict = dict(course)
                        certificate_dict = {
                            'certificate_number': certificate_number,
                            'issue_date': issue_date,
                            'certificate_file': new_filename
                        }
                        send_certificate_issued_email(student_dict, course_dict, certificate_dict)
                    except Exception as e:
                        current_app.logger.error(f"Error sending certificate email: {str(e)}")
            
            db.commit()
            
            if success_count > 0:
                flash(f'Successfully uploaded {success_count} certificates. {error_count} errors.', 'success')
            else:
                flash('No certificates were uploaded. Please check the ZIP file format.', 'error')
        except Exception as e:
            current_app.logger.error(f"Error bulk uploading certificates: {str(e)}")
            flash(f'Error bulk uploading certificates: {str(e)}', 'error')
        
        return redirect(url_for('admin_certificates.index'))

@admin_certificates_bp.route('/view/<int:certificate_id>')
def view_certificate(certificate_id):
    """View a certificate"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get database connection
    db = get_db()
    
    # Get certificate
    certificate = db.execute('SELECT * FROM certificates WHERE id = ?', (certificate_id,)).fetchone()
    
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('admin_certificates.index'))
    
    # Get file path
    file_path = os.path.join(current_app.static_folder, 'uploads', 'certificates', certificate['certificate_file'])
    
    if not os.path.exists(file_path):
        flash('Certificate file not found', 'error')
        return redirect(url_for('admin_certificates.index'))
    
    return send_file(file_path)

@admin_certificates_bp.route('/download/<int:certificate_id>')
def download_certificate(certificate_id):
    """Download a certificate"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get database connection
    db = get_db()
    
    # Get certificate
    certificate = db.execute('''
        SELECT c.*, s.service_number, co.name as course_name
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        JOIN courses co ON c.course_id = co.id
        WHERE c.id = ?
    ''', (certificate_id,)).fetchone()
    
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('admin_certificates.index'))
    
    # Get file path
    file_path = os.path.join(current_app.static_folder, 'uploads', 'certificates', certificate['certificate_file'])
    
    if not os.path.exists(file_path):
        flash('Certificate file not found', 'error')
        return redirect(url_for('admin_certificates.index'))
    
    # Generate download name
    download_name = f"Certificate_{certificate['service_number']}_{certificate['course_name'].replace(' ', '_')}.{certificate['certificate_file'].rsplit('.', 1)[1]}"
    
    return send_file(file_path, as_attachment=True, download_name=download_name)

@admin_certificates_bp.route('/delete', methods=['POST'])
def delete_certificate():
    """Delete a certificate"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id')
        
        if not certificate_id:
            flash('Certificate ID is required', 'error')
            return redirect(url_for('admin_certificates.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # Get certificate
            certificate = db.execute('SELECT * FROM certificates WHERE id = ?', (certificate_id,)).fetchone()
            
            if not certificate:
                flash('Certificate not found', 'error')
                return redirect(url_for('admin_certificates.index'))
            
            # Delete certificate file
            file_path = os.path.join(current_app.static_folder, 'uploads', 'certificates', certificate['certificate_file'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete certificate record
            db.execute('DELETE FROM certificates WHERE id = ?', (certificate_id,))
            
            # Update student course status back to in_progress
            db.execute('''
                UPDATE student_courses 
                SET status = 'in_progress', completion_date = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND course_id = ?
            ''', (
                certificate['student_id'], certificate['course_id']
            ))
            
            db.commit()
            flash('Certificate deleted successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error deleting certificate: {str(e)}")
            flash(f'Error deleting certificate: {str(e)}', 'error')
        
        return redirect(url_for('admin_certificates.index'))
