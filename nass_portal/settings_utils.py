import sqlite3
import json
import os
import shutil
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db

def get_setting(key, default=None):
    """
    Get a setting value by key

    Args:
        key (str): The setting key
        default: The default value to return if the setting doesn't exist

    Returns:
        The setting value or the default value
    """
    db = get_db()
    setting = db.execute('SELECT * FROM settings WHERE setting_key = ?', (key,)).fetchone()

    if not setting:
        return default

    # Convert the value based on the setting type
    if setting['setting_type'] == 'boolean':
        return setting['setting_value'].lower() == 'true'
    elif setting['setting_type'] == 'number':
        try:
            return int(setting['setting_value'])
        except (ValueError, TypeError):
            try:
                return float(setting['setting_value'])
            except (ValueError, TypeError):
                return 0
    elif setting['setting_type'] == 'json':
        try:
            return json.loads(setting['setting_value'])
        except (json.JSONDecodeError, TypeError):
            return {}

    # Default to returning the string value
    return setting['setting_value']

def get_settings_by_category(category):
    """
    Get all settings in a specific category

    Args:
        category (str): The category name

    Returns:
        A list of settings in the specified category
    """
    db = get_db()
    settings = db.execute(
        'SELECT * FROM settings WHERE category = ? ORDER BY id',
        (category,)
    ).fetchall()

    return settings

def get_all_settings():
    """
    Get all settings grouped by category

    Returns:
        A dictionary of settings grouped by category
    """
    from flask import current_app
    db = get_db()
    try:
        current_app.logger.info("Executing SQL query to get settings")
        settings = db.execute('SELECT * FROM settings ORDER BY category, id').fetchall()
        current_app.logger.info(f"Retrieved {len(settings)} settings")
    except Exception as e:
        current_app.logger.error(f"Error executing SQL query: {str(e)}")
        raise

    # Group settings by category
    grouped_settings = {}
    for setting in settings:
        category = setting['category']
        if category not in grouped_settings:
            grouped_settings[category] = []

        # Convert value based on type
        if setting['setting_type'] == 'boolean':
            setting = dict(setting)  # Convert from sqlite3.Row to dict
            setting['setting_value_parsed'] = setting['setting_value'].lower() == 'true'
        elif setting['setting_type'] == 'number':
            setting = dict(setting)
            try:
                setting['setting_value_parsed'] = int(setting['setting_value'])
            except (ValueError, TypeError):
                try:
                    setting['setting_value_parsed'] = float(setting['setting_value'])
                except (ValueError, TypeError):
                    setting['setting_value_parsed'] = 0

        grouped_settings[category].append(setting)

    return grouped_settings

