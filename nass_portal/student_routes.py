import os
import json
import time
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, send_file
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .db import get_db

# Create a blueprint for student routes
student_bp = Blueprint('student', __name__, url_prefix='/student')

# Helper function to check if student is logged in
def is_student_logged_in():
    return session.get('student_logged_in', False)

# Helper function to get current student
def get_current_student():
    if not is_student_logged_in():
        return None

    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (session.get('student_id'),)).fetchone()
    return student

# Helper function to get student courses
def get_student_courses(student_id):
    db = get_db()
    courses = db.execute(
        'SELECT sc.*, c.name, c.description, c.start_date, c.end_date, c.department, '
        '(SELECT COUNT(*) FROM certificates WHERE student_id = ? AND course_id = c.id) as has_certificate '
        'FROM student_courses sc '
        'JOIN courses c ON sc.course_id = c.id '
        'WHERE sc.student_id = ? '
        'ORDER BY sc.registration_date DESC',
        (student_id, student_id)
    ).fetchall()
    return courses

# Helper function to get student certificates
def get_student_certificates(student_id):
    db = get_db()
    certificates = db.execute(
        'SELECT cert.*, c.name as course_name '
        'FROM certificates cert '
        'JOIN courses c ON cert.course_id = c.id '
        'WHERE cert.student_id = ? '
        'ORDER BY cert.issue_date DESC',
        (student_id,)
    ).fetchall()
    return certificates

# Helper function to get available courses
def get_available_courses():
    db = get_db()

    # Get current active quarter
    quarter = db.execute(
        'SELECT * FROM registration_quarters WHERE is_active = 1 LIMIT 1'
    ).fetchone()

    if not quarter:
        return []

    # Check if registration is still open
    now = datetime.now().strftime('%Y-%m-%d')
    if now > quarter['registration_deadline']:
        return []

    # Get available courses for the current quarter
    courses = db.execute(
        'SELECT c.*, '
        '(SELECT COUNT(*) FROM student_courses WHERE course_id = c.id) as registered_students, '
        '(c.max_students - (SELECT COUNT(*) FROM student_courses WHERE course_id = c.id)) as available_slots '
        'FROM courses c '
        'WHERE c.is_active = 1 AND c.quarter = ? AND c.year = ? '
        'AND c.registration_deadline >= ? '
        'ORDER BY c.start_date ASC',
        (quarter['name'], quarter['year'], now)
    ).fetchall()

    return courses

@student_bp.route('/register-portal', methods=['GET', 'POST'])
def register_portal():
    """Student portal registration page"""
    if is_student_logged_in():
        return redirect(url_for('student.dashboard'))

    # Initialize form data from session if available
    form_data = {}
    if 'registration_form_data' in session:
        form_data = session['registration_form_data']

    if request.method == 'POST':
        # Get form data
        form_data = {
            'service_number': request.form.get('service_number'),
            'date_of_birth': request.form.get('date_of_birth'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password'),
            'terms': request.form.get('terms')
        }

        # Save form data to session for persistence
        session['registration_form_data'] = form_data

        # Extract variables for easier access
        service_number = form_data['service_number']
        date_of_birth = form_data['date_of_birth']
        email = form_data['email']
        phone = form_data['phone']
        password = form_data['password']
        confirm_password = form_data['confirm_password']
        terms = form_data['terms']

        # Validate form data
        error = None

        if not service_number:
            error = 'Service number is required.'
        elif not date_of_birth:
            error = 'Date of birth is required.'
        elif not email:
            error = 'Email address is required.'
        elif not phone:
            error = 'Phone number is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif not terms:
            error = 'You must agree to the terms and conditions.'

        # Check password strength
        if not error and (len(password) < 8 or not any(c.isupper() for c in password) or
                          not any(c.isdigit() for c in password) or
                          not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in password)):
            error = 'Password does not meet the requirements.'

        if error is None:
            db = get_db()

            # Check if student exists - use case-insensitive comparison for service number
            student = db.execute(
                'SELECT * FROM students WHERE LOWER(service_number) = LOWER(?) AND date_of_birth = ?',
                (service_number, date_of_birth)
            ).fetchone()

            if student is None:
                # If not found, try to create a new student record
                try:
                    # Insert a new student record with minimal information
                    db.execute(
                        'INSERT INTO students (service_number, rank, surname, other_names, date_of_birth, gender, current_unit, date_of_commission, years_in_service, passport_photo) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (service_number, 'Unknown', 'New', 'Student', date_of_birth, 'Male', 'Unknown', datetime.now().strftime('%Y-%m-%d'), 0, 'default.jpg')
                    )
                    db.commit()

                    # Retrieve the newly created student
                    student = db.execute(
                        'SELECT * FROM students WHERE service_number = ?',
                        (service_number,)
                    ).fetchone()

                    if student is None:
                        error = 'Error creating new student record. Please try again.'
                except Exception as e:
                    db.rollback()
                    current_app.logger.error(f"Error creating new student: {str(e)}")
                    error = f'Error creating new student record: {str(e)}'
            elif student['is_portal_registered'] == 1:
                error = 'This account is already registered for the portal. Please login instead.'
            else:
                try:
                    # Hash the password
                    password_hash = generate_password_hash(password)

                    # Update student record with portal information
                    db.execute(
                        'UPDATE students SET '
                        'password = ?, email = ?, phone = ?, is_portal_registered = 1, '
                        'last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP '
                        'WHERE id = ?',
                        (password_hash, email, phone, student['id'])
                    )

                    # Add a notification for the student
                    db.execute(
                        'INSERT INTO student_notifications (student_id, title, message, type) '
                        'VALUES (?, ?, ?, ?)',
                        (student['id'], 'Welcome to the Student Portal',
                         'Your account has been successfully created. You can now access your courses, certificates, and profile information.',
                         'success')
                    )

                    # Record login history
                    db.execute(
                        'INSERT INTO student_login_history (student_id, ip_address, user_agent) '
                        'VALUES (?, ?, ?)',
                        (student['id'], request.remote_addr, request.user_agent.string)
                    )

                    db.commit()

                    # Set session variables
                    session.clear()  # This clears all session data including registration_form_data
                    session['student_logged_in'] = True
                    session['student_id'] = student['id']
                    session['student_service_number'] = student['service_number']

                    flash('Your student portal account has been created successfully!', 'success')
                    return redirect(url_for('student.dashboard'))

                except Exception as e:
                    db.rollback()
                    current_app.logger.error(f"Error registering student portal: {str(e)}")
                    error = 'An error occurred during registration. Please try again.'

        if error:
            flash(error, 'error')

    return render_template('student_portal_register.html', form_data=form_data)

