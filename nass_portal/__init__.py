from flask import Flask
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key"
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Initialize extensions
    mail.init_app(app)
    
    # Database configuration
    app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    
    from . import db
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    return app

app = create_app()






