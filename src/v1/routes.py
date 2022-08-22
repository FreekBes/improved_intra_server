from flask import session, jsonify, request, redirect, url_for, render_template
import logging
import json
import time
from urllib.parse import urlparse
from .. import app, db
from ..models import ColorScheme, BannerImg, BannerPosition, Profile, Settings, User
from ..oauth import authstart
from .forms import OldSettings

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


@app.route('/connect.php', methods=['GET'])
def oldConnect():
	if not 'login' in session or not 'v1_conn_data' in session:
		return authstart(1)
	# if not 'v1_conn_data' in session:
	# 	return render_template('v1connect.j2', data={'type': 'error', 'message': 'No authorization data found in session', 'auth': {'error_description': 'No authorization data found in session'}})
	ret_data = {'type': 'success', 'auth': session['v1_conn_data'], 'user': {'login': session['login']}}
	ret_data['auth']['expires_in'] = int(session['v1_conn_data']['expires_at'] - time.time())
	if ret_data['auth']['expires_in'] <= 1:
		return authstart(1) # token expired, get a new one right away
	return render_template('v1connect.j2', data=ret_data, data_json=json.dumps(ret_data))


@app.route('/settings/<login>.json', methods=['GET'])
def oldSettings(login):
	try:
		db_user = db.session.query(User.intra_id, User.login).filter(User.login == login).one()
		db_settings = db.session.query(Settings).filter(Settings.user_id == db_user.intra_id).one() # This query can be sped up by selecting only what is needed in the future
		db_colors = db.session.query(ColorScheme.internal_name).filter(ColorScheme.id == db_settings.colors).one()
		db_profile = db.session.query(Profile.banner_img, Profile.banner_pos, Profile.link_git).filter(Profile.user_id == db_user.intra_id).one()
		db_banner_pos = db.session.query(BannerPosition.internal_name).filter(BannerPosition.id == db_profile.banner_pos).one()
		db_banner_img = None
		if db_profile.banner_img:
			db_banner_img = db.session.query(BannerImg.url).filter(BannerImg.id == db_profile.banner_img).first()
	except:
		return '404 Not Found', 404
	resp = {
		'username': db_user.login,
		'sync': True,

		'ext_version': db_settings.updated_ver,
		'theme': "dark" if db_settings.theme == 2 else "light" if db_settings.theme == 3 else "system",
		'colors': db_colors.internal_name,
		'show-custom-profiles': db_settings.show_custom_profiles,
		'hide-broadcasts': db_settings.hide_broadcasts,
		'logsum-month': db_settings.logsum_month,
		'logsum-week': db_settings.logsum_week,
		'outstandings': db_settings.outstandings,
		'hide-goals': db_settings.hide_goals,
		'holygraph-morecursuses': db_settings.holygraph_more_cursuses,
		'old-blackhole': db_settings.old_blackhole,
		'clustermap': db_settings.clustermap,
		'codam-monit': db_settings.codam_monit,
		'codam-buildingtimes-public': False,
		'codam-buildingtimes-chart': False,
		'codam-auto-equip-coa-title': True,
		'timestamp': int(db_settings.updated_at.timestamp()),

		'link-github': urlparse(db_profile.link_git).path.lstrip('/') if db_profile.link_git else '',
		'custom-banner-url': db_banner_img.url if db_banner_img else '',
		'custom-banner-pos': db_banner_pos.internal_name
	}
	return jsonify(resp), 200


@app.route('/options.php', methods=['GET'])
def oldOptions():
	if not 'login' in session:
		return redirect(url_for('oldConnect'), 302)
	return render_template('v1options.j2')


@app.route('/update.php', methods=['GET', 'POST'])
def oldUpdate():
	if not request.method == 'POST':
		return {'type': 'error', 'message': 'Method should be POST'}, 405
	if not 'login' in session:
		# TODO: replace with access token validation
		return {'type': 'error', 'message': 'Unauthorized'}, 401
	if not request.form.get('sync') is 'true':
		# TODO: replace by 307 to /delete.php
		return {'type': 'error', 'message': 'Syncing is disabled'}, 400
	if not 'v' in request.args:
		return {'type': 'error', 'message': 'GET key \'v\' (version) is not set, but is required'}, 400
	if not 'v' == '1':
		return {'type': 'error', 'message': 'Invalid value for GET key \'v\''}, 400
	form = OldSettings()
	if form.validate():
		return {'type': 'success', 'message': 'Settings saved', 'data': form.json()}, 201
	return {'type': 'error', 'message': 'Invalid form'}, 400
