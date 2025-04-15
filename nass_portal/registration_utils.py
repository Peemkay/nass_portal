"""
Utility functions for registration management
"""

from datetime import datetime
from flask import current_app
from .db import get_db

def get_active_registration_period():
    """
    Get the currently active registration period
    
    Returns:
        dict: Active registration period or None if no active period
    """
    db = get_db()
    period = db.execute(
        'SELECT * FROM registration_periods WHERE is_active = 1 LIMIT 1'
    ).fetchone()
    
    return period

def is_registration_open():
    """
    Check if registration is currently open
    
    Returns:
        bool: True if registration is open, False otherwise
    """
    period = get_active_registration_period()
    
    if not period:
        return False
    
    today = datetime.now().date()
    start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
    
    return start_date <= today <= end_date

def get_registration_status():
    """
    Get detailed registration status
    
    Returns:
        dict: Registration status information
    """
    period = get_active_registration_period()
    
    if not period:
        return {
            'is_open': False,
            'message': 'Registration is currently closed.',
            'period': None
        }
    
    today = datetime.now().date()
    start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
    
    is_open = start_date <= today <= end_date
    
    if today < start_date:
        message = f"Registration for {period['quarter'].title()} Quarter {period['year']} will open on {period['start_date']}."
    elif today > end_date:
        message = f"Registration for {period['quarter'].title()} Quarter {period['year']} closed on {period['end_date']}."
    else:
        days_left = (end_date - today).days
        message = f"Registration for {period['quarter'].title()} Quarter {period['year']} is open. {days_left} days remaining until deadline ({period['end_date']})."
    
    return {
        'is_open': is_open,
        'message': message,
        'period': dict(period)
    }

def get_all_registration_periods():
    """
    Get all registration periods
    
    Returns:
        list: All registration periods
    """
    db = get_db()
    periods = db.execute(
        'SELECT * FROM registration_periods ORDER BY year DESC, CASE quarter '
        'WHEN "first" THEN 1 '
        'WHEN "second" THEN 2 '
        'WHEN "third" THEN 3 '
        'ELSE 4 END'
    ).fetchall()
    
    return [dict(period) for period in periods]

def update_registration_period(period_id, data):
    """
    Update a registration period
    
    Args:
        period_id (int): ID of the period to update
        data (dict): Updated data
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = get_db()
    
    # If setting this period as active, deactivate all others
    if data.get('is_active'):
        db.execute('UPDATE registration_periods SET is_active = 0')
    
    # Update the specified period
    db.execute(
        'UPDATE registration_periods SET '
        'quarter = ?, year = ?, start_date = ?, end_date = ?, '
        'is_active = ?, description = ?, updated_at = CURRENT_TIMESTAMP '
        'WHERE id = ?',
        (
            data.get('quarter'),
            data.get('year'),
            data.get('start_date'),
            data.get('end_date'),
            1 if data.get('is_active') else 0,
            data.get('description'),
            period_id
        )
    )
    
    db.commit()
    return True

def add_registration_period(data):
    """
    Add a new registration period
    
    Args:
        data (dict): Period data
        
    Returns:
        int: ID of the new period
    """
    db = get_db()
    
    # If setting this period as active, deactivate all others
    if data.get('is_active'):
        db.execute('UPDATE registration_periods SET is_active = 0')
    
    cursor = db.execute(
        'INSERT INTO registration_periods '
        '(quarter, year, start_date, end_date, is_active, description) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (
            data.get('quarter'),
            data.get('year'),
            data.get('start_date'),
            data.get('end_date'),
            1 if data.get('is_active') else 0,
            data.get('description')
        )
    )
    
    db.commit()
    return cursor.lastrowid

def delete_registration_period(period_id):
    """
    Delete a registration period
    
    Args:
        period_id (int): ID of the period to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = get_db()
    db.execute('DELETE FROM registration_periods WHERE id = ?', (period_id,))
    db.commit()
    return True
