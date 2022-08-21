from flask import session, jsonify
import logging
from urllib.parse import urlparse
from .. import app
from ..models import ColorScheme, BannerImg, BannerPosition, Profile, Settings, User
from ..oauth import authstart

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


@app.route('/connect.php', methods=['GET'])
def oldConnect():
	if not 'login' in session:
		return authstart(1)
	return 'Connected V1', 200


@app.route('/settings/<login>.json', methods=['GET'])
def oldSettings(login):
	#try:
	db_user = User.query.filter_by(login = login).one()
	db_settings = Settings.query.filter_by(user_id=db_user.intra_id).one()
	db_colors = ColorScheme.query.filter_by(id=db_settings.colors).one()
	db_profile = Profile.query.filter_by(user_id=db_user.intra_id).one()
	db_banner_img = None
	if db_profile.banner_img:
		db_banner_img = BannerImg.query.filter_by(id=db_profile.banner_img).first()
	db_banner_pos = BannerPosition.query.filter_by(id=db_profile.banner_pos).one()
	#except:
	#	return '404 Not Found', 404
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

		'link-github': urlparse(db_profile.link_git).path.lstrip('/') if db_profile.link_git else None,
		'custom-banner-url': db_banner_img.url if db_banner_img else None,
		'custom-banner-pos': db_banner_pos.internal_name
	}
	return jsonify(resp), 200
