"""
Admin routes for quarters management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from datetime import datetime
from .db import get_db

admin_quarters_bp = Blueprint('admin_quarters', __name__, url_prefix='/admin/quarters')

@admin_quarters_bp.route('/')
def index():
    """Quarters management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    # Get database connection
    db = get_db()
    
    # Get filter parameters
    year = request.args.get('year')
    status = request.args.get('status')
    
    # Build query
    query = 'SELECT * FROM registration_quarters WHERE 1=1'
    params = []
    
    if year:
        query += ' AND year = ?'
        params.append(int(year))
    
    if status:
        query += ' AND is_active = ?'
        params.append(int(status))
    
    query += ' ORDER BY year DESC, name'
    
    # Get quarters
    quarters = db.execute(query, params).fetchall()
    
    # Get years for filter
    years = db.execute('SELECT DISTINCT year FROM registration_quarters ORDER BY year DESC').fetchall()
    years = [year['year'] for year in years]
    
    # Get current year
    current_year = datetime.now().year
    
    # Get current date for comparison
    now = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('admin/quarters.html', 
                           quarters=quarters, 
                           years=years, 
                           current_year=current_year,
                           now=now)

@admin_quarters_bp.route('/add', methods=['POST'])
def add_quarter():
    """Add a new quarter"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        year = request.form.get('year')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        is_active = 'is_active' in request.form
        
        # Validate required fields
        if not name or not year or not start_date or not end_date or not registration_deadline:
            flash('All fields are required', 'error')
            return redirect(url_for('admin_quarters.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # If this quarter is active, deactivate all others
            if is_active:
                db.execute('UPDATE registration_quarters SET is_active = 0')
            
            # Insert quarter
            db.execute('''
                INSERT INTO registration_quarters (
                    name, year, start_date, end_date, registration_deadline, is_active
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                name, year, start_date, end_date, registration_deadline, is_active
            ))
            
            db.commit()
            flash('Quarter added successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error adding quarter: {str(e)}")
            flash(f'Error adding quarter: {str(e)}', 'error')
        
        return redirect(url_for('admin_quarters.index'))

@admin_quarters_bp.route('/edit', methods=['POST'])
def edit_quarter():
    """Edit a quarter"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        # Get form data
        quarter_id = request.form.get('quarter_id')
        name = request.form.get('name')
        year = request.form.get('year')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        registration_deadline = request.form.get('registration_deadline')
        is_active = 'is_active' in request.form
        
        # Validate required fields
        if not quarter_id or not name or not year or not start_date or not end_date or not registration_deadline:
            flash('All fields are required', 'error')
            return redirect(url_for('admin_quarters.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # If this quarter is active, deactivate all others
            if is_active:
                db.execute('UPDATE registration_quarters SET is_active = 0')
            
            # Update quarter
            db.execute('''
                UPDATE registration_quarters SET
                    name = ?, year = ?, start_date = ?, end_date = ?, 
                    registration_deadline = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                name, year, start_date, end_date, registration_deadline, is_active, quarter_id
            ))
            
            db.commit()
            flash('Quarter updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error updating quarter: {str(e)}")
            flash(f'Error updating quarter: {str(e)}', 'error')
        
        return redirect(url_for('admin_quarters.index'))

@admin_quarters_bp.route('/delete', methods=['POST'])
def delete_quarter():
    """Delete a quarter"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        quarter_id = request.form.get('quarter_id')
        
        if not quarter_id:
            flash('Quarter ID is required', 'error')
            return redirect(url_for('admin_quarters.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # Check if there are courses associated with this quarter
            quarter = db.execute('SELECT * FROM registration_quarters WHERE id = ?', (quarter_id,)).fetchone()
            
            if not quarter:
                flash('Quarter not found', 'error')
                return redirect(url_for('admin_quarters.index'))
            
            course_count = db.execute(
                'SELECT COUNT(*) as count FROM courses WHERE quarter = ? AND year = ?', 
                (quarter['name'], quarter['year'])
            ).fetchone()['count']
            
            if course_count > 0:
                flash(f'Cannot delete quarter: {course_count} courses are associated with this quarter', 'error')
                return redirect(url_for('admin_quarters.index'))
            
            # Delete quarter
            db.execute('DELETE FROM registration_quarters WHERE id = ?', (quarter_id,))
            db.commit()
            flash('Quarter deleted successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error deleting quarter: {str(e)}")
            flash(f'Error deleting quarter: {str(e)}', 'error')
        
        return redirect(url_for('admin_quarters.index'))

@admin_quarters_bp.route('/activate', methods=['POST'])
def activate_quarter():
    """Activate a quarter"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        quarter_id = request.form.get('quarter_id')
        
        if not quarter_id:
            flash('Quarter ID is required', 'error')
            return redirect(url_for('admin_quarters.index'))
        
        # Get database connection
        db = get_db()
        
        try:
            # Deactivate all quarters
            db.execute('UPDATE registration_quarters SET is_active = 0')
            
            # Activate the selected quarter
            db.execute('UPDATE registration_quarters SET is_active = 1 WHERE id = ?', (quarter_id,))
            db.commit()
            
            flash('Quarter activated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f"Error activating quarter: {str(e)}")
            flash(f'Error activating quarter: {str(e)}', 'error')
        
        return redirect(url_for('admin_quarters.index'))

@admin_quarters_bp.route('/get-quarter-data')
def get_quarter_data():
    """Get quarter data for editing"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    quarter_id = request.args.get('quarter_id')
    
    if not quarter_id:
        return jsonify({'success': False, 'message': 'Quarter ID is required'})
    
    # Get database connection
    db = get_db()
    
    try:
        # Get quarter
        quarter = db.execute('SELECT * FROM registration_quarters WHERE id = ?', (quarter_id,)).fetchone()
        
        if not quarter:
            return jsonify({'success': False, 'message': 'Quarter not found'})
        
        # Convert to dict
        quarter_dict = dict(quarter)
        
        return jsonify({'success': True, 'quarter': quarter_dict})
    except Exception as e:
        current_app.logger.error(f"Error getting quarter data: {str(e)}")
        return jsonify({'success': False, 'message': f'Error getting quarter data: {str(e)}'})
