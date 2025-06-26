"""
Admin routes for reports
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file
import os
import csv
import io
# Try to import xlsxwriter, but make it optional
try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False
    print("Warning: xlsxwriter module not found. Excel export will not be available.")
from datetime import datetime
from .db import get_db

admin_reports_bp = Blueprint('admin_reports', __name__, url_prefix='/admin/reports')

@admin_reports_bp.route('/')
def index():
    """Reports page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get filter parameters
    quarter = request.args.get('quarter')
    department = request.args.get('department')
    course_id = request.args.get('course_id')

    # Build query for registrations
    query = '''
        SELECT sc.*, s.service_number, s.rank, s.surname, s.other_names, s.corps,
               c.name as course_name, c.department, c.quarter, c.year
        FROM student_courses sc
        JOIN students s ON sc.student_id = s.id
        JOIN courses c ON sc.course_id = c.id
        WHERE 1=1
    '''
    params = []

    if quarter:
        query += ' AND c.quarter = ?'
        params.append(quarter)

    if department:
        query += ' AND c.department = ?'
        params.append(department)

    if course_id:
        query += ' AND c.id = ?'
        params.append(course_id)

    query += ' ORDER BY sc.registration_date DESC'

    # Get registrations
    registrations = db.execute(query, params).fetchall()

    # Get statistics
    stats = {
        'total_students': db.execute('SELECT COUNT(*) as count FROM students').fetchone()['count'],
        'total_courses': db.execute('SELECT COUNT(*) as count FROM courses').fetchone()['count'],
        'total_registrations': db.execute('SELECT COUNT(*) as count FROM student_courses').fetchone()['count'],
        'total_certificates': db.execute('SELECT COUNT(*) as count FROM certificates').fetchone()['count']
    }

    # Get quarters for filter
    quarters = db.execute('SELECT DISTINCT name, year FROM registration_quarters ORDER BY year DESC, name').fetchall()

    # Get departments for filter
    departments = db.execute('SELECT DISTINCT name FROM departments WHERE is_active = 1 ORDER BY name').fetchall()

    # Get courses for filter
    courses = db.execute('SELECT id, name FROM courses ORDER BY name').fetchall()

    # Get chart data

    # Quarter data
    quarter_data = {
        'labels': [],
        'values': []
    }

    quarter_results = db.execute('''
        SELECT c.quarter || ' ' || c.year as quarter_label, COUNT(*) as count
        FROM student_courses sc
        JOIN courses c ON sc.course_id = c.id
        GROUP BY c.quarter, c.year
        ORDER BY c.year DESC, c.quarter DESC
        LIMIT 6
    ''').fetchall()

    for row in quarter_results:
        quarter_data['labels'].append(row['quarter_label'])
        quarter_data['values'].append(row['count'])

    # Department data
    department_data = {
        'labels': [],
        'values': []
    }

    department_results = db.execute('''
        SELECT c.department, COUNT(*) as count
        FROM student_courses sc
        JOIN courses c ON sc.course_id = c.id
        GROUP BY c.department
        ORDER BY count DESC
    ''').fetchall()

    for row in department_results:
        department_data['labels'].append(row['department'])
        department_data['values'].append(row['count'])

    # Level data
    level_data = {
        'labels': [],
        'values': []
    }

    level_results = db.execute('''
        SELECT c.level, COUNT(*) as count
        FROM student_courses sc
        JOIN courses c ON sc.course_id = c.id
        GROUP BY c.level
        ORDER BY count DESC
    ''').fetchall()

    for row in level_results:
        level_data['labels'].append(row['level'])
        level_data['values'].append(row['count'])

    # Corps data
    corps_data = {
        'labels': [],
        'values': []
    }

    corps_results = db.execute('''
        SELECT s.corps, COUNT(*) as count
        FROM student_courses sc
        JOIN students s ON sc.student_id = s.id
        WHERE s.corps IS NOT NULL
        GROUP BY s.corps
        ORDER BY count DESC
    ''').fetchall()

    for row in corps_results:
        corps_data['labels'].append(row['corps'] or 'Not Specified')
        corps_data['values'].append(row['count'])

    return render_template('admin/reports.html',
                           registrations=registrations,
                           stats=stats,
                           quarters=quarters,
                           departments=departments,
                           courses=courses,
                           quarter_data=quarter_data,
                           department_data=department_data,
                           level_data=level_data,
                           corps_data=corps_data)

