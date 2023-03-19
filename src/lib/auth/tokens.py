import tokenlib

from src.lib.auth.oauth import set_session_data
from src.models.models import User, UserToken
from flask import request, session
from src import app, db

token_manager = tokenlib.TokenManager(app.config['TOKEN_SECRET'], float(app.config['TOKEN_EXPIRATION']))


# create a token for use in the extension's frontend
# this token identifies the user for requests to the backend without requiring the user's interaction
def create_ext_token(user_id:int):
	user_token:UserToken = UserToken.query.filter_by(user_id = user_id).first()
	if not user_token:
		user_token = UserToken(user_id)
		db.session.add(user_token)
		db.session.flush()
	ext_token = token_manager.make_token({ 'user_token': user_token.token })
	user_token.update_last_used()
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
	user_token.update_last_used()
	return user, user_token


def get_ext_token():
	try:
		ext_token = request.headers['Authorization'].split(' ')[1]
		return ext_token
	except Exception as e:
		return None


def auth_with_ext_token():
	try:
		ext_token = get_ext_token()
		user, user_token = parse_ext_token(ext_token)
		app.logger.debug(f"Authenticated user {user.login} using ext_token")
		session['ext_token'] = ext_token
		set_session_data(user)
		return True
	except Exception as e:
		app.logger.exception(f"An error occurred while trying to authenticate using an ext_token: {str(e)}")
		return False


def auth_token_matches_sessions():
	try:
		ext_token = get_ext_token()
		if not ext_token or not 'ext_token' in session or ext_token != session.get('ext_token'):
			return False
		return True
	except Exception as e:
		app.logger.exception(f"An error occurred while trying to match an ext_token against a session: {str(e)}")
		return False
