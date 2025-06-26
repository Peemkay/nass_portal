"""
Production server script for NASS Portal
This script is used to run the application in production mode with gunicorn.
"""

import os
from nass_portal import create_app

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Create the application with production configuration
app = create_app('production')

if __name__ == '__main__':
    # This block will be executed when running this script directly
    # For production, we recommend using gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 production:app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
