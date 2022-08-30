import json
import time
from flask import session, jsonify, request, redirect, url_for, render_template, Response
from .helpers import get_v1_settings, set_v1_settings, get_projects_users
from werkzeug.datastructures import CombinedMultiDict
from ..models.models import OAuth2Token, User, Team, Evaluation, Runner
from .forms import OldSettings
from ..oauth import authstart
from .. import app, db


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
		return { 'type': 'error', 'message': 'No ongoing session, authenticate first' }, 401
	if not 'access_token' in request.form:
		return { 'type': 'error', 'message': 'Missing access_token field in POST data' }, 400
	try:
		db_token = OAuth2Token.query.filter_by(user_id=session['uid']).first()
		if not db_token:
			return { 'type': 'error', 'message': 'No access token in DB, authenticate again' }, 404
		if request.form.get('access_token') != db_token.access_token:
			return { 'type': 'error', 'message': 'Access token no longer works' }, 403
		return { 'type': 'success', 'message': 'Access token still works' }, 200
	except:
		return { 'type': 'error', 'message': 'Internal server error' }, 500


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

	# Retrieve user
	db_user:User = User.query.filter_by(login = request.args['username']).first()
	if not db_user:
		return { 'type': 'success', 'message': 'No data exists for this user', 'data': [] }, 200
	db_runner:Runner = db.session.query(Runner.outstandings).filter(Runner.user_id == db_user.intra_id).one()
	if not db_runner or not db_runner.outstandings:
		return { 'type': 'success', 'message': 'No data exists for this user', 'data': [] }, 200

	# Set up outstandings per projects_user dict
	outstandings = dict()
	projects_user_ids = get_projects_users(db_user)
	for projects_user_id in projects_user_ids:
		pu_outstandings = dict()
		pu_outstandings['current'] = 0
		pu_outstandings['best'] = 0
		pu_outstandings['all'] = list()
		outstandings[str(projects_user_id)] = pu_outstandings

	# Loop over all teams in the database
	db_teams:list[Team] = db.session.query(Team).filter(Team.user_id == db_user.intra_id).order_by(Team.projects_user_id.desc(), Team.intra_id.desc()).all()
	for db_team in db_teams:
		team_outstandings = 0
		db_evals:list[Evaluation] = db.session.query(Evaluation.outstanding).filter(Evaluation.intra_team_id == db_team.intra_id).all()
		for db_eval in db_evals:
			if db_eval.outstanding:
				team_outstandings += 1
		pu_outstandings = outstandings[str(db_team.projects_user_id)]
		pu_outstandings['all'].append(team_outstandings)
		if db_team.best:
			pu_outstandings['best'] = team_outstandings
		if db_team.current:
			pu_outstandings['current'] = team_outstandings

	# Create response with additional headers
	resp = Response(
		response = { 'type': 'success', 'message': 'Outstandings for user, per projectsUser', 'data': outstandings },
		status = 200,
		mimetype = 'application/json'
	)
	resp.headers['Last-Modified'] = db_runner.outstandings.strftime('%a, %d %b %Y %H:%M:%S GMT')
	return (resp.response, resp.status_code, resp.headers.items())