@admin_reports_bp.route('/export/<format>')
def export_report(format):
    """Export report in various formats"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get database connection
    db = get_db()

    # Get filter parameters
    quarter = request.args.get('quarter')
    department = request.args.get('department')
    course_id = request.args.get('course_id')

    # Build query for registrations
    query = '''
        SELECT sc.id, sc.registration_date, sc.status, sc.completion_date,
               s.service_number, s.rank, s.surname, s.other_names, s.corps, s.current_unit,
               c.name as course_name, c.department, c.level, c.quarter, c.year,
               c.start_date, c.end_date
        FROM student_courses sc
        JOIN students s ON sc.student_id = s.id
        JOIN courses c ON sc.course_id = c.id
        WHERE 1=1
    '''
    params = []

    if quarter:
        query += ' AND c.quarter = ?'
        params.append(quarter)

    if department:
        query += ' AND c.department = ?'
        params.append(department)

    if course_id:
        query += ' AND c.id = ?'
        params.append(course_id)

    query += ' ORDER BY sc.registration_date DESC'

    # Get registrations
    registrations = db.execute(query, params).fetchall()

    # Define column headers
    headers = [
        'Registration ID', 'Service Number', 'Rank', 'Surname', 'Other Names',
        'Corps', 'Unit', 'Course Name', 'Department', 'Level', 'Quarter', 'Year',
        'Course Start Date', 'Course End Date', 'Registration Date', 'Status', 'Completion Date'
    ]

    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if format == 'csv':
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(headers)

        # Write data
        for reg in registrations:
            writer.writerow([
                reg['id'], reg['service_number'], reg['rank'], reg['surname'], reg['other_names'],
                reg['corps'], reg['current_unit'], reg['course_name'], reg['department'], reg['level'],
                reg['quarter'], reg['year'], reg['start_date'], reg['end_date'],
                reg['registration_date'], reg['status'], reg['completion_date']
            ])

        # Prepare response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            download_name=f'nass_registrations_{timestamp}.csv',
            as_attachment=True
        )

    elif format == 'excel':
        if not XLSX_AVAILABLE:
            flash('Excel export is not available. Please install xlsxwriter module.', 'error')
            return redirect(url_for('admin_reports.index'))

        # Create Excel in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Registrations')

        # Add headers
        header_format = workbook.add_format({'bold': True, 'bg_color': '#3c78c3', 'color': 'white'})
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Add data
        for row, reg in enumerate(registrations, start=1):
            worksheet.write(row, 0, reg['id'])
            worksheet.write(row, 1, reg['service_number'])
            worksheet.write(row, 2, reg['rank'])
            worksheet.write(row, 3, reg['surname'])
            worksheet.write(row, 4, reg['other_names'])
            worksheet.write(row, 5, reg['corps'])
            worksheet.write(row, 6, reg['current_unit'])
            worksheet.write(row, 7, reg['course_name'])
            worksheet.write(row, 8, reg['department'])
            worksheet.write(row, 9, reg['level'])
            worksheet.write(row, 10, reg['quarter'])
            worksheet.write(row, 11, reg['year'])
            worksheet.write(row, 12, reg['start_date'])
            worksheet.write(row, 13, reg['end_date'])
            worksheet.write(row, 14, reg['registration_date'])
            worksheet.write(row, 15, reg['status'])
            worksheet.write(row, 16, reg['completion_date'])

        # Auto-adjust column widths
        for col, header in enumerate(headers):
            worksheet.set_column(col, col, len(header) + 5)

        workbook.close()

        # Prepare response
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name=f'nass_registrations_{timestamp}.xlsx',
            as_attachment=True
        )

    elif format == 'pdf':
        # For PDF, we'll redirect to a printable version that can be printed to PDF
        flash('Please use the Print button and save as PDF', 'info')
        return redirect(url_for('admin_reports.index', **request.args))

    else:
        flash('Invalid export format', 'error')
        return redirect(url_for('admin_reports.index'))
