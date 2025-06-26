"""
Admin routes for course management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from .db import get_db

admin_courses_bp = Blueprint('admin_courses', __name__, url_prefix='/admin/courses')

@admin_courses_bp.route('/')
def index():
    """Course management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get filter parameters
    quarter = request.args.get('quarter')
    department = request.args.get('department')
    status = request.args.get('status')

    # Build query
    query = 'SELECT c.*, (SELECT COUNT(*) FROM student_courses WHERE course_id = c.id) as registered_students FROM courses c WHERE 1=1'
    params = []

    if quarter:
        query += ' AND c.quarter = ?'
        params.append(quarter)

    if department:
        query += ' AND c.department = ?'
        params.append(department)

    if status and 'is_active' in db.execute('PRAGMA table_info(courses)').fetchall():
        query += ' AND c.is_active = ?'
        params.append(int(status))

    query += ' ORDER BY c.name'

    # Get courses
    courses = db.execute(query, params).fetchall()

    # Get quarters for filter
    try:
        quarters = db.execute('SELECT DISTINCT name, year FROM registration_quarters ORDER BY year DESC, name').fetchall()
    except:
        # If the year column doesn't exist, just get the names
        quarters = db.execute('SELECT DISTINCT name FROM registration_quarters ORDER BY name').fetchall()

    # Get departments for filter
    departments = db.execute('SELECT DISTINCT name FROM departments WHERE is_active = 1 ORDER BY name').fetchall()

    # Get current year
    current_year = datetime.now().year

    return render_template('admin/courses.html',
                           courses=courses,
                           quarters=quarters,
                           departments=departments,
                           current_year=current_year)

