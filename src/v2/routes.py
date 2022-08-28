from ..oauth import authstart
from flask import session
from .. import app


@app.route('/v2/connect', methods=['GET'])
def connect():
	if not 'uid' in session:
		return authstart(2)
	return 'Connected V2', 200


@app.route('/v2/disconnect', methods=['GET'])
def disconnect():
	if not 'uid' in session:
		return 'Already logged out', 200
	session.pop('login')
	session.pop('uid')
	session.pop('v')
	session.pop('v1_conn_data')
	return 'Logged out', 200
