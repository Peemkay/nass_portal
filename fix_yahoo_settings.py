"""
Script to fix Yahoo Mail settings
"""

import os
import sys
import sqlite3

# Connect to the database
db_path = os.path.join('instance', 'nass_portal.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Set your Yahoo email address here
yahoo_email = "your_actual_yahoo_email@yahoo.com"  # Replace with your actual Yahoo email

# Yahoo Mail settings
mail_settings = {
    'mail_server': 'smtp.mail.yahoo.com',
    'mail_port': '587',
    'mail_use_tls': 'true',
    'mail_use_ssl': 'false',
    'mail_username': yahoo_email,
    'mail_password': 'xswwpjaotwholron',  # The app password you provided
    'mail_default_sender': yahoo_email,
    'mail_sender_name': 'NASS Portal',
    'mail_contact_form_enabled': 'true',
    'mail_contact_form_recipients': yahoo_email,
    'mail_contact_form_subject_prefix': '[NASS Portal Contact]'
}

# Update each setting
for key, value in mail_settings.items():
    cursor.execute(
        'UPDATE settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?',
        (value, key)
    )
    
    # If the setting doesn't exist, insert it
    if cursor.rowcount == 0:
        setting_type = 'boolean' if key in ['mail_use_tls', 'mail_use_ssl', 'mail_contact_form_enabled'] else 'text'
        if key == 'mail_port':
            setting_type = 'number'
            
        cursor.execute(
            'INSERT INTO settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES (?, ?, ?, ?, ?, ?)',
            (key, value, setting_type, 'mail', f'Mail setting: {key}', 0)
        )

# Commit the changes
conn.commit()
conn.close()

print(f"Mail settings updated successfully with email: {yahoo_email}")
print("Please restart the application for the changes to take effect.")
