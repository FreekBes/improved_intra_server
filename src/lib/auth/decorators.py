from src.lib.auth.tokens import auth_with_ext_token
from src.lib.auth.oauth import authstart
from flask import session, request
from functools import wraps

def auth_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session and not auth_with_ext_token():
			return 'Not logged in', 401
		return f(*args, **kwargs)
	return decorated_function


def auth_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session and not auth_with_ext_token():
			return { 'type': 'error', 'message': 'Not logged in', 'data': {} }, 401
		return f(*args, **kwargs)
	return decorated_function


def auth_required_redirect(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session and not auth_with_ext_token():
			session['continue'] = request.url
			return authstart()
		return f(*args, **kwargs)
	return decorated_function


def staff_acc_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not 'uid' in session:
			auth_with_ext_token()
		if 'staff' not in session or not session['staff']:
			return 'Access denied', 403
		return f(*args, **kwargs)
	return decorated_function


def staff_acc_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not 'uid' in session:
			auth_with_ext_token()
		if 'staff' not in session or not session['staff']:
			return { 'type': 'error', 'message': 'Access denied', 'data': {} }, 403
		return f(*args, **kwargs)
	return decorated_function
