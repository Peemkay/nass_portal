import click
import os
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

@click.command('init-maintenance')
@with_appcontext
def init_maintenance_command():
    """Initialize maintenance schema."""
    db = get_db()

    try:
        # Read the maintenance schema file
        with open(os.path.join(os.path.dirname(__file__), 'maintenance_schema.sql'), 'r') as f:
            schema = f.read()

        # Execute the schema
        db.executescript(schema)
        db.commit()
        click.echo('Maintenance schema initialized successfully')
    except Exception as e:
        click.echo(f'Error initializing maintenance schema: {e}')

@click.command('apply-schema-updates')
@with_appcontext
def apply_schema_updates_command():
    """Apply schema updates from schema_updates.sql."""
    db = get_db()

    # Get the schema updates file path
    schema_updates_path = os.path.join(os.path.dirname(__file__), 'schema_updates.sql')

    # Check if the file exists
    if not os.path.exists(schema_updates_path):
        click.echo('Schema updates file not found.')
        return

    # Read the schema updates file
    with open(schema_updates_path, 'r') as f:
        schema_updates = f.read()

    # Split the schema updates into individual statements
    statements = schema_updates.split(';')

    # Execute each statement
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                db.execute(statement)
                db.commit()
            except Exception as e:
                db.rollback()
                click.echo(f'Error executing statement: {e}')
                click.echo(f'Statement: {statement}')

    click.echo('Schema updates applied successfully.')

def init_app(app):
    """Register commands."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_admin_command)
    app.cli.add_command(init_maintenance_command)
    app.cli.add_command(apply_schema_updates_command)

