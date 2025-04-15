from nass_portal import create_app
from nass_portal.db import init_db

def main():
    app = create_app()
    with app.app_context():
        init_db()
        print("Database initialized successfully with the updated schema.")

if __name__ == '__main__':
    main()
