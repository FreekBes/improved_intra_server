from src.lib.auth.tokens import auth_with_ext_token, auth_token_matches_sessions
from src.lib.auth.oauth import authstart
from flask import session, request
from functools import wraps


def session_active():
	return 'uid' in session


def session_is_staff():
	return 'staff' in session and session['staff'] == True


def session_ext_token_active():
	if 'uid' in session and 'ext_token' in session:
		return auth_token_matches_sessions()
	else:
		return auth_with_ext_token()


# Programmatically called endpoint: an ext_token is required in the Authorization header to call this endpoint, and the response should be json
def ext_token_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session_ext_token_active():
			return { 'type': 'error', 'message': 'Not logged in or invalid ext_token', 'data': {} }, 401
		return f(*args, **kwargs)
	return decorated_function


# User-called endpoint: a session is required to call this endpoint, and if no session is active, the user will be redirected to the login page
def session_required_redirect(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session_active():
			session['continue'] = request.url
			return authstart()
		return f(*args, **kwargs)
	return decorated_function


# Programatically called endpoint: a session is required to call this endpoint, and the response should be json
def session_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session_active():
			return { 'type': 'error', 'message': 'Not logged in', 'data': {} }, 401
		return f(*args, **kwargs)
	return decorated_function


# User-called endpoint: a session with a staff account is required to call this endpoint
def staff_acc_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session_is_staff():
			return 'Access denied', 403
		return f(*args, **kwargs)
	return decorated_function


# Programatically called endpoint: a session with a staff account is required to call this endpoint and the response should be json
def staff_acc_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session_is_staff():
			return { 'type': 'error', 'message': 'Access denied', 'data': {} }, 403
		return f(*args, **kwargs)
	return decorated_function
