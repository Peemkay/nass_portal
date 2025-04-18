"""
Script to fix mail settings in the database
"""

import os
import sys
import sqlite3

# Connect to the database
db_path = os.path.join('instance', 'nass_portal.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Yahoo Mail settings
mail_settings = {
    'mail_server': 'smtp.mail.yahoo.com',
    'mail_port': '587',
    'mail_use_tls': 'true',
    'mail_use_ssl': 'false',
    'mail_username': 'chakin700@yahoo.com',
    'mail_password': 'xswwpjaotwholron',
    'mail_default_sender': 'chakin700@yahoo.com',
    'mail_sender_name': 'NASS Portal',
    'mail_contact_form_enabled': 'true',
    'mail_contact_form_recipients': 'chakin700@yahoo.com',
    'mail_contact_form_subject_prefix': '[NASS Portal Contact]'
}

# First, check if the mail settings exist
cursor.execute('SELECT COUNT(*) FROM settings WHERE category = ?', ('mail',))
count = cursor.fetchone()[0]

if count == 0:
    print("No mail settings found. Creating new settings...")

    # Insert mail settings
    for key, value in mail_settings.items():
        setting_type = 'boolean' if key in ['mail_use_tls', 'mail_use_ssl', 'mail_contact_form_enabled'] else 'text'
        if key == 'mail_port':
            setting_type = 'number'

        cursor.execute(
            'INSERT INTO settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES (?, ?, ?, ?, ?, ?)',
            (key, value, setting_type, 'mail', f'Mail setting: {key}', 0)
        )
else:
    print(f"Found {count} mail settings. Updating...")

    # Update existing settings
    for key, value in mail_settings.items():
        cursor.execute(
            'UPDATE settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?',
            (value, key)
        )

        if cursor.rowcount == 0:
            print(f"Setting {key} not found. Creating...")
            setting_type = 'boolean' if key in ['mail_use_tls', 'mail_use_ssl', 'mail_contact_form_enabled'] else 'text'
            if key == 'mail_port':
                setting_type = 'number'

            cursor.execute(
                'INSERT INTO settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES (?, ?, ?, ?, ?, ?)',
                (key, value, setting_type, 'mail', f'Mail setting: {key}', 0)
            )

# Commit the changes
conn.commit()

# Verify the settings
cursor.execute('SELECT setting_key, setting_value, setting_type FROM settings WHERE category = ?', ('mail',))
settings = cursor.fetchall()

print("\nCurrent mail settings:")
for setting in settings:
    if setting['setting_key'] != 'mail_password':
        print(f"{setting['setting_key']} = {setting['setting_value']} (type: {setting['setting_type']})")
    else:
        print(f"{setting['setting_key']} = ******** (type: {setting['setting_type']})")

conn.close()

print("\nMail settings updated successfully!")
print("Please restart the application for the changes to take effect.")
