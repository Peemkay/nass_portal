import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'

    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Database configuration
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'nass_portal.db')

    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'uploads')

    # Debug configuration
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Production-specific settings
    DEBUG = False

    # Use a more secure secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # Configure logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'true').lower() in ['true', 'yes', '1']

    # Configure server
    SERVER_NAME = os.environ.get('SERVER_NAME')

    # Configure security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

# Dictionary to map environment names to config classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}