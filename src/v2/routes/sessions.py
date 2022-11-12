from flask import session, redirect, url_for, request
from ...decorators import auth_required
from ...oauth import authstart, authend
from functools import wraps
from ... import app


def continue_init(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		query_params = request.args.to_dict()
		if 'continue' in query_params:
			session['continue'] = query_params['continue']
		return f(*args, **kwargs)
	return decorated_function


def continue_active():
	return 'continue' in session


def continue_now():
	if 'continue' in session:
		continue_url = session['continue']
		del session['continue']
		return redirect(continue_url)
	return redirect(url_for('home'))


@app.route('/v2/connect', methods=['GET'])
@continue_init
def connect():
	if not 'uid' in session:
		return authstart()

	if continue_active():
		return continue_now()
	else:
		return redirect(url_for('home'))


@app.route('/v2/disconnect', methods=['GET'])
@continue_init
def disconnect():
	if not 'uid' in session:
		if continue_active():
			return continue_now()
		return 'Already logged out. Go to <a href="/">home</a>', 200
	else:
		authend()
		if continue_active():
			return continue_now()
		return 'Logged out. Go to <a href="/">home</a>', 200


@app.route('/v2/ping', methods=['GET'])
def ping():
	if not 'uid' in session:
		return 'No active session', 404
	return 'Pong', 200
