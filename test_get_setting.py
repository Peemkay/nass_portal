from flask import Flask
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Create a Flask app
app = Flask(__name__)

# Set up the app context
with app.app_context():
    # Import the get_setting function
    from nass_portal.settings_utils import get_setting
    
    # Test the get_setting function
    maintenance_mode = get_setting('maintenance_mode', False)
    print(f"Maintenance Mode: {maintenance_mode}")
    
    # Test other settings
    site_title = get_setting('site_title', 'Default Title')
    print(f"Site Title: {site_title}")
    
    debug_mode = get_setting('debug_mode', False)
    print(f"Debug Mode: {debug_mode}")
