from flask import Flask
from flask_mail import Mail
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    if not app.debug:
        file_handler = RotatingFileHandler('nass_portal.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('NASS Portal startup')
    
    app.secret_key = os.environ.get('SECRET_KEY', 'dev')  # Change this in production!
    
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
    app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize database
    from . import db
    db.init_app(app)
    
    # Register commands
    from . import commands
    commands.init_app(app)
    
    # Register blueprint
    from .routes import bp
    app.register_blueprint(bp)
    
    return app

app = create_app()






