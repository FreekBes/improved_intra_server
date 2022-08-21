from flask import url_for, jsonify, session, redirect
from authlib.integrations.flask_client import OAuth
from .models import OAuth2Token
from . import app, db
import logging

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
	token = intra.authorize_access_token()
	resp = intra.get('me', token=token)
	resp.raise_for_status()
	user = resp.json()
	session['login'] = user['login']
	print("Login: {}".format(session['login']))
	print("SESSION v: {}".format(session['v']))
	if session['v'] == 1:
		return redirect(url_for('oldConnect'), 301)
	return redirect(url_for('connect'), 301)
