from flask import session, jsonify
import logging
from urllib.parse import urlparse
from .. import app, db
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

		'link-github': urlparse(db_profile.link_git).path.lstrip('/') if db_profile.link_git else None,
		'custom-banner-url': db_banner_img.url if db_banner_img else None,
		'custom-banner-pos': db_banner_pos.internal_name
	}
	return jsonify(resp), 200
