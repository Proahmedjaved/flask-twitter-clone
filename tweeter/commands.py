import click
from flask.cli import with_appcontext

from tweeter import db
from tweeter.models import User, Tweet


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()