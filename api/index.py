import sys
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Add the application directory to the Python path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Import the application factory function
from nass_portal import create_app

# Create the application instance
app = create_app('production')

# This is important for Vercel
if __name__ == '__main__':
    app.run()