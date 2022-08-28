# App info
__version__ = '2.0.0' # Server version, not Improved Intra version
__target_ext_version__ = '3.4.0' # Targeting Improved Intra extension version
__author__ = 'Freek Bes'

# Imports
import platform
import logging

# Import specifics
from werkzeug import __version__ as __werkzeug_version__
from flask import Flask, request, __version__ as __flask_version__
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
from .lib.config import config

# Set up DB uri
config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}"

# Set up logging
logging.basicConfig(filename=config['LOG_FILE_SERVER'], level=logging.DEBUG, format=config['LOG_FORMAT'])

# Set up Flask
print('Initializing Flask...')
app = Flask(__name__)
app.config.from_mapping(config)
app.secret_key = config['SESSION_KEY']
db = SQLAlchemy(app)
print('Flask initialized')

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
	response.headers['X-Powered-By'] = 'ImprovedIntraServer/{} Werkzeug/{} Flask/{} Python/{}'.format(__version__, __werkzeug_version__, __flask_version__, platform.python_version())
	response.headers['X-Target-Version'] = 'ImprovedIntra/{}'.format(__target_ext_version__)

	origin = request.environ.get('HTTP_ORIGIN', None)
	if origin is not None:
		origin_host = urlparse(origin).hostname
		if origin_host is not None and (origin_host == 'intra.42.fr' or origin_host.endswith('.intra.42.fr')):
			response.headers['Access-Control-Allow-Origin'] = 'https://{}'.format(origin_host)
			response.headers['X-Frame-Options'] = 'allow-from'

	return response