@student_bp.route('/clear-form')
def clear_form():
    """Clear registration form data from session"""
    if 'registration_form_data' in session:
        session.pop('registration_form_data')
    flash('Form data has been cleared.', 'info')
    return redirect(url_for('student.register_portal'))

@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Student login page"""
    if is_student_logged_in():
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        error = None

        if not email:
            error = 'Email address is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            db = get_db()
            # Find student by email
            student = db.execute(
                'SELECT * FROM students WHERE LOWER(email) = LOWER(?) AND is_portal_registered = 1',
                (email,)
            ).fetchone()

            if student is None:
                error = 'Invalid email address or account not registered for portal access.'
            elif not check_password_hash(student['password'], password):
                error = 'Invalid password.'
            else:
                # Clear the session
                session.clear()

                # Set student session variables
                session['student_logged_in'] = True
                session['student_id'] = student['id']
                session['student_service_number'] = student['service_number']

                # Update last login time
                db.execute(
                    'UPDATE students SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                    (student['id'],)
                )

                # Record login history
                db.execute(
                    'INSERT INTO student_login_history (student_id, ip_address, user_agent) '
                    'VALUES (?, ?, ?)',
                    (student['id'], request.remote_addr, request.user_agent.string)
                )

                db.commit()

                # Redirect to dashboard
                return redirect(url_for('student.dashboard'))

        if error:
            flash(error, 'error')

    return render_template('student_login.html')

@student_bp.route('/logout')
def logout():
    """Student logout"""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('student.login'))

@student_bp.route('/dashboard')
def dashboard():
    """Student dashboard"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get student courses
    courses = get_student_courses(student['id'])

    # Get student certificates
    certificates = get_student_certificates(student['id'])

    # Get available courses
    available_courses = get_available_courses()

    # Get registration deadline
    db = get_db()
    quarter = db.execute('SELECT * FROM registration_quarters WHERE is_active = 1 LIMIT 1').fetchone()
    registration_deadline = quarter['registration_deadline'] if quarter else None

    return render_template(
        'student_dashboard.html',
        student=student,
        courses=courses,
        certificates=certificates,
        available_courses=available_courses,
        registration_deadline=registration_deadline
    )

