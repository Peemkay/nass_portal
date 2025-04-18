import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/nass_portal.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check the maintenance_mode setting
cursor.execute('SELECT * FROM settings WHERE setting_key = ?', ('maintenance_mode',))
setting = cursor.fetchone()

if setting:
    print(f"Setting ID: {setting['id']}")
    print(f"Setting Key: {setting['setting_key']}")
    print(f"Setting Value: {setting['setting_value']}")
    print(f"Setting Type: {setting['setting_type']}")
    print(f"Category: {setting['category']}")
    print(f"Description: {setting['description']}")
    print(f"Is Public: {setting['is_public']}")
else:
    print("Maintenance mode setting not found")

# Close the connection
conn.close()