@admin_courses_bp.route('/add', methods=['POST'])
def add_course():
    """Add a new course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        level = request.form.get('level')
        department = request.form.get('department')
        duration = request.form.get('duration')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        max_students = request.form.get('max_students')
        quarter = request.form.get('quarter')
        year = request.form.get('year')
        is_active = 'is_active' in request.form

        # Validate required fields
        if not name or not description:
            flash('Name and description are required', 'error')
            return redirect(url_for('admin_courses.index'))

        # Get database connection
        db = get_db()

        try:
            # Check if the courses table has the required columns
            columns = [column[1] for column in db.execute('PRAGMA table_info(courses)').fetchall()]

            # Build the query dynamically based on available columns
            insert_columns = ['name', 'description']
            insert_values = [name, description]

            if 'level' in columns and level:
                insert_columns.append('level')
                insert_values.append(level)

            if 'department' in columns and department:
                insert_columns.append('department')
                insert_values.append(department)

            if 'duration' in columns and duration:
                insert_columns.append('duration')
                insert_values.append(duration)

            if 'start_date' in columns and start_date:
                insert_columns.append('start_date')
                insert_values.append(start_date)

            if 'end_date' in columns and end_date:
                insert_columns.append('end_date')
                insert_values.append(end_date)

            if 'registration_deadline' in columns and registration_deadline:
                insert_columns.append('registration_deadline')
                insert_values.append(registration_deadline)

            if 'max_students' in columns and max_students:
                insert_columns.append('max_students')
                insert_values.append(max_students)

            if 'quarter' in columns and quarter:
                insert_columns.append('quarter')
                insert_values.append(quarter)

            if 'year' in columns and year:
                insert_columns.append('year')
                insert_values.append(year)

            if 'is_active' in columns:
                insert_columns.append('is_active')
                insert_values.append(is_active)

            # Build the query
            query = f'''
                INSERT INTO courses (
                    {', '.join(insert_columns)}
                ) VALUES ({', '.join(['?'] * len(insert_values))})
            '''

            # Execute the query
            db.execute(query, insert_values)

            db.commit()
            flash('Course added successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error adding course: {str(e)}")
            flash(f'Error adding course: {str(e)}', 'error')

        return redirect(url_for('admin_courses.index'))

@admin_courses_bp.route('/edit', methods=['POST'])
def edit_course():
    """Edit a course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Get form data
        course_id = request.form.get('course_id')
        name = request.form.get('name')
        description = request.form.get('description')
        level = request.form.get('level')
        department = request.form.get('department')
        duration = request.form.get('duration')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        max_students = request.form.get('max_students')
        quarter = request.form.get('quarter')
        year = request.form.get('year')
        is_active = 'is_active' in request.form

        # Validate required fields
        if not course_id or not name or not description:
            flash('Course ID, name, and description are required', 'error')
            return redirect(url_for('admin_courses.index'))

        # Get database connection
        db = get_db()

        try:
            # Check if the courses table has the required columns
            columns = [column[1] for column in db.execute('PRAGMA table_info(courses)').fetchall()]

            # Build the query dynamically based on available columns
            update_columns = []
            update_values = []

            # Always update name and description
            update_columns.append('name = ?')
            update_values.append(name)

            update_columns.append('description = ?')
            update_values.append(description)

            if 'level' in columns and level:
                update_columns.append('level = ?')
                update_values.append(level)

            if 'department' in columns and department:
                update_columns.append('department = ?')
                update_values.append(department)

            if 'duration' in columns and duration:
                update_columns.append('duration = ?')
                update_values.append(duration)

            if 'start_date' in columns and start_date:
                update_columns.append('start_date = ?')
                update_values.append(start_date)

            if 'end_date' in columns and end_date:
                update_columns.append('end_date = ?')
                update_values.append(end_date)

            if 'registration_deadline' in columns and registration_deadline:
                update_columns.append('registration_deadline = ?')
                update_values.append(registration_deadline)

            if 'max_students' in columns and max_students:
                update_columns.append('max_students = ?')
                update_values.append(max_students)

            if 'quarter' in columns and quarter:
                update_columns.append('quarter = ?')
                update_values.append(quarter)

            if 'year' in columns and year:
                update_columns.append('year = ?')
                update_values.append(year)

            if 'is_active' in columns:
                update_columns.append('is_active = ?')
                update_values.append(is_active)

            if 'updated_at' in columns:
                update_columns.append('updated_at = CURRENT_TIMESTAMP')

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
            flash('Course updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error updating course: {str(e)}")
            flash(f'Error updating course: {str(e)}', 'error')

        return redirect(url_for('admin_courses.index'))

@admin_courses_bp.route('/delete', methods=['POST'])
def delete_course():
    """Delete a course"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        course_id = request.form.get('course_id')

        if not course_id:
            flash('Course ID is required', 'error')
            return redirect(url_for('admin_courses.index'))

        # Get database connection
        db = get_db()

        try:
            # Check if there are students registered for this course
            student_count = db.execute('SELECT COUNT(*) as count FROM student_courses WHERE course_id = ?', (course_id,)).fetchone()['count']

            if student_count > 0:
                flash(f'Cannot delete course: {student_count} students are registered for this course', 'error')
                return redirect(url_for('admin_courses.index'))

            # Delete course
            db.execute('DELETE FROM courses WHERE id = ?', (course_id,))
            db.commit()
            flash('Course deleted successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error deleting course: {str(e)}")
            flash(f'Error deleting course: {str(e)}', 'error')

        return redirect(url_for('admin_courses.index'))

@admin_courses_bp.route('/get-course-data')
def get_course_data():
    """Get course data for editing"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not logged in'})

    course_id = request.args.get('course_id')

    if not course_id:
        return jsonify({'success': False, 'message': 'Course ID is required'})

    # Get database connection
    db = get_db()

    try:
        # Get course
        course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()

        if not course:
            return jsonify({'success': False, 'message': 'Course not found'})

        # Convert to dict
        course_dict = dict(course)

        return jsonify({'success': True, 'course': course_dict})
    except Exception as e:
        current_app.logger.error(f"Error getting course data: {str(e)}")
        return jsonify({'success': False, 'message': f'Error getting course data: {str(e)}'})
