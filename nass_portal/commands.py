import click
from flask.cli import with_appcontext
from .db import init_db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    init_db()
    click.echo('Initialized the database.')

