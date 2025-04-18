import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/nass_portal.db')
cursor = conn.cursor()

# Update the maintenance_mode setting to true
cursor.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('true', 'maintenance_mode'))
conn.commit()

# Verify the update
cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_mode',))
value = cursor.fetchone()[0]
print(f"Maintenance mode is now set to: {value}")

# Close the connection
conn.close()
