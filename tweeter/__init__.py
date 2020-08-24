from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SECRET_KEY'] = 'dcef3fd2f3a917dda52f56ed46ddea37'
app.config['DATABASE_URL'] = 'postgresql:///tweeter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

import click
from flask.cli import with_appcontext

from tweeter.models import User, Tweet

@click.command('create-tables')
@with_appcontext
def create_tables():
    db.create_all()


from tweeter import routes
from tweeter import commands