from flask import session
import logging
from .. import app
from ..oauth import authstart

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


@app.route('/v2/connect', methods=['GET'])
def connect():
	if not 'login' in session:
		return authstart(2)
	return 'Connected V2', 200


@app.route('/v2/disconnect', methods=['GET'])
def disconnect():
	if not 'login' in session:
		return 'Already logged out', 200
	session.pop('login')
	return 'Logged out', 200
