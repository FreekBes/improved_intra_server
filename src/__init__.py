# App info
__version__ = '2.0.0' # Server version, not Improved Intra version
__target_ext_version__ = '3.4.0' # Targeting Improved Intra extension version
__author__ = 'Freek Bes'

# Imports
import os
import platform
from werkzeug import __version__ as __werkzeug_version__
from flask import Flask, request, __version__ as __flask_version__
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import func
from urllib.parse import urlparse
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

# Set up headers
@app.after_request
def add_headers(response):
	response.headers['X-Frame-Options'] = 'sameorigin'
	response.headers['Vary'] = 'Origin'
	response.headers['X-Content-Type-Options'] = 'nosniff'
	response.headers['X-Powered-By'] = 'Werkzeug/{} Flask/{} Python/{}'.format(__werkzeug_version__, __flask_version__, platform.python_version())
	response.headers['X-Target-Version'] = 'ImprovedIntra/{}'.format(__target_ext_version__)
	response.headers['Server'] = 'ImprovedIntraServer/{}'.format(__version__)

	origin = request.environ.get('HTTP_ORIGIN', None)
	if origin is not None:
		origin_host = urlparse(origin).hostname
		if origin_host is not None and (origin_host == 'intra.42.fr' or origin_host.endswith('.intra.42.fr')):
			response.headers['Access-Control-Allow-Origin'] = 'https://{}'.format(origin_host)
			response.headers['X-Frame-Options'] = 'allow-from'

	return response
