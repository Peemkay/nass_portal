# Nigerian Army School of Signals Portal

A comprehensive web portal for the Nigerian Army School of Signals, providing course registration, student management, and administrative capabilities.

## Features

- **Student Registration**: Complete multi-step registration process for students
- **Student Portal**: Secure access to course history, certificates, and profile management
- **Course Management**: Comprehensive course creation and management
- **Admin Dashboard**: Full administrative control over all aspects of the portal
- **Document Management**: Upload and manage student documents
- **Certificate Management**: Generate and distribute course certificates
- **Responsive Design**: Mobile-friendly interface for all users

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLite (can be upgraded to PostgreSQL or MySQL for production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Custom authentication system with password hashing
- **Email**: SMTP integration for notifications

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Setup Instructions

1. **Clone the repository** (or download and extract the ZIP file):
   ```bash
   git clone https://github.com/yourusername/nass_portal.git
   cd nass_portal
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment variables**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file with your configuration

6. **Initialize the database**:
   ```bash
   python initialize_app.py
   ```
   - Follow the prompts to create an admin user

7. **Run the application**:
   ```bash
   python run.py
   ```

8. **Access the application**:
   - Open a web browser and navigate to `http://localhost:5000`
   - Admin dashboard is available at `http://localhost:5000/admin`

## Deployment

### PythonAnywhere Deployment

1. **Create a PythonAnywhere account** at [pythonanywhere.com](https://www.pythonanywhere.com/)

2. **Upload your code**:
   - Use the PythonAnywhere Files tab to upload a ZIP of your project, or
   - Clone from GitHub using the Bash console:
     ```bash
     git clone https://github.com/yourusername/nass_portal.git
     ```

3. **Set up a virtual environment**:
   ```bash
   cd nass_portal
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Create a `.env` file in your project directory
   - Set all required environment variables

5. **Initialize the database**:
   ```bash
   python initialize_app.py
   ```

6. **Configure the web app**:
   - Go to the Web tab in PythonAnywhere
   - Add a new web app
   - Select "Manual configuration" and Python 3.8 (or your version)
   - Set the path to your project directory
   - Set the WSGI configuration file to point to your `wsgi.py`

7. **Reload the web app** to apply changes

### Other Deployment Options

- **Heroku**: Use the Procfile and requirements.txt for deployment
- **Docker**: A Dockerfile is provided for containerized deployment
- **Traditional Hosting**: Use any WSGI-compatible server like Gunicorn or uWSGI

## Project Structure

```
nass_portal/
├── instance/                  # Instance-specific data (database)
├── nass_portal/               # Application package
│   ├── static/                # Static files (CSS, JS, images)
│   ├── templates/             # HTML templates
│   ├── __init__.py            # Application factory
│   ├── admin_routes.py        # Admin routes
│   ├── config.py              # Configuration
│   ├── db.py                  # Database functions
│   ├── routes.py              # Main routes
│   ├── schema.sql             # Database schema
│   ├── schema_updates.sql     # Schema updates
│   └── student_routes.py      # Student portal routes
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── initialize_app.py          # Database initialization script
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── run.py                     # Development server script
└── wsgi.py                    # WSGI entry point for production
```

## Maintenance

### Database Backups

It's recommended to regularly back up the SQLite database file:

```bash
# Create a timestamped backup
cp instance/nass_portal.sqlite instance/nass_portal_backup_$(date +%Y%m%d_%H%M%S).sqlite
```

### Updates

To update the application:

1. Pull the latest code or upload the new version
2. Activate the virtual environment
3. Install any new dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply any database migrations:
   ```bash
   python -c "from nass_portal.db import get_db; db = get_db(); with open('nass_portal/schema_updates.sql') as f: db.executescript(f.read()); db.commit()"
   ```
5. Restart the application

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For support or inquiries, please contact the Nigerian Army School of Signals administration.
