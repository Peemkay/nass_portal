import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from .db import get_db, init_db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    init_db()
    click.echo('Initialized the database.')

@click.command('init-admin')
@with_appcontext
def init_admin_command():
    """Initialize admin user."""
    db = get_db()
    
    # Create admin user
    username = 'admin'
    password = 'admin123'  # Change this in production!
    hashed_password = generate_password_hash(password)
    
    try:
        db.execute('INSERT OR REPLACE INTO admins (username, password) VALUES (?, ?)',
                  (username, hashed_password))
        db.commit()
        click.echo('Admin user created successfully')
        click.echo(f'Username: {username}')
        click.echo(f'Password: {password}')
    except Exception as e:
        click.echo(f'Error creating admin: {e}')

def init_app(app):
    """Register commands."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_admin_command)

