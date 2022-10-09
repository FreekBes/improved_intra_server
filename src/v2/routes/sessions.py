from flask import session, redirect, url_for
from ...oauth import authstart
from ... import app


@app.route('/v2/connect', methods=['GET'])
def connect():
	if not 'uid' in session:
		return authstart(2)
	return 'Connected V2', 200


@app.route('/v2/disconnect', methods=['GET'])
def disconnect():
	if not 'uid' in session:
		return 'Already logged out. Go to <a href="/">home</a>', 200
	session.pop('login', None)
	session.pop('uid', None)
	session.pop('staff', None)
	session.pop('v', None)
	session.pop('v1_conn_data', None)
	return 'Logged out. Go to <a href="/">home</a>', 200


@app.route('/v2/ping', methods=['GET'])
def ping():
	if not 'uid' in session:
		return 'No active session', 404
	return 'Pong', 200
