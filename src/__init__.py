from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import func
import os
import platform
from dotenv import dotenv_values

# Load config from .env files
config = {
	**dotenv_values(".shared.env", verbose=True),  # load shared development variables
	**dotenv_values(".secret.env", verbose=True),  # load sensitive variables
	**os.environ,  # override loaded values with environment variables
}
config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}"

# Set up Flask
print('Initializing Flask...')
app = Flask(__name__)
app.config.from_mapping(config)
app.secret_key = config['SESSION_KEY']
db = SQLAlchemy(app)
print('Flask initialized')

# Set up database
if not database_exists(db.engine.url):
	print('Database \'iintra\' does not exist, creating...')
	if 'microsoft' in platform.uname()[2].lower():
		print('You are using Microsoft\'s Windows Subsystem for Linux, which under WSL1 has problems with PostgreSQL.')
		print('If the program hangs here, you will need to switch to WSL2 to continue.')
	create_database(db.engine.url, encoding='utf8', template='template0')
	print('Database created')

# Set up tables
print('Initializing database models...')
from src import models
db.create_all()
db.session.commit()
print('Database models initialized')

# Set up default content
print('Initializing default content...')
from src import defaults
defaults.populate_banner_pos(db.session)
defaults.populate_color_schemes(db.session)
print('Default content initialized')

# Import routes
from src.v1 import routes
from src.v2 import routes
from . import oauth
