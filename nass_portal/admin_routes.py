"""
Admin routes for the NASS Portal
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, jsonify
import csv
import io
import os
import time
import random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .db import get_db
from .registration_utils import get_all_registration_periods, update_registration_period, add_registration_period, delete_registration_period
from .apply_impact_stats_schema import apply_impact_stats_schema

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/')
def index():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student count
    student_count = db.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']

    # Get course count
    course_count = db.execute('SELECT COUNT(*) as count FROM courses').fetchone()['count']

    # Get registration status
    from .registration_utils import is_registration_open, get_registration_status, get_active_registration_period
    registration_open = is_registration_open()
    registration_status = get_registration_status()
    active_period = get_active_registration_period()

    return render_template('admin/dashboard.html',
                           student_count=student_count,
                           course_count=course_count,
                           registration_open=registration_open,
                           registration_status=registration_status,
                           active_period=active_period)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hardcoded admin credentials for development
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_id'] = 1
            session['admin_username'] = username

            return redirect(url_for('admin.index'))

        # If hardcoded credentials don't match, try database
        try:
            db = get_db()
            admin = db.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()

            if admin and check_password_hash(admin['password'], password):
                session['admin_logged_in'] = True
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']

                return redirect(url_for('admin.index'))
        except Exception as e:
            current_app.logger.error(f"Database error during login: {e}")

        flash('Invalid username or password', 'error')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)

    return redirect(url_for('admin.login'))


# Courses Management
@admin_bp.route('/courses')
def courses():
    """Display all courses"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()
    courses = db.execute('SELECT * FROM courses ORDER BY name').fetchall()

    return render_template('admin/courses.html', courses=courses)