@student_bp.route('/profile')
def profile():
    """Student profile page"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get student documents
    db = get_db()
    documents = db.execute(
        'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
        'JOIN document_requirements dr ON sd.requirement_id = dr.id '
        'WHERE sd.student_id = ? ORDER BY dr.display_order',
        (student['id'],)
    ).fetchall()

    return render_template(
        'student_profile.html',
        student=student,
        documents=documents
    )

@student_bp.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    """Edit student profile"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        phone = request.form.get('phone')
        current_password = request.form.get('current_password')

        # Validate form data
        error = None

        if not email:
            error = 'Email address is required.'
        elif not phone:
            error = 'Phone number is required.'

        # If password is provided, verify it
        if not error and current_password:
            if not check_password_hash(student['password'], current_password):
                error = 'Current password is incorrect.'

        if error is None:
            try:
                db = get_db()

                # Handle profile photo upload
                profile_photo = student['passport_photo']
                if 'profile_photo' in request.files and request.files['profile_photo'].filename:
                    file = request.files['profile_photo']
                    filename = secure_filename(file.filename)

                    # Generate unique filename
                    timestamp = int(time.time())
                    new_filename = f"{student['service_number']}_{timestamp}_{filename}"

                    # Save file
                    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'passport_photos')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, new_filename)
                    file.save(file_path)

                    profile_photo = f"passport_photos/{new_filename}"

                # Update student record
                db.execute(
                    'UPDATE students SET '
                    'email = ?, phone = ?, passport_photo = ?, updated_at = CURRENT_TIMESTAMP '
                    'WHERE id = ?',
                    (email, phone, profile_photo, student['id'])
                )

                db.commit()
                flash('Your profile has been updated successfully.', 'success')
                return redirect(url_for('student.profile'))

            except Exception as e:
                db.rollback()
                current_app.logger.error(f"Error updating profile: {str(e)}")
                error = 'An error occurred while updating your profile. Please try again.'

        flash(error, 'error')

    return render_template('student_profile_edit.html', student=student)

@student_bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    """Change student password"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    if request.method == 'POST':
        # Get form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate form data
        error = None

        if not current_password:
            error = 'Current password is required.'
        elif not new_password:
            error = 'New password is required.'
        elif not confirm_password:
            error = 'Confirm password is required.'
        elif new_password != confirm_password:
            error = 'New passwords do not match.'
        elif not check_password_hash(student['password'], current_password):
            error = 'Current password is incorrect.'

        # Check password strength
        if not error and (len(new_password) < 8 or not any(c.isupper() for c in new_password) or
                          not any(c.isdigit() for c in new_password) or
                          not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in new_password)):
            error = 'Password does not meet the requirements.'

        if error is None:
            try:
                db = get_db()

                # Hash the new password
                password_hash = generate_password_hash(new_password)

                # Update student record
                db.execute(
                    'UPDATE students SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (password_hash, student['id'])
                )

                # Add a notification for the student
                db.execute(
                    'INSERT INTO student_notifications (student_id, title, message, type) '
                    'VALUES (?, ?, ?, ?)',
                    (student['id'], 'Password Changed',
                     'Your password has been changed successfully.',
                     'success')
                )

                db.commit()
                flash('Your password has been changed successfully.', 'success')
                return redirect(url_for('student.profile'))

            except Exception as e:
                db.rollback()
                current_app.logger.error(f"Error changing password: {str(e)}")
                error = 'An error occurred while changing your password. Please try again.'

        flash(error, 'error')

    return render_template('student_change_password.html', student=student)

@student_bp.route('/documents')
def documents():
    """Student documents page"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get student documents
    db = get_db()
    documents = db.execute(
        'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
        'JOIN document_requirements dr ON sd.requirement_id = dr.id '
        'WHERE sd.student_id = ? ORDER BY dr.display_order',
        (student['id'],)
    ).fetchall()

    return render_template(
        'student_documents.html',
        student=student,
        documents=documents
    )

@student_bp.route('/document/<int:document_id>')
def view_document(document_id):
    """View a document"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get document details
    db = get_db()
    document = db.execute(
        'SELECT * FROM student_documents WHERE id = ? AND student_id = ?',
        (document_id, student['id'])
    ).fetchone()

    if not document:
        flash('Document not found or you do not have permission to view it.', 'error')
        return redirect(url_for('student.documents'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])

    if not os.path.exists(file_path):
        flash('Document file not found.', 'error')
        return redirect(url_for('student.documents'))

    try:
        return send_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Error viewing document: {str(e)}")
        flash('Error viewing document.', 'error')
        return redirect(url_for('student.documents'))

@student_bp.route('/document/<int:document_id>/download')
def download_document(document_id):
    """Download a document"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get document details
    db = get_db()
    document = db.execute(
        'SELECT * FROM student_documents WHERE id = ? AND student_id = ?',
        (document_id, student['id'])
    ).fetchone()

    if not document:
        flash('Document not found or you do not have permission to download it.', 'error')
        return redirect(url_for('student.documents'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])

    if not os.path.exists(file_path):
        flash('Document file not found.', 'error')
        return redirect(url_for('student.documents'))

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document['original_filename']
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading document: {str(e)}")
        flash('Error downloading document.', 'error')
        return redirect(url_for('student.documents'))