def update_setting(key, value, setting_type='text', category='general', description='', is_public=0):
    """
    Update a setting value or create it if it doesn't exist

    Args:
        key (str): The setting key
        value: The new value
        setting_type (str): The type of setting (only used if creating a new setting)
        category (str): The category of the setting (only used if creating a new setting)
        description (str): Description of the setting (only used if creating a new setting)
        is_public (int): Whether the setting is public (only used if creating a new setting)

    Returns:
        bool: True if successful, False otherwise
    """
    from flask import current_app
    db = get_db()

    try:
        # Get the current setting to determine its type
        setting = db.execute('SELECT * FROM settings WHERE setting_key = ?', (key,)).fetchone()

        if setting:
            # Convert the value based on the setting type
            if setting['setting_type'] == 'boolean':
                value_str = str(value).lower() == 'true' and 'true' or 'false'
            elif setting['setting_type'] == 'json':
                try:
                    # If value is already a string, try to parse it as JSON to validate
                    if isinstance(value, str):
                        json.loads(value)
                        value_str = value
                    else:
                        # If value is a Python object, convert it to a JSON string
                        value_str = json.dumps(value)
                except (json.JSONDecodeError, TypeError):
                    return False
            else:
                # For text and number, just convert to string
                value_str = str(value)

            # Update the setting
            db.execute(
                'UPDATE settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?',
                (value_str, key)
            )
        else:
            # Setting doesn't exist, create it
            current_app.logger.info(f"Creating new setting: {key} = {value} (type: {setting_type}, category: {category})")

            # For new settings, convert value to string based on the provided type
            if setting_type == 'boolean':
                value_str = str(value).lower() == 'true' and 'true' or 'false'
            elif setting_type == 'json':
                try:
                    if isinstance(value, str):
                        json.loads(value)
                        value_str = value
                    else:
                        value_str = json.dumps(value)
                except (json.JSONDecodeError, TypeError):
                    return False
            else:
                value_str = str(value)

            # Insert the new setting
            db.execute(
                '''INSERT INTO settings (
                    setting_key, setting_value, setting_type,
                    category, description, is_public, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                (key, value_str, setting_type, category, description, is_public)
            )

        db.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error updating setting {key}: {str(e)}")
        return False

def update_settings(settings_dict):
    """
    Update multiple settings at once

    Args:
        settings_dict (dict): A dictionary of setting keys and values

    Returns:
        tuple: (success_count, total_count)
    """
    success_count = 0
    total_count = len(settings_dict)

    for key, value in settings_dict.items():
        if update_setting(key, value):
            success_count += 1

    return success_count, total_count

def reset_settings():
    """
    Reset all settings to their default values

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_db()

        # Get the path to the schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Read the schema file to extract default settings
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Extract the INSERT INTO settings statement
        import re
        insert_pattern = r"INSERT INTO settings \(.*?\) VALUES(.*?);"
        match = re.search(insert_pattern, schema_sql, re.DOTALL)

        if not match:
            return False

        # Delete all current settings
        db.execute('DELETE FROM settings')

        # Re-run the INSERT statement
        insert_sql = f"INSERT INTO settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES{match.group(1)};"
        db.executescript(insert_sql)
        db.commit()

        return True
    except (sqlite3.Error, IOError):
        return False

def change_admin_password(admin_id, current_password, new_password):
    """
    Change an admin's password

    Args:
        admin_id (int): The admin ID
        current_password (str): The current password
        new_password (str): The new password

    Returns:
        tuple: (success, message)
    """
    db = get_db()

    # Get the admin
    admin = db.execute('SELECT * FROM admins WHERE id = ?', (admin_id,)).fetchone()
    if not admin:
        return False, "Admin not found"

    # Check the current password
    if not check_password_hash(admin['password'], current_password):
        return False, "Current password is incorrect"

    # Validate the new password
    min_length = get_setting('password_min_length', 8)
    if len(new_password) < min_length:
        return False, f"New password must be at least {min_length} characters long"

    # Update the password
    try:
        hashed_password = generate_password_hash(new_password)
        db.execute(
            'UPDATE admins SET password = ? WHERE id = ?',
            (hashed_password, admin_id)
        )
        db.commit()
        return True, "Password changed successfully"
    except sqlite3.Error:
        return False, "Database error occurred"

def backup_database():
    """
    Create a backup of the database

    Returns:
        tuple: (success, message, backup_path)
    """
    try:
        # Get the path to the database file
        db_path = os.path.join('instance', 'nass_portal.db')

        # Create a backup directory if it doesn't exist
        backup_dir = os.path.join('instance', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Create a backup filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Copy the database file
        shutil.copy2(db_path, backup_path)

        return True, "Database backup created successfully", backup_path
    except Exception as e:
        return False, f"Error creating database backup: {str(e)}", None

def restore_database(backup_path):
    """
    Restore the database from a backup

    Args:
        backup_path (str): Path to the backup file

    Returns:
        tuple: (success, message)
    """
    try:
        # Get the path to the database file
        db_path = os.path.join('instance', 'nass_portal.db')

        # Create a backup of the current database before restoring
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = os.path.join('instance', 'backups', f"pre_restore_backup_{timestamp}.db")
        os.makedirs(os.path.dirname(pre_restore_backup), exist_ok=True)
        shutil.copy2(db_path, pre_restore_backup)

        # Restore the database
        shutil.copy2(backup_path, db_path)

        return True, "Database restored successfully"
    except Exception as e:
        return False, f"Error restoring database: {str(e)}"

def get_database_backups():
    """
    Get a list of database backups

    Returns:
        list: A list of backup files with metadata
    """
    backup_dir = os.path.join('instance', 'backups')
    if not os.path.exists(backup_dir):
        return []

    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.db'):
            file_path = os.path.join(backup_dir, filename)
            file_stats = os.stat(file_path)

            # Extract timestamp from filename or use file modification time
            timestamp = None
            import re
            match = re.search(r'database_backup_(\d{8}_\d{6})\.db', filename)
            if match:
                try:
                    timestamp = datetime.datetime.strptime(match.group(1), '%Y%m%d_%H%M%S')
                except ValueError:
                    pass

            if not timestamp:
                timestamp = datetime.datetime.fromtimestamp(file_stats.st_mtime)

            backups.append({
                'filename': filename,
                'path': file_path,
                'size': file_stats.st_size,
                'timestamp': timestamp,
                'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'formatted_size': format_file_size(file_stats.st_size)
            })

    # Sort backups by timestamp (newest first)
    backups.sort(key=lambda x: x['timestamp'], reverse=True)

    return backups

def format_file_size(size_bytes):
    """
    Format a file size in bytes to a human-readable string

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