@admin_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    """Add a new course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get preset category from query parameter if available
    preset_category = request.args.get('category')

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        category = request.form.get('category')
        level = request.form.get('level')

        # Validate input
        error = None
        if not name:
            error = 'Course name is required.'
        elif not description:
            error = 'Course description is required.'
        elif not category:
            error = 'Course category is required.'
        elif not level:
            error = 'Course level is required.'

        if error is not None:
            flash(error, 'error')
        else:
            db = get_db()
            try:
                # Check if the courses table has the required columns
                columns = [column[1] for column in db.execute('PRAGMA table_info(courses)').fetchall()]

                # Build the query dynamically based on available columns
                insert_columns = ['name', 'description']
                insert_values = [name, description]

                if 'duration' in columns and duration:
                    insert_columns.append('duration')
                    insert_values.append(duration)

                if 'category' in columns and category:
                    insert_columns.append('category')
                    insert_values.append(category)

                if 'level' in columns and level:
                    insert_columns.append('level')
                    insert_values.append(level)

                # Build the query
                query = f'''
                    INSERT INTO courses (
                        {', '.join(insert_columns)}
                    ) VALUES ({', '.join(['?'] * len(insert_values))})
                '''

                # Execute the query
                db.execute(query, insert_values)
                db.commit()
                flash('Course added successfully!', 'success')
                return redirect(url_for('admin.courses'))
            except Exception as e:
                flash(f'Error adding course: {str(e)}', 'error')

    return render_template('admin/add_course.html', preset_category=preset_category)


@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    """Edit an existing course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()

    if course is None:
        flash('Course not found', 'error')
        return redirect(url_for('admin.courses'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        category = request.form.get('category')
        level = request.form.get('level')

        # Validate input
        error = None
        if not name:
            error = 'Course name is required.'
        elif not description:
            error = 'Course description is required.'
        elif not category:
            error = 'Course category is required.'
        elif not level:
            error = 'Course level is required.'

        if error is not None:
            flash(error, 'error')
        else:
            try:
                # Check if the courses table has the required columns
                columns = [column[1] for column in db.execute('PRAGMA table_info(courses)').fetchall()]

                # Build the query dynamically based on available columns
                update_columns = ['name = ?', 'description = ?']
                update_values = [name, description]

                if 'duration' in columns and duration:
                    update_columns.append('duration = ?')
                    update_values.append(duration)

                if 'category' in columns and category:
                    update_columns.append('category = ?')
                    update_values.append(category)

                if 'level' in columns and level:
                    update_columns.append('level = ?')
                    update_values.append(level)

                # Add course_id to values
                update_values.append(course_id)

                # Build the query
                query = f'''
                    UPDATE courses SET
                        {', '.join(update_columns)}
                    WHERE id = ?
                '''

                # Execute the query
                db.execute(query, update_values)
                db.commit()
                flash('Course updated successfully!', 'success')
                return redirect(url_for('admin.courses'))
            except Exception as e:
                flash(f'Error updating course: {str(e)}', 'error')

    return render_template('admin/edit_course.html', course=course)


@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    """Delete a course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()

    if course is None:
        flash('Course not found', 'error')
    else:
        try:
            db.execute('DELETE FROM courses WHERE id = ?', (course_id,))
            db.commit()
            flash('Course deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting course: {str(e)}', 'error')

    return redirect(url_for('admin.courses'))

@admin_bp.route('/registration-periods')
def registration_periods():
    """Manage registration periods"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    periods = get_all_registration_periods()
    current_year = datetime.now().year

    return render_template('admin/registration_periods.html', periods=periods, current_year=current_year)

@admin_bp.route('/registration-periods/add', methods=['POST'])
def add_registration_period_route():
    """Add a new registration period"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        data = {
            'quarter': request.form.get('quarter'),
            'year': request.form.get('year'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'is_active': 'is_active' in request.form,
            'description': request.form.get('description')
        }

        try:
            add_registration_period(data)
            flash('Registration period added successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error adding registration period: {str(e)}")
            flash('An error occurred while adding the registration period', 'error')

    return redirect(url_for('admin.registration_periods'))

@admin_bp.route('/registration-periods/<int:period_id>/update', methods=['POST'])
def update_registration_period_route(period_id):
    """Update a registration period"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        data = {
            'quarter': request.form.get('quarter'),
            'year': request.form.get('year'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'is_active': 'is_active' in request.form,
            'description': request.form.get('description')
        }

        try:
            update_registration_period(period_id, data)
            flash('Registration period updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error updating registration period: {str(e)}")
            flash('An error occurred while updating the registration period', 'error')

    return redirect(url_for('admin.registration_periods'))

@admin_bp.route('/registration-periods/<int:period_id>/delete', methods=['POST'])
def delete_registration_period_route(period_id):
    """Delete a registration period"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    try:
        delete_registration_period(period_id)
        flash('Registration period deleted successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting registration period: {str(e)}")
        flash('An error occurred while deleting the registration period', 'error')

    return redirect(url_for('admin.registration_periods'))

@admin_bp.route('/registration-periods/<int:period_id>/activate', methods=['POST'])
def activate_registration_period(period_id):
    """Activate a registration period"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()

    try:
        # Deactivate all periods
        db.execute('UPDATE registration_periods SET is_active = 0')

        # Activate the selected period
        db.execute('UPDATE registration_periods SET is_active = 1 WHERE id = ?', (period_id,))

        db.commit()
        flash('Registration period activated successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error activating registration period: {str(e)}")
        flash('An error occurred while activating the registration period', 'error')

    return redirect(url_for('admin.registration_periods'))


@admin_bp.route('/students')
def students():
    """Student management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all students
    # First check if corps column exists
    cursor = db.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'corps' in columns:
        students = db.execute('SELECT id, service_number, rank, surname, other_names, date_of_birth, gender, corps, current_unit, date_of_commission, years_in_service, passport_photo FROM students ORDER BY surname').fetchall()
    else:
        # If corps column doesn't exist, use NULL as a placeholder
        students = db.execute('SELECT id, service_number, rank, surname, other_names, date_of_birth, gender, NULL as corps, current_unit, date_of_commission, years_in_service, passport_photo FROM students ORDER BY surname').fetchall()

    # Get statistics
    total_students = len(students)

    # Get gender distribution
    male_count = db.execute('SELECT COUNT(*) as count FROM students WHERE gender = "Male"').fetchone()['count']
    female_count = db.execute('SELECT COUNT(*) as count FROM students WHERE gender = "Female"').fetchone()['count']

    # Get rank distribution
    ranks = db.execute('SELECT rank, COUNT(*) as count FROM students GROUP BY rank ORDER BY count DESC').fetchall()

    # Get unit distribution
    units = db.execute('SELECT current_unit, COUNT(*) as count FROM students GROUP BY current_unit ORDER BY count DESC').fetchall()

    return render_template('admin/students.html',
                           students=students,
                           total_students=total_students,
                           male_count=male_count,
                           female_count=female_count,
                           ranks=ranks,
                           units=units)


@admin_bp.route('/students/<int:student_id>')
def student_detail(student_id):
    """Student detail page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Check if corps column exists
    cursor = db.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    # Get student details
    if 'corps' in columns:
        student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    else:
        # If corps column doesn't exist, add a placeholder
        student = db.execute('SELECT id, service_number, rank, surname, other_names, date_of_birth, gender, current_unit, date_of_commission, years_in_service, passport_photo, created_at, updated_at FROM students WHERE id = ?', (student_id,)).fetchone()
        # Add corps field manually
        student = dict(student)
        student['corps'] = None

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    # Get student documents
    try:
        student_documents = db.execute(
            'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
            'JOIN document_requirements dr ON sd.requirement_id = dr.id '
            'WHERE sd.student_id = ? ORDER BY dr.display_order',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching student documents: {str(e)}")
        student_documents = []

    # Get military courses
    try:
        military_courses = db.execute(
            'SELECT * FROM military_courses WHERE student_id = ? ORDER BY end_date DESC',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching military courses: {str(e)}")
        military_courses = []

    # Get NASS courses (student_courses)
    try:
        student_courses = db.execute(
            'SELECT sc.*, c.name, c.description, c.department, c.quarter, c.year, '
            '(SELECT COUNT(*) FROM certificates WHERE student_id = ? AND course_id = c.id) as has_certificate '
            'FROM student_courses sc '
            'JOIN courses c ON sc.course_id = c.id '
            'WHERE sc.student_id = ? '
            'ORDER BY sc.registration_date DESC',
            (student_id, student_id)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching student courses: {str(e)}")
        student_courses = []

    # Get certificates
    try:
        certificates = db.execute(
            'SELECT cert.*, c.name as course_name '
            'FROM certificates cert '
            'JOIN courses c ON cert.course_id = c.id '
            'WHERE cert.student_id = ? '
            'ORDER BY cert.issue_date DESC',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching certificates: {str(e)}")
        certificates = []

    # Get login history
    try:
        login_history = db.execute(
            'SELECT * FROM student_login_history '
            'WHERE student_id = ? '
            'ORDER BY login_time DESC LIMIT 10',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching login history: {str(e)}")
        login_history = []

    # Get available courses for assignment
    try:
        available_courses = db.execute(
            'SELECT c.* FROM courses c '
            'WHERE c.is_active = 1 AND c.id NOT IN '
            '(SELECT course_id FROM student_courses WHERE student_id = ?) '
            'ORDER BY c.year DESC, c.quarter DESC, c.name',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching available courses: {str(e)}")
        available_courses = []

    # Get completed courses for certificate upload
    try:
        completed_courses = db.execute(
            'SELECT c.id, c.name, c.quarter, c.year FROM student_courses sc '
            'JOIN courses c ON sc.course_id = c.id '
            'WHERE sc.student_id = ? AND sc.status = "completed" '
            'AND c.id NOT IN (SELECT course_id FROM certificates WHERE student_id = ?) '
            'ORDER BY c.year DESC, c.quarter DESC, c.name',
            (student_id, student_id)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching completed courses: {str(e)}")
        completed_courses = []

    # Get document requirements
    try:
        document_requirements = db.execute(
            'SELECT * FROM document_requirements '
            'WHERE is_active = 1 '
            'ORDER BY display_order'
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching document requirements: {str(e)}")
        document_requirements = []

    # Check if tables exist, if not, set empty lists
    if not student_documents and not military_courses:
        try:
            # Check if student_documents table exists
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_documents'")
            if not cursor.fetchone():
                student_documents = []

            # Check if military_courses table exists
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='military_courses'")
            if not cursor.fetchone():
                military_courses = []
        except Exception as e:
            current_app.logger.error(f"Error checking tables: {str(e)}")

    # Current date for forms
    now = datetime.now()

    return render_template('admin/student_detail.html',
                           student=student,
                           student_documents=student_documents,
                           military_courses=military_courses,
                           student_courses=student_courses,
                           certificates=certificates,
                           login_history=login_history,
                           available_courses=available_courses,
                           completed_courses=completed_courses,
                           document_requirements=document_requirements,
                           now=now)


@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit student information"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Check if corps column exists
    cursor = db.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    # Get student details
    if 'corps' in columns:
        student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    else:
        # If corps column doesn't exist, add a placeholder
        student = db.execute('SELECT id, service_number, rank, surname, other_names, date_of_birth, gender, current_unit, date_of_commission, years_in_service, passport_photo, created_at, updated_at FROM students WHERE id = ?', (student_id,)).fetchone()
        # Add corps field manually
        student = dict(student)
        student['corps'] = None

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        # Get form data
        service_number = request.form.get('service_number')
        rank = request.form.get('rank')
        surname = request.form.get('surname')
        other_names = request.form.get('other_names')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        corps = request.form.get('corps')
        current_unit = request.form.get('current_unit')
        date_of_commission = request.form.get('date_of_commission')

        # Calculate years in service
        if date_of_commission:
            commission_date = datetime.strptime(date_of_commission, '%Y-%m-%d')
            years_in_service = datetime.now().year - commission_date.year
        else:
            years_in_service = student['years_in_service']

        # Handle passport photo upload
        passport_photo = student['passport_photo']
        if 'passport_photo' in request.files and request.files['passport_photo'].filename:
            photo_file = request.files['passport_photo']
            if photo_file and allowed_file(photo_file.filename):
                # Generate a secure filename
                filename = secure_filename(f"{service_number}_{int(datetime.now().timestamp())}.jpg")

                # Ensure the upload directory exists
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'passport_photos')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Save the file
                photo_path = os.path.join(upload_dir, filename)
                photo_file.save(photo_path)

                # Update the passport photo filename
                passport_photo = filename

        try:
            # Update student information
            if 'corps' in columns:
                db.execute(
                    'UPDATE students SET service_number = ?, rank = ?, surname = ?, other_names = ?, '
                    'date_of_birth = ?, gender = ?, corps = ?, current_unit = ?, date_of_commission = ?, '
                    'years_in_service = ?, passport_photo = ?, updated_at = CURRENT_TIMESTAMP '
                    'WHERE id = ?',
                    (service_number, rank, surname, other_names, date_of_birth, gender, corps,
                     current_unit, date_of_commission, years_in_service, passport_photo, student_id)
                )
            else:
                db.execute(
                    'UPDATE students SET service_number = ?, rank = ?, surname = ?, other_names = ?, '
                    'date_of_birth = ?, gender = ?, current_unit = ?, date_of_commission = ?, '
                    'years_in_service = ?, passport_photo = ?, updated_at = CURRENT_TIMESTAMP '
                    'WHERE id = ?',
                    (service_number, rank, surname, other_names, date_of_birth, gender,
                     current_unit, date_of_commission, years_in_service, passport_photo, student_id)
                )

            db.commit()
            flash('Student information updated successfully', 'success')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error updating student: {str(e)}")
            flash(f'Error updating student: {str(e)}', 'error')

    return render_template('admin/edit_student.html', student=student)


@admin_bp.route('/students/<int:student_id>/print')
def print_student(student_id):
    """Print student profile"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    # Get student documents
    try:
        student_documents = db.execute(
            'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
            'JOIN document_requirements dr ON sd.requirement_id = dr.id '
            'WHERE sd.student_id = ? ORDER BY dr.display_order',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching student documents: {str(e)}")
        student_documents = []

    # Get military courses
    try:
        military_courses = db.execute(
            'SELECT * FROM military_courses WHERE student_id = ? ORDER BY year DESC',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching military courses: {str(e)}")
        military_courses = []

    # Get educational background
    try:
        student_education = db.execute(
            'SELECT * FROM student_education WHERE student_id = ? ORDER BY year DESC',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching student education: {str(e)}")
        student_education = []

    # Current date for the printout
    now = datetime.now()

    return render_template('admin/student_print.html',
                           student=student,
                           student_documents=student_documents,
                           military_courses=military_courses,
                           student_education=student_education,
                           now=now)


@admin_bp.route('/students/<int:student_id>/assign-course', methods=['POST'])
def assign_course(student_id):
    """Assign a course to a student"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        status = request.form.get('status')
        registration_date = request.form.get('registration_date')
        remarks = request.form.get('remarks')

        # Validate input
        if not course_id:
            flash('Course is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        if not status:
            status = 'registered'

        if not registration_date:
            registration_date = datetime.now().strftime('%Y-%m-%d')

        try:
            # Check if student is already registered for this course
            existing = db.execute(
                'SELECT * FROM student_courses WHERE student_id = ? AND course_id = ?',
                (student_id, course_id)
            ).fetchone()

            if existing:
                flash('Student is already registered for this course', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Insert new course registration
            db.execute(
                'INSERT INTO student_courses (student_id, course_id, status, registration_date, remarks) '
                'VALUES (?, ?, ?, ?, ?)',
                (student_id, course_id, status, registration_date, remarks)
            )
            db.commit()
            flash('Course assigned successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error assigning course: {str(e)}")
            flash(f'Error assigning course: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/update-course-status', methods=['POST'])
def update_course_status(student_id):
    """Update a student's course status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        status = request.form.get('status')
        completion_date = request.form.get('completion_date')
        grade = request.form.get('grade')
        remarks = request.form.get('remarks')

        # Validate input
        if not course_id or not status:
            flash('Course ID and status are required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Update course status
            if status == 'completed' and completion_date:
                db.execute(
                    'UPDATE student_courses SET status = ?, completion_date = ?, grade = ?, remarks = ? '
                    'WHERE student_id = ? AND course_id = ?',
                    (status, completion_date, grade, remarks, student_id, course_id)
                )
            else:
                db.execute(
                    'UPDATE student_courses SET status = ?, grade = ?, remarks = ? '
                    'WHERE student_id = ? AND course_id = ?',
                    (status, grade, remarks, student_id, course_id)
                )
            db.commit()
            flash('Course status updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error updating course status: {str(e)}")
            flash(f'Error updating course status: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/remove-course', methods=['POST'])
def remove_course(student_id):
    """Remove a course from a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')

        if not course_id:
            flash('Course ID is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Delete course registration
            db.execute(
                'DELETE FROM student_courses WHERE student_id = ? AND course_id = ?',
                (student_id, course_id)
            )
            db.commit()
            flash('Course removed successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error removing course: {str(e)}")
            flash(f'Error removing course: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/add-military-course', methods=['POST'])
def add_military_course(student_id):
    """Add a military course to a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        serial_number = request.form.get('serial_number')
        institution_name = request.form.get('institution_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        certificate = request.form.get('certificate')
        grade = request.form.get('grade')
        remarks = request.form.get('remarks')

        # Validate input
        if not institution_name or not start_date or not end_date or not certificate:
            flash('Institution name, start date, end date, and certificate are required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Extract year from end date
            year = end_date.split('-')[0] if '-' in end_date else end_date

            # Insert new military course
            db.execute(
                'INSERT INTO military_courses (student_id, serial_number, institution_name, start_date, end_date, year, certificate, grade, remarks) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (student_id, serial_number, institution_name, start_date, end_date, year, certificate, grade, remarks)
            )
            db.commit()
            flash('Military course added successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error adding military course: {str(e)}")
            flash(f'Error adding military course: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/update-military-course', methods=['POST'])
def update_military_course(student_id):
    """Update a military course in a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        serial_number = request.form.get('serial_number')
        institution_name = request.form.get('institution_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        certificate = request.form.get('certificate')
        grade = request.form.get('grade')
        remarks = request.form.get('remarks')

        # Validate input
        if not course_id or not institution_name or not start_date or not end_date or not certificate:
            flash('Course ID, institution name, start date, end date, and certificate are required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Extract year from end date
            year = end_date.split('-')[0] if '-' in end_date else end_date

            # Update military course
            db.execute(
                'UPDATE military_courses SET serial_number = ?, institution_name = ?, start_date = ?, end_date = ?, '
                'year = ?, certificate = ?, grade = ?, remarks = ? WHERE id = ? AND student_id = ?',
                (serial_number, institution_name, start_date, end_date, year, certificate, grade, remarks, course_id, student_id)
            )
            db.commit()
            flash('Military course updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error updating military course: {str(e)}")
            flash(f'Error updating military course: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/remove-military-course', methods=['POST'])
def remove_military_course(student_id):
    """Remove a military course from a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')

        if not course_id:
            flash('Course ID is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Delete military course
            db.execute(
                'DELETE FROM military_courses WHERE id = ? AND student_id = ?',
                (course_id, student_id)
            )
            db.commit()
            flash('Military course removed successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error removing military course: {str(e)}")
            flash(f'Error removing military course: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/upload-certificate-manual', methods=['POST'])
def upload_certificate_manual(student_id):
    """Upload a certificate for a student"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        issue_date = request.form.get('issue_date')
        certificate_number = request.form.get('certificate_number')
        certificate_file = request.files.get('certificate_file')

        # Validate input
        if not course_id or not issue_date or not certificate_file:
            flash('Course, issue date, and certificate file are required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Check if certificate already exists
            existing = db.execute(
                'SELECT * FROM certificates WHERE student_id = ? AND course_id = ?',
                (student_id, course_id)
            ).fetchone()

            if existing:
                flash('Certificate already exists for this course', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Save certificate file
            if certificate_file and certificate_file.filename:
                # Create certificates directory if it doesn't exist
                certificates_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
                if not os.path.exists(certificates_dir):
                    os.makedirs(certificates_dir)

                # Generate unique filename
                filename = secure_filename(certificate_file.filename)
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f"{student['service_number']}_{course_id}_{int(time.time())}{file_ext}"
                file_path = os.path.join('certificates', unique_filename)
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)

                # Save file
                certificate_file.save(full_path)

                # Insert certificate record
                db.execute(
                    'INSERT INTO certificates (student_id, course_id, file_path, issue_date, certificate_number) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (student_id, course_id, file_path, issue_date, certificate_number)
                )
                db.commit()
                flash('Certificate uploaded successfully', 'success')
            else:
                flash('Certificate file is required', 'error')
        except Exception as e:
            current_app.logger.error(f"Error uploading certificate: {str(e)}")
            flash(f'Error uploading certificate: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/remove-certificate', methods=['POST'])
def remove_certificate(student_id):
    """Remove a certificate from a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id')

        if not certificate_id:
            flash('Certificate ID is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Get certificate details
            certificate = db.execute(
                'SELECT * FROM certificates WHERE id = ? AND student_id = ?',
                (certificate_id, student_id)
            ).fetchone()

            if not certificate:
                flash('Certificate not found', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Delete certificate file
            if certificate['file_path']:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], certificate['file_path'])
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Delete certificate record
            db.execute(
                'DELETE FROM certificates WHERE id = ? AND student_id = ?',
                (certificate_id, student_id)
            )
            db.commit()
            flash('Certificate removed successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error removing certificate: {str(e)}")
            flash(f'Error removing certificate: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/upload-document', methods=['POST'])
def upload_document(student_id):
    """Upload a document for a student"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        requirement_id = request.form.get('requirement_id')
        document_file = request.files.get('document_file')

        # Validate input
        if not requirement_id or not document_file:
            flash('Document type and file are required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Check if document already exists for this requirement
            existing = db.execute(
                'SELECT * FROM student_documents WHERE student_id = ? AND requirement_id = ?',
                (student_id, requirement_id)
            ).fetchone()

            if existing:
                # Delete existing document file
                if existing['file_path']:
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], existing['file_path'])
                    if os.path.exists(file_path):
                        os.remove(file_path)

                # Delete existing document record
                db.execute(
                    'DELETE FROM student_documents WHERE id = ?',
                    (existing['id'],)
                )
                db.commit()

            # Save document file
            if document_file and document_file.filename:
                # Create documents directory if it doesn't exist
                documents_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
                if not os.path.exists(documents_dir):
                    os.makedirs(documents_dir)

                # Generate unique filename
                filename = secure_filename(document_file.filename)
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f"{student['service_number']}_{requirement_id}_{int(time.time())}{file_ext}"
                file_path = os.path.join('documents', unique_filename)
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)

                # Save file
                document_file.save(full_path)

                # Get file size
                file_size = os.path.getsize(full_path)

                # Insert document record
                db.execute(
                    'INSERT INTO student_documents (student_id, requirement_id, file_path, original_filename, file_size) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (student_id, requirement_id, file_path, filename, file_size)
                )
                db.commit()
                flash('Document uploaded successfully', 'success')
            else:
                flash('Document file is required', 'error')
        except Exception as e:
            current_app.logger.error(f"Error uploading document: {str(e)}")
            flash(f'Error uploading document: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/remove-document', methods=['POST'])
def remove_document(student_id):
    """Remove a document from a student's record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        document_id = request.form.get('document_id')

        if not document_id:
            flash('Document ID is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Get document details
            document = db.execute(
                'SELECT * FROM student_documents WHERE id = ? AND student_id = ?',
                (document_id, student_id)
            ).fetchone()

            if not document:
                flash('Document not found', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Delete document file
            if document['file_path']:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Delete document record
            db.execute(
                'DELETE FROM student_documents WHERE id = ? AND student_id = ?',
                (document_id, student_id)
            )
            db.commit()
            flash('Document removed successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error removing document: {str(e)}")
            flash(f'Error removing document: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/create-portal-account', methods=['GET', 'POST'])
def create_student_portal(student_id):
    """Create a portal account for a student"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'GET':
        # Check if student already has a portal account
        portal_user = db.execute(
            'SELECT * FROM student_portal_users WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        if portal_user:
            flash('Student already has a portal account', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        # Generate a random password
        import string
        import random
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        return render_template('admin/create_student_portal.html', student=student, password=password)

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Validate input
        if not password:
            flash('Password is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Check if student already has a portal account
            portal_user = db.execute(
                'SELECT * FROM student_portal_users WHERE student_id = ?',
                (student_id,)
            ).fetchone()

            if portal_user:
                flash('Student already has a portal account', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Create portal account
            from werkzeug.security import generate_password_hash

            db.execute(
                'INSERT INTO student_portal_users (student_id, email, phone, password, is_active, created_at) '
                'VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)',
                (student_id, email, phone, generate_password_hash(password))
            )

            # Update student record to mark as portal registered
            db.execute(
                'UPDATE students SET is_portal_registered = 1, email = ?, phone = ? WHERE id = ?',
                (email, phone, student_id)
            )

            db.commit()
            flash('Portal account created successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error creating portal account: {str(e)}")
            flash(f'Error creating portal account: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/reset-password', methods=['GET', 'POST'])
def reset_student_password(student_id):
    """Reset a student's portal password"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'GET':
        # Generate a random password
        import string
        import random
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return render_template('admin/reset_password.html', student=student, password=password)

    if request.method == 'POST':
        password = request.form.get('password')

        # Validate input
        if not password:
            flash('Password is required', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        try:
            # Check if student has a portal account
            portal_user = db.execute(
                'SELECT * FROM student_portal_users WHERE student_id = ?',
                (student_id,)
            ).fetchone()

            if not portal_user:
                flash('Student does not have a portal account', 'error')
                return redirect(url_for('admin.student_detail', student_id=student_id))

            # Update password
            from werkzeug.security import generate_password_hash

            db.execute(
                'UPDATE student_portal_users SET password = ? WHERE student_id = ?',
                (generate_password_hash(password), student_id)
            )

            db.commit()
            flash('Password reset successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error resetting password: {str(e)}")
            flash(f'Error resetting password: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/toggle-account', methods=['GET'])
def toggle_student_account(student_id):
    """Toggle a student's portal account status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    try:
        # Check if student has a portal account
        portal_user = db.execute(
            'SELECT * FROM student_portal_users WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        if not portal_user:
            flash('Student does not have a portal account', 'error')
            return redirect(url_for('admin.student_detail', student_id=student_id))

        # Toggle account status
        new_status = 0 if portal_user['is_active'] else 1

        db.execute(
            'UPDATE student_portal_users SET is_active = ? WHERE student_id = ?',
            (new_status, student_id)
        )

        db.commit()

        status_text = 'activated' if new_status else 'deactivated'
        flash(f'Student portal account {status_text} successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error toggling account status: {str(e)}")
        flash(f'Error toggling account status: {str(e)}', 'error')

    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/students/<int:student_id>/documents/download')
def download_student_documents(student_id):
    """Download all documents for a student as a zip file"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get student details
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))

    # Get student documents
    try:
        student_documents = db.execute(
            'SELECT sd.*, dr.name as requirement_name FROM student_documents sd '
            'JOIN document_requirements dr ON sd.requirement_id = dr.id '
            'WHERE sd.student_id = ?',
            (student_id,)
        ).fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching student documents: {str(e)}")
        flash('Error fetching student documents', 'error')
        return redirect(url_for('admin.student_detail', student_id=student_id))

    if not student_documents:
        flash('No documents found for this student', 'warning')
        return redirect(url_for('admin.student_detail', student_id=student_id))

    try:
        import io
        import zipfile
        from flask import send_file

        # Create a zip file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for doc in student_documents:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc['file_path'])
                if os.path.exists(file_path):
                    # Add file to zip with a descriptive name
                    zf.write(file_path, f"{doc['requirement_name']}_{doc['original_filename']}")

        # Seek to the beginning of the stream
        memory_file.seek(0)

        # Send the zip file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"documents_{student['service_number']}.zip"
        )
    except Exception as e:
        current_app.logger.error(f"Error creating zip file: {str(e)}")
        flash('Error creating zip file', 'error')
        return redirect(url_for('admin.student_detail', student_id=student_id))


@admin_bp.route('/documents/<int:document_id>/view')
def view_document(document_id):
    """View a document"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get document details
    document = db.execute('SELECT * FROM student_documents WHERE id = ?', (document_id,)).fetchone()

    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('admin.students'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])

    if not os.path.exists(file_path):
        flash('Document file not found', 'error')
        return redirect(url_for('admin.student_detail', student_id=document['student_id']))

    try:
        from flask import send_file
        return send_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Error viewing document: {str(e)}")
        flash('Error viewing document', 'error')
        return redirect(url_for('admin.student_detail', student_id=document['student_id']))


@admin_bp.route('/documents/<int:document_id>/download')
def download_document(document_id):
    """Download a document"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get document details
    document = db.execute('SELECT * FROM student_documents WHERE id = ?', (document_id,)).fetchone()

    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('admin.students'))

    # Get the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])

    if not os.path.exists(file_path):
        flash('Document file not found', 'error')
        return redirect(url_for('admin.student_detail', student_id=document['student_id']))

    try:
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document['original_filename']
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading document: {str(e)}")
        flash('Error downloading document', 'error')
        return redirect(url_for('admin.student_detail', student_id=document['student_id']))


@admin_bp.route('/document-requirements')
def document_requirements():
    """Manage document requirements"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    current_app.logger.info("Loading document requirements page")
    db = get_db()

    try:
        requirements = db.execute('SELECT * FROM document_requirements ORDER BY display_order').fetchall()
        current_app.logger.info(f"Found {len(requirements)} document requirements")
    except Exception as e:
        current_app.logger.error(f"Error loading document requirements: {str(e)}")
        requirements = []
        flash(f'Error loading document requirements: {str(e)}', 'error')

    return render_template('admin/document_requirements.html', requirements=requirements)

@admin_bp.route('/document-requirements/add', methods=['POST'])
def add_document_requirement():
    """Add a new document requirement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        current_app.logger.info("Processing add document requirement request")

        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        is_required = 1 if request.form.get('is_required') else 0
        file_types = request.form.get('file_types')
        max_file_size = float(request.form.get('max_file_size', 5)) * 1024 * 1024  # Convert MB to bytes
        display_order = int(request.form.get('display_order', 0))
        is_active = 1 if request.form.get('is_active') else 0

        current_app.logger.info(f"Form data: name={name}, is_required={is_required}, file_types={file_types}, "
                               f"max_file_size={max_file_size}, display_order={display_order}, is_active={is_active}")

        db = get_db()
        try:
            db.execute(
                'INSERT INTO document_requirements (name, description, is_required, file_types, max_file_size, display_order, is_active) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, description, is_required, file_types, max_file_size, display_order, is_active)
            )
            db.commit()
            current_app.logger.info("Document requirement added successfully")
            flash('Document requirement added successfully', 'success')
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error adding document requirement: {str(e)}")
            flash(f'Error adding document requirement: {str(e)}', 'error')

    return redirect(url_for('admin.document_requirements'))

@admin_bp.route('/document-requirements/edit', methods=['POST'])
def edit_document_requirement():
    """Edit a document requirement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        current_app.logger.info("Processing edit document requirement request")

        # Get form data
        req_id = request.form.get('id')
        name = request.form.get('name')
        description = request.form.get('description')
        is_required = 1 if request.form.get('is_required') else 0
        file_types = request.form.get('file_types')
        max_file_size = float(request.form.get('max_file_size', 5)) * 1024 * 1024  # Convert MB to bytes
        display_order = int(request.form.get('display_order', 0))
        is_active = 1 if request.form.get('is_active') else 0

        current_app.logger.info(f"Form data: id={req_id}, name={name}, is_required={is_required}, file_types={file_types}, "
                               f"max_file_size={max_file_size}, display_order={display_order}, is_active={is_active}")

        db = get_db()
        try:
            db.execute(
                'UPDATE document_requirements SET name = ?, description = ?, is_required = ?, '
                'file_types = ?, max_file_size = ?, display_order = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP '
                'WHERE id = ?',
                (name, description, is_required, file_types, max_file_size, display_order, is_active, req_id)
            )
            db.commit()
            current_app.logger.info(f"Document requirement {req_id} updated successfully")
            flash('Document requirement updated successfully', 'success')
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error updating document requirement: {str(e)}")
            flash(f'Error updating document requirement: {str(e)}', 'error')

    return redirect(url_for('admin.document_requirements'))

@admin_bp.route('/document-requirements/delete', methods=['POST'])
def delete_document_requirement():
    """Delete a document requirement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        current_app.logger.info("Processing delete document requirement request")

        req_id = request.form.get('id')
        current_app.logger.info(f"Deleting document requirement with ID: {req_id}")

        db = get_db()
        try:
            # First delete any associated student documents
            result = db.execute('DELETE FROM student_documents WHERE requirement_id = ?', (req_id,))
            current_app.logger.info(f"Deleted {result.rowcount if hasattr(result, 'rowcount') else 'unknown'} associated student documents")

            # Then delete the requirement
            result = db.execute('DELETE FROM document_requirements WHERE id = ?', (req_id,))
            deleted_count = result.rowcount if hasattr(result, 'rowcount') else 'unknown'
            current_app.logger.info(f"Deleted {deleted_count} document requirement records")

            db.commit()
            current_app.logger.info(f"Document requirement {req_id} deleted successfully")
            flash('Document requirement deleted successfully', 'success')
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error deleting document requirement: {str(e)}")
            flash(f'Error deleting document requirement: {str(e)}', 'error')

    return redirect(url_for('admin.document_requirements'))

@admin_bp.route('/students/export')
def export_students():
    """Export students to CSV"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all students
    students = db.execute('SELECT * FROM students ORDER BY surname').fetchall()

    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['ID', 'Service Number', 'Rank', 'Surname', 'Other Names', 'Gender',
                    'Date of Birth', 'Current Unit', 'Date of Commission', 'Years in Service'])

    # Write data
    for student in students:
        writer.writerow([student['id'], student['service_number'], student['rank'],
                        student['surname'], student['other_names'], student['gender'],
                        student['date_of_birth'], student['current_unit'],
                        student['date_of_commission'], student['years_in_service']])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=students.csv'
    response.headers['Content-type'] = 'text/csv'

    return response


@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Admin settings page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Import settings utilities
    from .settings_utils import get_all_settings, update_settings, get_setting

    # Apply impact stats schema if needed
    try:
        apply_impact_stats_schema()
    except Exception as e:
        current_app.logger.error(f"Error applying impact stats schema: {str(e)}")

    # Get current date for the system information section
    now = datetime.now()

    if request.method == 'POST':
        # Handle different form submissions based on form_type
        form_type = request.form.get('form_type')

        if form_type == 'general_settings':
            # Update general settings
            settings_to_update = {
                'site_title': request.form.get('site_title'),
                'site_description': request.form.get('site_description'),
                'contact_email': request.form.get('contact_email'),
                'contact_phone': request.form.get('contact_phone'),
                'footer_text': request.form.get('footer_text')
            }
            success_count, total_count = update_settings(settings_to_update)
            if success_count == total_count:
                flash('General settings updated successfully!', 'success')
            else:
                flash(f'Some settings could not be updated. {success_count} of {total_count} settings were updated.', 'warning')

        elif form_type == 'registration_settings':
            # Update registration settings
            settings_to_update = {
                'max_students_per_course': request.form.get('max_students_per_course'),
                'require_approval': 'require_approval' in request.form,
                'registration_email_notification': 'registration_email_notification' in request.form,
                'registration_closed_message': request.form.get('registration_closed_message')
            }
            success_count, total_count = update_settings(settings_to_update)
            if success_count == total_count:
                flash('Registration settings updated successfully!', 'success')
            else:
                flash(f'Some settings could not be updated. {success_count} of {total_count} settings were updated.', 'warning')

        elif form_type == 'security_settings':
            # Update security settings
            settings_to_update = {
                'password_min_length': request.form.get('password_min_length'),
                'session_timeout': request.form.get('session_timeout'),
                'login_attempts': request.form.get('login_attempts'),
                'lockout_duration': request.form.get('lockout_duration')
            }
            success_count, total_count = update_settings(settings_to_update)
            if success_count == total_count:
                flash('Security settings updated successfully!', 'success')
            else:
                flash(f'Some settings could not be updated. {success_count} of {total_count} settings were updated.', 'warning')

        elif form_type == 'system_settings':
            # Update system settings
            settings_to_update = {
                'maintenance_mode': 'maintenance_mode' in request.form,
                'maintenance_message': request.form.get('maintenance_message'),
                'debug_mode': 'debug_mode' in request.form,
                'log_level': request.form.get('log_level')
            }
            success_count, total_count = update_settings(settings_to_update)
            if success_count == total_count:
                flash('System settings updated successfully!', 'success')
            else:
                flash(f'Some settings could not be updated. {success_count} of {total_count} settings were updated.', 'warning')

        elif form_type == 'mail_settings':
            # Update mail settings
            settings_to_update = {
                'mail_server': request.form.get('mail_server'),
                'mail_port': request.form.get('mail_port'),
                'mail_use_tls': 'mail_use_tls' in request.form,
                'mail_use_ssl': 'mail_use_ssl' in request.form,
                'mail_username': request.form.get('mail_username'),
                'mail_password': request.form.get('mail_password'),
                'mail_default_sender': request.form.get('mail_default_sender'),
                'mail_sender_name': request.form.get('mail_sender_name'),
                'mail_contact_form_enabled': 'mail_contact_form_enabled' in request.form,
                'mail_contact_form_recipients': request.form.get('mail_contact_form_recipients'),
                'mail_contact_form_subject_prefix': request.form.get('mail_contact_form_subject_prefix')
            }
            success_count, total_count = update_settings(settings_to_update)
            if success_count == total_count:
                flash('Mail settings updated successfully!', 'success')
            else:
                flash(f'Some settings could not be updated. {success_count} of {total_count} settings were updated.', 'warning')

        elif form_type == 'change_password':
            # Change admin password
            from .settings_utils import change_admin_password
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_password or not new_password or not confirm_password:
                flash('All password fields are required.', 'error')
            elif new_password != confirm_password:
                flash('New password and confirmation do not match.', 'error')
            else:
                success, message = change_admin_password(session.get('admin_id'), current_password, new_password)
                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'error')

        return redirect(url_for('admin.settings'))

    # Get all settings grouped by category
    try:
        current_app.logger.info("Attempting to get all settings")
        all_settings = get_all_settings()
        current_app.logger.info(f"Retrieved settings categories: {list(all_settings.keys()) if all_settings else 'None'}")
    except Exception as e:
        current_app.logger.error(f"Error getting settings: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        all_settings = {'general': [], 'registration': [], 'security': [], 'system': []}

    # Get database information
    db_path = os.path.join('instance', 'nass_portal.db')
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    from .settings_utils import format_file_size
    formatted_db_size = format_file_size(db_size)

    # Get database backups
    from .settings_utils import get_database_backups
    backups = get_database_backups()

    return render_template('admin/settings.html',
                          now=now,
                          settings=all_settings,
                          db_size=formatted_db_size,
                          backups=backups)


# Database Management Routes
@admin_bp.route('/settings/backup-database', methods=['POST'])
def backup_database_route():
    """Create a database backup"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    from .settings_utils import backup_database
    success, message, backup_path = backup_database()

    if success:
        current_app.logger.info(f"Database backup created at {backup_path}")

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/restore-database/<path:backup_filename>', methods=['POST'])
def restore_database_route(backup_filename):
    """Restore database from a backup"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Validate the backup filename to prevent directory traversal
    if '..' in backup_filename or backup_filename.startswith('/'):
        flash('Invalid backup filename', 'error')
        return redirect(url_for('admin.settings'))

    backup_path = os.path.join('instance', 'backups', backup_filename)

    if not os.path.exists(backup_path):
        flash('Backup file not found', 'error')
        return redirect(url_for('admin.settings'))

    from .settings_utils import restore_database
    current_app.logger.info(f"Attempting to restore database from {backup_path}")
    success, message = restore_database(backup_path)

    if success:
        current_app.logger.info("Database restored successfully")
    else:
        current_app.logger.error(f"Database restore failed: {message}")

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/reset-settings', methods=['POST'])
def reset_settings_route():
    """Reset all settings to default values"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    from .settings_utils import reset_settings
    current_app.logger.info("Attempting to reset settings to default values")
    try:
        if reset_settings():
            current_app.logger.info("Settings reset successfully")
            flash('All settings have been reset to their default values', 'success')
        else:
            current_app.logger.error("Failed to reset settings")
            flash('An error occurred while resetting settings', 'error')
    except Exception as e:
        current_app.logger.error(f"Error resetting settings: {str(e)}")
        flash('An error occurred while resetting settings', 'error')

    return redirect(url_for('admin.settings'))


@admin_bp.route('/settings/test-email', methods=['POST'])
def test_email():
    """Send a test email using the current mail settings"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    recipient = request.form.get('test_email_recipient')
    if not recipient:
        flash('Please provide a recipient email address', 'error')
        return redirect(url_for('admin.settings'))

    # Use our email utility to send the test email
    from .email_utils import send_test_email
    success, error_message = send_test_email(recipient)

    if success:
        flash('Test email sent successfully! Please check your inbox.', 'success')
    else:
        current_app.logger.error(f"Error sending test email: {error_message}")
        flash(f'Error sending test email: {error_message}', 'error')

    return redirect(url_for('admin.settings'))


# Departments Management Routes
@admin_bp.route('/departments')
def departments():
    """Manage departments"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all departments
    departments = db.execute('SELECT * FROM departments ORDER BY display_order').fetchall()

    return render_template('admin/departments.html', departments=departments)


@admin_bp.route('/departments/add', methods=['GET', 'POST'])
def add_department():
    """Add a new department"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon')
        color = request.form.get('color')
        display_order = request.form.get('display_order', 0)
        is_active = 'is_active' in request.form

        # Validate required fields
        if not name or not description or not icon or not color:
            flash('Please fill in all required fields', 'error')
            return render_template('admin/department_form.html')

        # Handle image upload
        image_url = None
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            if allowed_file(image.filename, ['png', 'jpg', 'jpeg', 'gif']):
                # Create unique filename
                filename = secure_filename(image.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"department_{int(time.time())}_{random.randint(1000, 9999)}.{file_ext}"

                # Ensure upload directory exists
                upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'departments')
                os.makedirs(upload_dir, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_dir, unique_filename)
                image.save(file_path)

                # Store the relative path
                image_url = f"images/departments/{unique_filename}"
            else:
                flash('Invalid file type. Please upload a valid image file (PNG, JPG, JPEG, GIF)', 'error')
                return render_template('admin/department_form.html')

        # Get database connection
        db = get_db()

        try:
            # Insert new department
            db.execute('''
                INSERT INTO departments (
                    name, description, icon, color, image_url, display_order, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                name, description, icon, color, image_url, display_order, is_active
            ))

            db.commit()
            flash('Department added successfully', 'success')
            return redirect(url_for('admin.departments'))

        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            flash(f'Error adding department: {str(e)}', 'error')
            return render_template('admin/department_form.html')

    return render_template('admin/department_form.html')


@admin_bp.route('/departments/<int:department_id>/edit', methods=['GET', 'POST'])
def edit_department(department_id):
    """Edit a department"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get the department
    department = db.execute('SELECT * FROM departments WHERE id = ?', (department_id,)).fetchone()

    if not department:
        flash('Department not found', 'error')
        return redirect(url_for('admin.departments'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon')
        color = request.form.get('color')
        display_order = request.form.get('display_order', 0)
        is_active = 'is_active' in request.form
        delete_image = 'delete_image' in request.form

        # Validate required fields
        if not name or not description or not icon or not color:
            flash('Please fill in all required fields', 'error')
            return render_template('admin/department_form.html', department=department)

        # Handle image upload or deletion
        image_url = department['image_url']
        if delete_image:
            # Delete the current image file if it exists
            if image_url:
                try:
                    file_path = os.path.join(current_app.root_path, 'static', image_url)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    current_app.logger.error(f"Error deleting image: {str(e)}")
            image_url = None

        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            if allowed_file(image.filename, ['png', 'jpg', 'jpeg', 'gif']):
                # Delete the current image file if it exists
                if image_url:
                    try:
                        file_path = os.path.join(current_app.root_path, 'static', image_url)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        current_app.logger.error(f"Error deleting image: {str(e)}")

                # Create unique filename
                filename = secure_filename(image.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"department_{int(time.time())}_{random.randint(1000, 9999)}.{file_ext}"

                # Ensure upload directory exists
                upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'departments')
                os.makedirs(upload_dir, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_dir, unique_filename)
                image.save(file_path)

                # Store the relative path
                image_url = f"images/departments/{unique_filename}"
            else:
                flash('Invalid file type. Please upload a valid image file (PNG, JPG, JPEG, GIF)', 'error')
                return render_template('admin/department_form.html', department=department)

        try:
            # Update department
            db.execute('''
                UPDATE departments SET
                    name = ?, description = ?, icon = ?, color = ?,
                    image_url = ?, display_order = ?, is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                name, description, icon, color, image_url,
                display_order, is_active, department_id
            ))

            db.commit()
            flash('Department updated successfully', 'success')
            return redirect(url_for('admin.departments'))

        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            flash(f'Error updating department: {str(e)}', 'error')
            return render_template('admin/department_form.html', department=department)

    return render_template('admin/department_form.html', department=department)


@admin_bp.route('/departments/<int:department_id>/toggle')
def toggle_department(department_id):
    """Toggle department active status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get the department
    department = db.execute('SELECT * FROM departments WHERE id = ?', (department_id,)).fetchone()

    if not department:
        flash('Department not found', 'error')
        return redirect(url_for('admin.departments'))

    # Toggle the active status
    new_status = not department['is_active']

    try:
        db.execute('UPDATE departments SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                  (new_status, department_id))
        db.commit()

        status_text = 'activated' if new_status else 'deactivated'
        flash(f'Department {status_text} successfully', 'success')

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        flash(f'Error toggling department status: {str(e)}', 'error')

    return redirect(url_for('admin.departments'))


@admin_bp.route('/departments/<int:department_id>/delete')
def delete_department(department_id):
    """Delete a department"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get the department
    department = db.execute('SELECT * FROM departments WHERE id = ?', (department_id,)).fetchone()

    if not department:
        flash('Department not found', 'error')
        return redirect(url_for('admin.departments'))

    try:
        # Delete the image file if it exists
        if department['image_url']:
            try:
                file_path = os.path.join(current_app.root_path, 'static', department['image_url'])
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting image: {str(e)}")

        # Delete the department
        db.execute('DELETE FROM departments WHERE id = ?', (department_id,))
        db.commit()

        flash('Department deleted successfully', 'success')

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        flash(f'Error deleting department: {str(e)}', 'error')

    return redirect(url_for('admin.departments'))


# Maintenance Management Routes
@admin_bp.route('/maintenance')
def maintenance():
    """Manage scheduled maintenance"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all scheduled maintenance periods
    scheduled = db.execute(
        'SELECT * FROM scheduled_maintenance WHERE status = "scheduled" ORDER BY start_datetime'
    ).fetchall()

    in_progress = db.execute(
        'SELECT * FROM scheduled_maintenance WHERE status = "in_progress" ORDER BY start_datetime'
    ).fetchall()

    completed = db.execute(
        'SELECT * FROM scheduled_maintenance WHERE status IN ("completed", "cancelled") ORDER BY start_datetime DESC LIMIT 10'
    ).fetchall()

    # Get maintenance settings
    from .settings_utils import get_setting
    auto_enable = get_setting('maintenance_auto_enable', 'true')
    notification_enabled = get_setting('maintenance_notification_enabled', 'true')
    notification_style = get_setting('maintenance_notification_style', 'banner')

    return render_template('admin/maintenance.html',
                           scheduled=scheduled,
                           in_progress=in_progress,
                           completed=completed,
                           auto_enable=auto_enable,
                           notification_enabled=notification_enabled,
                           notification_style=notification_style)


@admin_bp.route('/maintenance/add', methods=['GET', 'POST'])
def add_maintenance():
    """Add a new scheduled maintenance"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')
        notification_days = int(request.form.get('notification_days', 3))
        show_countdown = 1 if request.form.get('show_countdown') else 0

        # Validate form data
        if not title or not description or not start_date or not start_time or not end_date or not end_time:
            flash('All fields are required', 'error')
            return redirect(url_for('admin.add_maintenance'))

        # Format datetime strings
        start_datetime = f"{start_date}T{start_time}:00"
        end_datetime = f"{end_date}T{end_time}:00"

        # Validate dates
        try:
            start_dt = datetime.fromisoformat(start_datetime)
            end_dt = datetime.fromisoformat(end_datetime)

            if end_dt <= start_dt:
                flash('End date must be after start date', 'error')
                return redirect(url_for('admin.add_maintenance'))

        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('admin.add_maintenance'))

        # Get database connection
        db = get_db()

        try:
            # Insert new maintenance period
            db.execute('''
                INSERT INTO scheduled_maintenance (
                    title, description, start_datetime, end_datetime,
                    status, notification_days_before, show_countdown, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                title, description, start_datetime, end_datetime,
                'scheduled', notification_days, show_countdown
            ))

            db.commit()
            flash('Maintenance period scheduled successfully', 'success')
            return redirect(url_for('admin.maintenance'))

        except Exception as e:
            current_app.logger.error(f"Error scheduling maintenance: {str(e)}")
            flash('An error occurred while scheduling maintenance', 'error')
            return redirect(url_for('admin.add_maintenance'))

    # GET request - show form
    # Set default dates (start: tomorrow, end: day after tomorrow)
    tomorrow = datetime.now() + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)

    default_start_date = tomorrow.strftime('%Y-%m-%d')
    default_start_time = '22:00'
    default_end_date = day_after.strftime('%Y-%m-%d')
    default_end_time = '06:00'

    return render_template('admin/maintenance_form.html',
                          default_start_date=default_start_date,
                          default_start_time=default_start_time,
                          default_end_date=default_end_date,
                          default_end_time=default_end_time)


@admin_bp.route('/maintenance/<int:maintenance_id>/edit', methods=['GET', 'POST'])
def edit_maintenance(maintenance_id):
    """Edit a scheduled maintenance"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get maintenance record
    maintenance = db.execute('SELECT * FROM scheduled_maintenance WHERE id = ?', (maintenance_id,)).fetchone()

    if not maintenance:
        flash('Maintenance period not found', 'error')
        return redirect(url_for('admin.maintenance'))

    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')
        status = request.form.get('status')
        notification_days = int(request.form.get('notification_days', 3))
        show_countdown = 1 if request.form.get('show_countdown') else 0

        # Validate form data
        if not title or not description or not start_date or not start_time or not end_date or not end_time:
            flash('All fields are required', 'error')
            return redirect(url_for('admin.edit_maintenance', maintenance_id=maintenance_id))

        # Format datetime strings
        start_datetime = f"{start_date}T{start_time}:00"
        end_datetime = f"{end_date}T{end_time}:00"

        # Validate dates
        try:
            start_dt = datetime.fromisoformat(start_datetime)
            end_dt = datetime.fromisoformat(end_datetime)

            if end_dt <= start_dt:
                flash('End date must be after start date', 'error')
                return redirect(url_for('admin.edit_maintenance', maintenance_id=maintenance_id))

        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('admin.edit_maintenance', maintenance_id=maintenance_id))

        try:
            # Update maintenance period
            db.execute('''
                UPDATE scheduled_maintenance SET
                    title = ?, description = ?, start_datetime = ?, end_datetime = ?,
                    status = ?, notification_days_before = ?, show_countdown = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                title, description, start_datetime, end_datetime,
                status, notification_days, show_countdown, maintenance_id
            ))

            db.commit()
            flash('Maintenance period updated successfully', 'success')
            return redirect(url_for('admin.maintenance'))

        except Exception as e:
            current_app.logger.error(f"Error updating maintenance: {str(e)}")
            flash('An error occurred while updating maintenance', 'error')
            return redirect(url_for('admin.edit_maintenance', maintenance_id=maintenance_id))

    # GET request - show form with current values
    # Parse datetime strings
    start_dt = datetime.fromisoformat(maintenance['start_datetime'])
    end_dt = datetime.fromisoformat(maintenance['end_datetime'])

    start_date = start_dt.strftime('%Y-%m-%d')
    start_time = start_dt.strftime('%H:%M')
    end_date = end_dt.strftime('%Y-%m-%d')
    end_time = end_dt.strftime('%H:%M')

    return render_template('admin/maintenance_form.html',
                          maintenance=maintenance,
                          start_date=start_date,
                          start_time=start_time,
                          end_date=end_date,
                          end_time=end_time,
                          edit_mode=True)


@admin_bp.route('/maintenance/<int:maintenance_id>/delete', methods=['POST'])
def delete_maintenance(maintenance_id):
    """Delete a scheduled maintenance"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    try:
        # Delete maintenance period
        db.execute('DELETE FROM scheduled_maintenance WHERE id = ?', (maintenance_id,))
        db.commit()
        flash('Maintenance period deleted successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting maintenance: {str(e)}")
        flash('An error occurred while deleting maintenance', 'error')

    return redirect(url_for('admin.maintenance'))


@admin_bp.route('/maintenance/<int:maintenance_id>/toggle-status', methods=['POST'])
def toggle_maintenance_status(maintenance_id):
    """Toggle maintenance status (activate/deactivate)"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get maintenance record
    maintenance = db.execute('SELECT * FROM scheduled_maintenance WHERE id = ?', (maintenance_id,)).fetchone()

    if not maintenance:
        flash('Maintenance period not found', 'error')
        return redirect(url_for('admin.maintenance'))

    # Get new status from form
    new_status = request.form.get('status')
    if new_status not in ['scheduled', 'in_progress', 'completed', 'cancelled']:
        flash('Invalid status', 'error')
        return redirect(url_for('admin.maintenance'))

    try:
        # Update status
        db.execute('UPDATE scheduled_maintenance SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                  (new_status, maintenance_id))

        # If status is in_progress, enable maintenance mode
        if new_status == 'in_progress':
            from .settings_utils import update_setting
            update_setting('maintenance_mode', 'true')
            flash('Maintenance mode has been enabled', 'info')

        # If status is completed, disable maintenance mode
        elif new_status == 'completed' and maintenance['status'] == 'in_progress':
            from .settings_utils import update_setting
            update_setting('maintenance_mode', 'false')
            flash('Maintenance mode has been disabled', 'info')

        db.commit()
        flash(f'Maintenance status updated to {new_status}', 'success')
    except Exception as e:
        current_app.logger.error(f"Error updating maintenance status: {str(e)}")
        flash('An error occurred while updating maintenance status', 'error')

    return redirect(url_for('admin.maintenance'))


@admin_bp.route('/maintenance/settings', methods=['POST'])
def update_maintenance_settings():
    """Update maintenance settings"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get form data
    auto_enable = request.form.get('auto_enable', 'false')
    notification_enabled = request.form.get('notification_enabled', 'false')
    notification_style = request.form.get('notification_style', 'banner')
    contact_email = request.form.get('contact_email', '')
    contact_phone = request.form.get('contact_phone', '')

    # Update settings
    from .settings_utils import update_setting
    update_setting('maintenance_auto_enable', auto_enable)
    update_setting('maintenance_notification_enabled', notification_enabled)
    update_setting('maintenance_notification_style', notification_style)
    update_setting('maintenance_contact_email', contact_email)
    update_setting('maintenance_contact_phone', contact_phone)

    flash('Maintenance settings updated successfully', 'success')
    return redirect(url_for('admin.maintenance'))


# Contact Messages Management Routes
@admin_bp.route('/contact-messages')
def contact_messages():
    """Manage contact messages"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all contact messages
    contact_messages = db.execute('SELECT * FROM contact_messages ORDER BY id DESC').fetchall()

    return render_template('admin/contact_messages.html', contact_messages=contact_messages)


@admin_bp.route('/contact-messages/<int:message_id>')
def view_message(message_id):
    """View a contact message"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get the message
    message = db.execute('SELECT * FROM contact_messages WHERE id = ?', (message_id,)).fetchone()

    if not message:
        flash('Message not found', 'error')
        return redirect(url_for('admin.contact_messages'))

    # Mark the message as read
    if not message['is_read']:
        db.execute('UPDATE contact_messages SET is_read = 1 WHERE id = ?', (message_id,))
        db.commit()

    return render_template('admin/view_message.html', message=message)


@admin_bp.route('/contact-messages/<int:message_id>/mark-read')
def mark_read(message_id):
    """Mark a message as read"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Mark the message as read
    db.execute('UPDATE contact_messages SET is_read = 1 WHERE id = ?', (message_id,))
    db.commit()

    flash('Message marked as read', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin_bp.route('/contact-messages/mark-all-read')
def mark_all_read():
    """Mark all messages as read"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Mark all messages as read
    db.execute('UPDATE contact_messages SET is_read = 1')
    db.commit()

    flash('All messages marked as read', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin_bp.route('/contact-messages/<int:message_id>/delete')
def delete_message(message_id):
    """Delete a message"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Delete the message
    db.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
    db.commit()

    flash('Message deleted', 'success')
    return redirect(url_for('admin.contact_messages'))


# Announcements Management Routes
@admin_bp.route('/announcements')
def announcements():
    """Manage announcements"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all announcements
    announcements = db.execute('SELECT * FROM announcements ORDER BY display_order').fetchall()

    return render_template('admin/announcements.html', announcements=announcements)


@admin_bp.route('/announcements/add', methods=['GET', 'POST'])
def add_announcement():
    """Add a new announcement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = 1 if request.form.get('is_active') else 0

        # Get the highest display order
        db = get_db()
        max_order = db.execute('SELECT MAX(display_order) as max_order FROM announcements').fetchone()
        display_order = 1
        if max_order and max_order['max_order'] is not None:
            display_order = max_order['max_order'] + 1

        # Handle image upload if provided
        image_url = None
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            if image and allowed_file(image.filename):
                # Generate a secure filename
                filename = secure_filename(f"announcement_{int(datetime.now().timestamp())}.jpg")

                # Ensure the upload directory exists
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'announcements')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Save the file
                image_path = os.path.join(upload_dir, filename)
                image.save(image_path)

                # Set the image URL
                image_url = f"uploads/announcements/{filename}"

        try:
            # Insert the announcement
            db.execute(
                'INSERT INTO announcements (title, content, image_url, is_active, display_order, created_at, updated_at) '
                'VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
                (title, content, image_url, is_active, display_order)
            )
            db.commit()
            flash('Announcement added successfully', 'success')
            return redirect(url_for('admin.announcements'))
        except Exception as e:
            db.rollback()
            flash(f'Error adding announcement: {str(e)}', 'error')

    return render_template('admin/add_announcement.html')


@admin_bp.route('/announcements/<int:announcement_id>/edit', methods=['GET', 'POST'])
def edit_announcement(announcement_id):
    """Edit an announcement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get the announcement
    announcement = db.execute('SELECT * FROM announcements WHERE id = ?', (announcement_id,)).fetchone()

    if not announcement:
        flash('Announcement not found', 'error')
        return redirect(url_for('admin.announcements'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = 1 if request.form.get('is_active') else 0
        display_order = request.form.get('display_order', announcement['display_order'])

        # Handle image upload if provided
        image_url = announcement['image_url']
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            if image and allowed_file(image.filename):
                # Generate a secure filename
                filename = secure_filename(f"announcement_{int(datetime.now().timestamp())}.jpg")

                # Ensure the upload directory exists
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'announcements')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Save the file
                image_path = os.path.join(upload_dir, filename)
                image.save(image_path)

                # Set the image URL
                image_url = f"uploads/announcements/{filename}"

        try:
            # Update the announcement
            db.execute(
                'UPDATE announcements SET title = ?, content = ?, image_url = ?, is_active = ?, '
                'display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (title, content, image_url, is_active, display_order, announcement_id)
            )
            db.commit()
            flash('Announcement updated successfully', 'success')
            return redirect(url_for('admin.announcements'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating announcement: {str(e)}', 'error')

    return render_template('admin/edit_announcement.html', announcement=announcement)


@admin_bp.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
def delete_announcement(announcement_id):
    """Delete an announcement"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    try:
        # Delete the announcement
        db.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        db.commit()
        flash('Announcement deleted successfully', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting announcement: {str(e)}', 'error')

    return redirect(url_for('admin.announcements'))


@admin_bp.route('/announcements/reorder', methods=['POST'])
def reorder_announcements():
    """Reorder announcements"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401

    # Get the new order from the request
    new_order = request.json.get('order', [])

    if not new_order:
        return jsonify({'success': False, 'message': 'No order provided'}), 400

    # Get database connection
    db = get_db()

    try:
        # Update the display order for each announcement
        for i, announcement_id in enumerate(new_order):
            db.execute(
                'UPDATE announcements SET display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (i + 1, announcement_id)
            )

        db.commit()
        return jsonify({'success': True, 'message': 'Announcements reordered successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Error reordering announcements: {str(e)}'}), 500


# Impact Statistics Management Routes
@admin_bp.route('/impact-stats')
def impact_stats():
    """Manage impact statistics"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get all impact stats
    try:
        # Apply the schema first to ensure the table exists
        apply_impact_stats_schema()

        stats = db.execute('SELECT * FROM impact_stats ORDER BY display_order').fetchall()

        # Get active stats for preview
        active_stats = db.execute('SELECT * FROM impact_stats WHERE active = 1 ORDER BY display_order').fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching impact stats: {str(e)}")
        stats = []
        active_stats = []
        flash(f'Error loading impact statistics: {str(e)}. The table may not exist yet.', 'warning')

    return render_template('admin/impact_stats.html', stats=stats, active_stats=active_stats)


@admin_bp.route('/impact-stats/add', methods=['POST'])
def add_impact_stat():
    """Add a new impact statistic"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        value = request.form.get('value')
        icon = request.form.get('icon')
        color = request.form.get('color')
        display_order = request.form.get('display_order', 0)
        active = 1 if request.form.get('active') else 0

        # Validate input
        error = None
        if not title:
            error = 'Title is required.'
        elif not value:
            error = 'Value is required.'

        if error is not None:
            flash(error, 'error')
        else:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO impact_stats (title, value, icon, color, display_order, active) VALUES (?, ?, ?, ?, ?, ?)',
                    (title, value, icon, color, display_order, active)
                )
                db.commit()
                flash('Impact statistic added successfully!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Error adding impact statistic: {str(e)}', 'error')

    return redirect(url_for('admin.impact_stats'))


@admin_bp.route('/impact-stats/edit', methods=['POST'])
def edit_impact_stat():
    """Edit an impact statistic"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        stat_id = request.form.get('id')
        title = request.form.get('title')
        value = request.form.get('value')
        icon = request.form.get('icon')
        color = request.form.get('color')
        display_order = request.form.get('display_order', 0)
        active = 1 if request.form.get('active') else 0

        # Validate input
        error = None
        if not stat_id:
            error = 'Statistic ID is required.'
        elif not title:
            error = 'Title is required.'
        elif not value:
            error = 'Value is required.'

        if error is not None:
            flash(error, 'error')
        else:
            db = get_db()
            try:
                db.execute(
                    'UPDATE impact_stats SET title = ?, value = ?, icon = ?, color = ?, display_order = ?, active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (title, value, icon, color, display_order, active, stat_id)
                )
                db.commit()
                flash('Impact statistic updated successfully!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Error updating impact statistic: {str(e)}', 'error')

    return redirect(url_for('admin.impact_stats'))


@admin_bp.route('/impact-stats/delete', methods=['POST'])
def delete_impact_stat():
    """Delete an impact statistic"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        stat_id = request.form.get('id')

        if not stat_id:
            flash('Statistic ID is required.', 'error')
        else:
            db = get_db()
            try:
                db.execute('DELETE FROM impact_stats WHERE id = ?', (stat_id,))
                db.commit()
                flash('Impact statistic deleted successfully!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Error deleting impact statistic: {str(e)}', 'error')

    return redirect(url_for('admin.impact_stats'))


@admin_bp.route('/impact-stats/<int:stat_id>/toggle', methods=['GET'])
def toggle_impact_stat(stat_id):
    """Toggle the active status of an impact statistic"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    db = get_db()

    # Get the current status
    stat = db.execute('SELECT active FROM impact_stats WHERE id = ?', (stat_id,)).fetchone()

    if not stat:
        flash('Statistic not found', 'error')
    else:
        try:
            # Toggle the status
            new_status = 0 if stat['active'] else 1
            db.execute('UPDATE impact_stats SET active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_status, stat_id))
            db.commit()
            flash('Impact statistic status updated successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error updating impact statistic status: {str(e)}', 'error')

    return redirect(url_for('admin.impact_stats'))