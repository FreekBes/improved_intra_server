from flask import session, request
from .oauth import authstart
from functools import wraps

def auth_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			return 'Not logged in', 401
		return f(*args, **kwargs)
	return decorated_function


def auth_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			return { 'type': 'error', 'message': 'Not logged in', 'data': {} }, 401
		return f(*args, **kwargs)
	return decorated_function


def auth_required_redirect(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			session['continue'] = request.url
			return authstart()
		return f(*args, **kwargs)
	return decorated_function


def staff_acc_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'staff' not in session or not session['staff']:
			return 'Access denied', 403
		return f(*args, **kwargs)
	return decorated_function


def staff_acc_required_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'staff' not in session or not session['staff']:
			return { 'type': 'error', 'message': 'Access denied', 'data': {} }, 403
		return f(*args, **kwargs)
	return decorated_function
