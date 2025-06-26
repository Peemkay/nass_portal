"""
This is a fixed version of the problematic line in routes.py
"""

# The correct code should be:
# Generate unique filename
filename = secure_filename(document_file.filename)
file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

# Sanitize service number to avoid path issues
service_number = str(session.get('service_number', '')).replace('/', '_').replace('\\', '_')
unique_filename = f"{service_number}_{req['id']}_{int(time.time())}.{file_ext}"
