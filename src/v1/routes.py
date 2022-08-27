from flask import session, jsonify, request, redirect, url_for, render_template
import logging
import json
import time
from .. import app
from ..models import OAuth2Token
from ..oauth import authstart
from .forms import OldSettings
from .helpers import get_v1_settings, set_v1_settings
from werkzeug.datastructures import CombinedMultiDict

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


@app.route('/connect.php', methods=['GET'])
def oldConnect():
	if not 'uid' in session or not 'v1_conn_data' in session:
		return authstart(1)
	# if not 'v1_conn_data' in session:
	# 	return render_template('v1connect.j2', data={ 'type': 'error', 'message': 'No authorization data found in session', 'auth': { 'error_description': 'No authorization data found in session' } })
	ret_data = { 'type': 'success', 'auth': session['v1_conn_data'], 'user': { 'login': session['login'] } }
	ret_data['auth']['expires_in'] = int(session['v1_conn_data']['expires_at'] - time.time())
	if ret_data['auth']['expires_in'] <= 1:
		return authstart(1) # token expired, get a new one right away
	return render_template('v1connect.j2', data=ret_data, data_json=json.dumps(ret_data))


@app.route('/settings/<login>.json', methods=['GET'])
def oldSettings(login:str):
	old_settings = get_v1_settings(login)
	if old_settings:
		return jsonify(old_settings), 200
	return '404 Not Found', 404


@app.route('/options.php', methods=['GET'])
def oldOptions():
	if not 'uid' in session:
		return redirect(url_for('oldConnect'), 302)
	return render_template('v1options.j2')


@app.route('/testkey.php', methods=['GET', 'POST'])
def oldTestKey():
	if not request.method == 'POST':
		return { 'type': 'error', 'message': 'Method should be POST' }, 405
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'No ongoing session, authenticate first' }, 410
	try:
		db_token = OAuth2Token.query.filter_by(user_id=session['uid']).first()
		if request.form.get('access_token') != db_token.access_token:
			return { 'type': 'error', 'message': 'Access token no longer works' }, 410
		return { 'type': 'success', 'message': 'Access token still works' }, 200
	except:
		return { 'type': 'error', 'message': 'No access token in DB, authenticate again' }, 410


@app.route('/delete.php')
def oldDelete():
	return { 'type': 'error', 'message': 'The delete endpoint has been removed' }, 404


@app.route('/update.php', methods=['GET', 'POST'])
def oldUpdate():
	if not request.method == 'POST':
		return { 'type': 'error', 'message': 'Method should be POST' }, 405
	if not 'v' in request.args:
		return { 'type': 'error', 'message': 'GET key \'v\' (version) is not set, but is required' }, 400
	if request.args['v'] != '1':
		return { 'type': 'error', 'message': 'Invalid value for GET key \'v\'', 'v': request.args['v'] }, 400
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'Unauthorized' }, 401
	if session['login'] != request.form.get('username'):
		return { 'type': 'error', 'message': 'Form username does not match the one found in your session' }, 403
	if request.form.get('sync') != 'true':
		return { 'type': 'error', 'message': 'Syncing is disabled in the form, cannot proceed' }, 400
	form = OldSettings(CombinedMultiDict([request.files, request.form]))
	if form.validate():
		if set_v1_settings(form):
			return { 'type': 'success', 'message': 'Settings saved', 'data': get_v1_settings(form.username.data) }, 201
		else:
			return { 'type': 'error', 'message': 'Could not save settings', 'data': get_v1_settings(form.username.data) }, 500
	form_errors = dict()
	for field_name, error_msgs in form.errors.items():
		form_errors[field_name] = list()
		for error_msg in error_msgs:
			form_errors[field_name].append(error_msg)
	return { 'type': 'error', 'message': 'Invalid form', 'form_errors': form_errors }, 400