@student_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get course details
    db = get_db()
    course_registration = db.execute(
        'SELECT sc.*, c.* FROM student_courses sc '
        'JOIN courses c ON sc.course_id = c.id '
        'WHERE sc.student_id = ? AND sc.course_id = ?',
        (student['id'], course_id)
    ).fetchone()

    if not course_registration:
        flash('Course not found or you are not registered for this course.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check if certificate exists
    certificate = db.execute(
        'SELECT * FROM certificates WHERE student_id = ? AND course_id = ?',
        (student['id'], course_id)
    ).fetchone()

    return render_template(
        'student_course_detail.html',
        student=student,
        course=course_registration,
        certificate=certificate
    )

@student_bp.route('/certificate/<int:certificate_id>')
def certificate(certificate_id):
    """Download a certificate"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get certificate details
    db = get_db()
    certificate = db.execute(
        'SELECT * FROM certificates WHERE id = ? AND student_id = ?',
        (certificate_id, student['id'])
    ).fetchone()

    if not certificate:
        flash('Certificate not found or you do not have permission to download it.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], certificate['certificate_file'])

    if not os.path.exists(file_path):
        flash('Certificate file not found.', 'error')
        return redirect(url_for('student.dashboard'))

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"Certificate_{certificate['certificate_number']}.pdf"
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading certificate: {str(e)}")
        flash('Error downloading certificate.', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/certificate/<int:certificate_id>/view')
def certificate_view(certificate_id):
    """View a certificate"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get certificate details
    db = get_db()
    certificate = db.execute(
        'SELECT * FROM certificates WHERE id = ? AND student_id = ?',
        (certificate_id, student['id'])
    ).fetchone()

    if not certificate:
        flash('Certificate not found or you do not have permission to view it.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], certificate['certificate_file'])

    if not os.path.exists(file_path):
        flash('Certificate file not found.', 'error')
        return redirect(url_for('student.dashboard'))

    try:
        return send_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Error viewing certificate: {str(e)}")
        flash('Error viewing certificate.', 'error')
        return redirect(url_for('student.dashboard'))

@student_bp.route('/register/<int:course_id>', methods=['GET', 'POST'])
def register_course(course_id):
    """Register for a course"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    db = get_db()

    # Check if registration is open
    quarter = db.execute('SELECT * FROM registration_quarters WHERE is_active = 1 LIMIT 1').fetchone()
    if not quarter:
        flash('Registration is currently closed.', 'error')
        return redirect(url_for('student.dashboard'))

    now = datetime.now().strftime('%Y-%m-%d')
    if now > quarter['registration_deadline']:
        flash('Registration deadline has passed.', 'error')
        return redirect(url_for('student.dashboard'))

    # Get course details
    course = db.execute('SELECT * FROM courses WHERE id = ? AND is_active = 1', (course_id,)).fetchone()
    if not course:
        flash('Course not found or not available for registration.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check if student is already registered for this course
    existing_registration = db.execute(
        'SELECT * FROM student_courses WHERE student_id = ? AND course_id = ?',
        (student['id'], course_id)
    ).fetchone()

    if existing_registration:
        flash('You are already registered for this course.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check if course has available slots
    registered_count = db.execute(
        'SELECT COUNT(*) as count FROM student_courses WHERE course_id = ?',
        (course_id,)
    ).fetchone()['count']

    if registered_count >= course['max_students']:
        flash('This course is full. Please try another course.', 'error')
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        try:
            # Register student for the course
            db.execute(
                'INSERT INTO student_courses (student_id, course_id, status, registration_date) '
                'VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                (student['id'], course_id, 'registered')
            )
            db.commit()

            flash(f'You have successfully registered for {course["name"]}.', 'success')
            return redirect(url_for('student.dashboard', registered='success'))

        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error registering for course: {str(e)}")
            flash('An error occurred while registering for the course. Please try again.', 'error')

    return render_template(
        'student_register_course.html',
        student=student,
        course=course,
        quarter=quarter
    )

@student_bp.route('/print-profile')
def print_profile():
    """Print student profile"""
    if not is_student_logged_in():
        return redirect(url_for('student.login'))

    student = get_current_student()
    if not student:
        session.clear()
        flash('Student not found. Please login again.', 'error')
        return redirect(url_for('student.login'))

    # Get student documents
    db = get_db()
    documents = db.execute(
        'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
        'JOIN document_requirements dr ON sd.requirement_id = dr.id '
        'WHERE sd.student_id = ? ORDER BY dr.display_order',
        (student['id'],)
    ).fetchall()

    # Get student courses
    courses = get_student_courses(student['id'])

    # Get student certificates
    certificates = get_student_certificates(student['id'])

    # Current date for the printout
    now = datetime.now()

    return render_template(
        'student_print_profile.html',
        student=student,
        documents=documents,
        courses=courses,
        certificates=certificates,
        now=now
    )
