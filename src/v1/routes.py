import json
import time

from flask import session, jsonify, request, redirect, url_for, render_template, Response
from src.v1.helpers import get_v1_settings, set_v1_settings
from src.models.models import OAuth2Token, User, Team, Evaluation, Runner
from werkzeug.datastructures import CombinedMultiDict
from src.lib.auth.oauth import authstart
from src.v1.forms import OldSettings
from sqlalchemy import func, case
from src import app, db


@app.route('/connect.php', methods=['GET'])
def oldConnect():
	if not 'uid' in session or not 'v1_conn_data' in session:
		return authstart(v=1)
	# if not 'v1_conn_data' in session:
	# 	return render_template('v1/connect.j2', data={ 'type': 'error', 'message': 'No authorization data found in session', 'auth': { 'error_description': 'No authorization data found in session' } })
	ret_data = { 'type': 'success', 'auth': session['v1_conn_data'], 'user': { 'login': session['login'] } }
	ret_data['auth']['expires_in'] = int(session['v1_conn_data']['expires_at'] - time.time())
	if ret_data['auth']['expires_in'] <= 1:
		return authstart(v=1) # token expired, get a new one right away
	return render_template('v1/connect.j2', data=ret_data, data_json=json.dumps(ret_data))


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
	return render_template('v1/options.j2')


@app.route('/testkey.php', methods=['GET', 'POST'])
def oldTestKey():
	if not request.method == 'POST':
		return { 'type': 'error', 'message': 'Method should be POST' }, 405
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'No ongoing session, authenticate first' }, 401
	if not 'access_token' in request.form:
		return { 'type': 'error', 'message': 'Missing access_token field in POST data' }, 400
	try:
		db_token:OAuth2Token = OAuth2Token.query.filter_by(user_id=session['uid']).first()
		if not db_token:
			return { 'type': 'error', 'message': 'No access token in DB, authenticate again' }, 404
		if str(request.form['access_token']) != str(db_token.access_token):
			return { 'type': 'error', 'message': 'Access token no longer works' }, 403
		return { 'type': 'success', 'message': 'Access token still works' }, 200
	except:
		return { 'type': 'error', 'message': 'Internal server error' }, 500


@app.route('/delete.php')
def oldDelete():
	return { 'type': 'error', 'message': 'The delete endpoint has been removed' }, 410


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

	# Validate and save form
	form = OldSettings(CombinedMultiDict([request.files, request.form]))
	if form.validate():
		if set_v1_settings(form):
			return { 'type': 'success', 'message': 'Settings saved', 'data': get_v1_settings(form.username.data) }, 201
		else:
			return { 'type': 'error', 'message': 'Could not save settings', 'data': get_v1_settings(form.username.data) }, 500

	# Gather form errors if not validated
	form_errors = dict()
	for field_name, error_msgs in form.errors.items():
		form_errors[field_name] = list()
		for error_msg in error_msgs:
			form_errors[field_name].append(error_msg)
	return { 'type': 'error', 'message': 'Invalid form', 'form_errors': form_errors }, 400


@app.route('/outstandings.php', methods=['GET'])
def oldOutstandings():
	if not 'username' in request.args:
		return { 'type': 'error', 'message': 'GET key \'username\' is not set, but is required' }, 400

	# Retrieve user and check if outstanding runner already fetched outstandings for this user
	db_user = db.session.query(User.intra_id, Runner.outstandings).join(Runner).filter(User.login == request.args['username']).first()
	if not db_user or not db_user.outstandings:
		return { 'type': 'success', 'message': 'No data exists for this user', 'data': [] }, 200

	outstandings = dict()

	# Retrieve outstandings for each project user and fetch the amount of outstanding evaluations for each team
	# Outer join, to make sure even teams without evaluations are returned
	db_q = db.session.query(Team, func.sum(case([(Evaluation.outstanding == True, 1)], else_ = 0)).label('outstandings')).outerjoin(Evaluation, Evaluation.intra_team_id == Team.intra_id).filter(Team.user_id == db_user.intra_id).order_by(Team.projects_user_id.desc(), Team.intra_id.desc()).group_by(Team.id)
	db_res:list = db_q.all()

	for db_row in db_res:
		if not str(db_row.Team.projects_user_id) in outstandings:
			pu_outstandings = dict()
			pu_outstandings['current'] = 0
			pu_outstandings['best'] = 0
			pu_outstandings['all'] = list()
			outstandings[str(db_row.Team.projects_user_id)] = pu_outstandings
		else:
			pu_outstandings = outstandings[str(db_row.Team.projects_user_id)]
		if db_row.Team.current:
			pu_outstandings['current'] = db_row.outstandings
		if db_row.Team.best:
			pu_outstandings['best'] = db_row.outstandings
		pu_outstandings['all'].append(db_row.outstandings)

	# Create response with additional headers
	resp = Response(
		response = { 'type': 'success', 'message': 'Outstandings for user, per projectsUser', 'data': outstandings },
		status = 200,
		mimetype = 'application/json'
	)
	resp.headers['Last-Modified'] = db_user.outstandings.strftime('%a, %d %b %Y %H:%M:%S GMT')
	return (resp.response, resp.status_code, resp.headers.items())


@app.route('/imagery.php', methods=['GET'])
def imagery():
	if not 'uid' in session:
		return redirect(url_for('connect'), 302)
	if not 'staff' in session or session['staff'] != True:
		return 'Access Denied', 403
	return render_template('v1/banners.j2')
