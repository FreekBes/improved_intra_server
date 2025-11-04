# App info
__version__ = '3.3.2' # Server version, not Improved Intra version
__target_ext_version__ = '4.4.2' # Targeting Improved Intra extension version
__author__ = 'Freek Bes'

# Imports
import platform
import logging

# Import specifics
from werkzeug import __version__ as __werkzeug_version__
from flask import Flask, request, __version__ as __flask_version__
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse

from src.lib.config import config

# Set up DB uri
config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}"

# Prevent Internal Server Error (Flask is stupid)
config['MAX_CONTENT_LENGTH'] = int(config['MAX_CONTENT_LENGTH'])

# Set up logging
logging.basicConfig(filename=config['LOG_FILE_SERVER'], level=logging.DEBUG, format=config['LOG_FORMAT'])

# Set up Flask
print('Initializing Flask...')
app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='templates')
app.config.from_mapping(config)
app.secret_key = config['SESSION_KEY']
# Uncomment the following line to echo queries for debugging
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
print('Flask initialized')

# Import routes
from src.v1 import routes as v1routes
from src.v2.routes.banners import *
from src.v2.routes.sessions import *
from src.v2.routes.options.get import *
from src.v2.routes.options.set import *
from src.v2.routes.options.json import *
from src.v2.routes.home import *
from src.v2.routes.takeout import *
from src.v2.routes.events import *
from src.lib import utilities
from src.lib.auth import oauth

# Set up headers
@app.after_request
def add_headers(response:Response):
	response.headers['X-Frame-Options'] = 'sameorigin'
	response.headers['Vary'] = 'Origin'
	response.headers['X-Content-Type-Options'] = 'nosniff'
	response.headers['X-Powered-By'] = 'ImprovedIntraServer/{} Werkzeug/{} Flask/{} Python/{}'.format(__version__, __werkzeug_version__, __flask_version__, platform.python_version())
	response.headers['X-Target-Version'] = 'ImprovedIntra/{}'.format(__target_ext_version__)
	response.headers['Access-Control-Allow-Credentials'] = 'true'
	response.headers['Access-Control-Allow-Methods'] = 'GET,HEAD,POST,OPTIONS'
	response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Headers, Origin, Accept, Authorization, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers'

	origin = request.environ.get('HTTP_ORIGIN', None)
	if origin is not None:
		origin_host = urlparse(origin).hostname
		if origin_host is not None and (origin_host == 'intra.42.fr' or origin_host.endswith('.intra.42.fr')):
			response.headers['Access-Control-Allow-Origin'] = 'https://{}'.format(origin_host)
			response.headers['X-Frame-Options'] = 'allow-from'

	# If request ends with a specific file extension, set the content type (and if request was met with a 200 status code)
	if response.status_code == 200:
		ext_content_types = {
			'.svg': 'image/svg+xml',
			'.ics': 'text/calendar',
		}
		for ext in ext_content_types:
			if request.path.endswith(ext):
				response.headers['Content-Type'] = ext_content_types[ext]

	return response
