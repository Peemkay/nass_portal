"""
WSGI entry point for Nigerian Army School of Signals Portal

This file is used by WSGI servers like Gunicorn or uWSGI to serve the application.
For deployment on platforms like PythonAnywhere, Heroku, or other WSGI-compatible servers.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Add the application directory to the Python path
# Change this path to your actual deployment path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Import the application factory function
from nass_portal import create_app

# Create the application instance
application = create_app('production')

# For compatibility with some WSGI servers that look for 'app'
app = application

if __name__ == "__main__":
    # This block will be executed when running directly with Python
    # It's useful for development and testing
    app.run(host='0.0.0.0', port=5000)