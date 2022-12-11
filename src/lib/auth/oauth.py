import time

from src.models.models import Campus, OAuth2Token, Profile, Settings, User, Runner
from authlib.integrations.flask_client import OAuth
from flask import url_for, session, redirect
from src.lib.auth.users import add_mod_user
from functools import wraps
from src import app, db


def update_token(name:str, token:str, refresh_token:str=None, access_token:str=None):
	if refresh_token:
		item:OAuth2Token = OAuth2Token.query.filter_by(name=name, refresh_token=refresh_token).first()
	elif access_token:
		item:OAuth2Token = OAuth2Token.query.filter_by(name=name, access_token=access_token).first()
	else:
		return
	item.access_token = token['access_token']
	item.refresh_token = token['refresh_token']
	item.expires_at = token['expires_at']
	db.session.commit()


oauth = OAuth(app, update_token=update_token)
oauth.register(
	name='intra',
	client_id=app.config['O2_CLIENT_ID'],
	client_secret=app.config['O2_CLIENT_SECRET'],

	access_token_url=app.config['INTRA_TOKEN_URL'],
	access_token_params=None,

	authorize_url=app.config['INTRA_AUTH_URL'] + "?client_id=" ,
	authorize_params={'scope': 'public'},

	api_base_url=app.config['INTRA_API_URL'],
	client_kwargs={'scope': 'public'}
)
intra = oauth.create_client('intra')


def authstart(v:int=2):
	session['v'] = v # Version of the back-end
	return intra.authorize_redirect(url_for('auth', _external=True))


def authend():
	# User data
	session.pop('login', None)
	session.pop('uid', None)
	session.pop('staff', None)
	session.pop('campus', None)
	session.pop('image', None)

	# Back-end version-specific data
	session.pop('v', None)
	session.pop('v1_conn_data', None)


def set_session_data(user:User):
	session['login'] = user.login
	session['uid'] = user.intra_id
	session['staff'] = user.staff
	session['campus'] = user.campus_id
	session['image'] = 'https://picsum.photos/200/200' # TODO: get user image from Intra


@app.route('/auth')
def auth():
	# Retrieve token
	token = intra.authorize_access_token()

	# Get user info
	resp = intra.get('me', token=token)
	resp.raise_for_status()
	user = resp.json()

	# Update user info in DB
	if not add_mod_user(user):
		return 'Access Denied', 403

	# Add or modify token in DB
	db_token = OAuth2Token(user_id=user['id'], name='intra', token_type=token['token_type'], access_token=token['access_token'], refresh_token=token['refresh_token'], expires_at=int(time.time()+token['expires_in']))
	db.session.merge(db_token)

	# Commit all DB changes
	db.session.commit()

	# Set session data
	db_user:User = User.query.filter_by(intra_id=user['id']).first()
	if db_user:
		set_session_data(db_user)

	# Redirect after auth
	if 'v' in session and session['v'] == 1:
		session['v1_conn_data'] = token
		del session['v1_conn_data']['expires_in']
		session['v1_conn_data']['expires_at'] = db_token.expires_at
		return redirect(url_for('oldConnect'), 302)
	return redirect(url_for('connect'), 302)


def fail_on_noauth_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			return { 'type': 'error', 'message': 'Not logged in', 'data': {} }, 401
		return f(*args, **kwargs)
	return decorated_function


def fail_on_noauth(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			return 'Not logged in', 401
		return f(*args, **kwargs)
	return decorated_function


def auth_on_noauth(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'uid' not in session:
			return authstart(v=2)
		return f(*args, **kwargs)
	return decorated_function
