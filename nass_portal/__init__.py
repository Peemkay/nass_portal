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
    try:
        # Use a stream handler instead of file handler to avoid permission issues
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        stream_handler.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs
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

    # Register middleware for maintenance mode
    from .middleware import check_maintenance_mode
    @app.before_request
    def before_request():
        maintenance_response = check_maintenance_mode()
        if maintenance_response:
            return maintenance_response

    # Always start maintenance scheduler
    try:
        from .maintenance_tasks import start_scheduler
        start_scheduler()
        app.logger.info('Maintenance scheduler started')
    except Exception as e:
        app.logger.error(f'Error starting maintenance scheduler: {e}')

    @app.context_processor
    def utility_processor():
        return dict(len=len)

    # Add custom Jinja2 filters
    @app.template_filter('strptime')
    def _jinja2_filter_strptime(date_string, format_string):
        from datetime import datetime
        return datetime.strptime(date_string, format_string)

    @app.template_filter('now')
    def _jinja2_filter_now():
        from datetime import datetime
        return datetime.now()

    return app

app = create_app()






