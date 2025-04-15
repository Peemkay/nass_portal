"""
Admin routes for the NASS Portal
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .registration_utils import get_all_registration_periods, update_registration_period, add_registration_period, delete_registration_period

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
