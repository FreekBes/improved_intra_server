from flask import url_for, session, redirect
from authlib.integrations.flask_client import OAuth
from sqlalchemy.sql import func
from .models import Campus, OAuth2Token, Profile, Settings, User
from . import app, db
import logging
import time

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


def update_token(name, token, refresh_token=None, access_token=None):
	if refresh_token:
		item = OAuth2Token.query.filter_by(name=name, refresh_token=refresh_token).first()
	elif access_token:
		item = OAuth2Token.query.filter_by(name=name, access_token=access_token).first()
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


def authstart(v):
	session['v'] = v # Version of the back-end
	return intra.authorize_redirect(url_for('auth', _external=True))


@app.route('/auth')
def auth():
	# Retrieve token
	token = intra.authorize_access_token()
	print(token)

	# Get user info
	resp = intra.get('me', token=token)
	resp.raise_for_status()
	user = resp.json()
	session['login'] = user['login']
	session['uid'] = user['id']
	print("Login: {}".format(user['login']))
	print("User: {}".format(user))

	# Add campus(es) to DB
	for campus in user['campus']:
		if not Campus.query.filter_by(intra_id = campus['id']).first():
			resp = intra.get('campus/{}'.format(campus['id']), token=token)
			resp.raise_for_status()
			full_campus = resp.json()
			db_campus = Campus(full_campus['id'], full_campus['name'], full_campus['city'], full_campus['country'])
			db.session.add(db_campus)

	# Find primary campus
	primary_campus_id = None
	for campus_user in user['campus_users']:
		if campus_user['is_primary']:
			primary_campus_id = campus_user['campus_id']
			break

	# Add or modify user in DB
	db_user = User(
		intra_id=user['id'],
		login=user['login'],
		campus_id=primary_campus_id,
		email=user['email'],
		first_name=user['first_name'],
		last_name=user['last_name'],
		display_name=user['displayname'],
		staff=user['staff?'] == True,
		anonymize_date=user['anonymize_date']
	)
	db.session.merge(db_user) # Add if not exist, update if exist

	# Create settings for user if not exist
	if not Settings.query.filter_by(user_id = user['id']).first():
		db_settings = Settings(user['id'])
		db.session.add(db_settings)

	# Create profile for user if not exist
	if not Profile.query.filter_by(user_id = user['id']).first():
		db_profile = Profile(user['id'])
		db.session.add(db_profile)

	# Add or modify token in DB
	db_token = OAuth2Token(user_id=user['id'], name='intra', token_type=token['token_type'], access_token=token['access_token'], refresh_token=token['refresh_token'], expires_at=int(time.time()+token['expires_in']))
	db.session.merge(db_token)

	# Commit all DB changes
	db.session.commit()

	# Redirect after auth
	if 'v' in session:
		version = session['v']
		session.pop('v')
		if version == 1:
			session['v1_conn_data'] = token
			del session['v1_conn_data']['expires_in']
			session['v1_conn_data']['expires_at'] = db_token.expires_at
			session.pop('v1_conn_data')
			return redirect(url_for('oldConnect'), 302)
	return redirect(url_for('connect'), 302)
