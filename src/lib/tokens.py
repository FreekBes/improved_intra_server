import tokenlib

from ..models.models import User, UserToken
from flask import request, session
from functools import wraps
from .. import app

token_manager = tokenlib.TokenManager(app.config['TOKEN_SECRET'], app.config['TOKEN_EXPIRATION'])


# create a token for use in the extension's frontend
# this token identifies the user for requests to the backend without requiring the user's interaction
def create_ext_token(user_id:int):
	user_token:UserToken = UserToken.query.filter_by(user_id = user_id).one()
	ext_token = token_manager.make_token({ 'user_token': user_token.token })
	return ext_token


# parse an extension token and return the user
# throws an exception if it is unable to (in this case server should respond 401)
def parse_ext_token(ext_token:str):
	ext_token_content = token_manager.parse_token(ext_token)
	user_token:UserToken = UserToken.query.filter_by(token = ext_token_content['user_token']).first()
	if not user_token:
		raise Exception('User token not found, please reauthenticate')
	user:User = User.query.filter_by(intra_id=user_token.user_id).first()
	if not user:
		raise Exception('User not found')
	return user


def auth_session_with_ext_token(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not 'Authorization' in request.headers:
			return None
		try:
			# Remove bearer from Authorization header
			ext_token = request.headers['Authorization'].split(' ')[1]
			user:User = parse_ext_token(ext_token)
			session['login'] = user.login
			session['uid'] = user.intra_id
		except Exception as e:
			return None, 403
	return decorated_function

