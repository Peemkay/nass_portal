"""
Development server script for Nigerian Army School of Signals Portal

This script is used to run the application in development mode.
For production deployment, use a proper WSGI server like Gunicorn or uWSGI.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Using default environment variables.")

# Import the application factory function
from nass_portal import create_app

# Get environment from environment variable or default to development
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Get port from command line arguments or default to 5000
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 5000.")

    # In production mode, we use different settings
    if env == 'production':
        print(f"Running in PRODUCTION mode on port {port}")
        print("WARNING: This is not recommended for production deployment.")
        print("Use a proper WSGI server like Gunicorn or uWSGI instead.")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    else:
        print(f"Running in DEVELOPMENT mode on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
