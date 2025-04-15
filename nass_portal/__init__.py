from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
import logging
import sys
import os
from nass_portal.config import Config  # Update this import

# Load environment variables
load_dotenv()

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    if not app.debug:
        try:
            # Use a stream handler instead of file handler to avoid permission issues
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('NASS Portal startup')
        except Exception as e:
            print(f"Logging setup error: {e}")

    # Initialize extensions
    mail.init_app(app)

    # Ensure instance and upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

    # Initialize database
    from . import db
    db.init_app(app)

    # Register commands
    from . import commands
    commands.init_app(app)

    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)

    # Register admin blueprint
    from .admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    @app.context_processor
    def utility_processor():
        return dict(len=len)

    return app

app = create_app()






