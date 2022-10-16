from src.models.models import BannerImg, BannerPosition, Campus, ColorScheme, Profile, Settings
from flask import render_template, session, redirect, url_for
from ... import app, __version__, __target_ext_version__
from ...oauth import authstart

FETCH_DISTRIBUTION = {
	'improvements': [ 'settings' ],
	'appearance': [ 'settings', 'color_schemes' ],
	'profile': [ 'profile', 'banner_positions' ],
	'14': [ 'settings' ], # Codam campus, Amsterdam
	'help': []
}

VERSION_INFO:tuple[str, str] = (__version__, __target_ext_version__)


@app.route('/v2/options')
def options():
	if not 'uid' in session:
		return authstart()
	return redirect(url_for('options_section', section='improvements'))


@app.route('/v2/options/<section>')
def options_section(section:str):
	if not 'uid' in session:
		return authstart()

	# Set default FETCH_DISTRIBUTION key (defaults to session slug)
	dist_key:str = section

	# Get campus data if required
	campus:Campus = None
	if section == 'campus':
		campus:Campus = Campus.query.filter_by(intra_id=int(session['campus'])).first()
		if not campus:
			return render_no_campus_settings()
		dist_key = str(campus.intra_id)

	# Fetch table rows based on the fetch_dist_key
	settings:Settings = None
	if 'settings' in FETCH_DISTRIBUTION[dist_key]:
		settings:Settings = Settings.query.filter_by(user_id=session['uid']).first()

	# Fetch all possible color schemes if required for page
	color_schemes:list[ColorScheme] = []
	if 'color_schemes' in FETCH_DISTRIBUTION[dist_key]:
		color_schemes:list[ColorScheme] = ColorScheme.query.all()

	# Fetch all possible banner positions if required for page
	banner_positions:list[BannerPosition] = []
	if 'banner_positions' in FETCH_DISTRIBUTION[dist_key]:
		banner_positions:list[BannerPosition] = BannerPosition.query.all()

	# Fetch profile data if required for the page
	profile:Profile = None
	banner_img:BannerImg = None
	if 'profile' in FETCH_DISTRIBUTION[dist_key]:
		profile:Profile = Profile.query.filter_by(user_id=session['uid']).first()
		if profile.banner_img:
			banner_img = BannerImg.query.filter_by(id=profile.banner_img).first()

	# Render page
	user_settings:tuple = (settings, profile, banner_img)
	possible_options:tuple = (color_schemes, banner_positions)
	if section == 'campus':
		return render_campus_settings(dist_key, campus, user_settings, possible_options)
	return render_template(f"v2/options/{section}.j2", user_settings=user_settings, possible_options=possible_options, user_login=session['login'], user_image=session['image'], version=VERSION_INFO)


@app.route('/v2/options/<section>/save', methods=['POST'])
def options_section_save(section:str):
	return 'Not implemented', 501


# Campus-specific settings
def render_campus_settings(dist_key:str, campus:Campus, user_settings:tuple[Settings, Profile, BannerImg], possible_options:tuple[list[ColorScheme], list[BannerPosition]]=None):
	if campus.intra_id == 14: # Codam, Amsterdam
		return render_template('v2/options/codam.j2', user_settings=user_settings, possible_options=possible_options, user_login=session['login'], user_image=session['image'], version=VERSION_INFO)
	return render_no_campus_settings()

def render_no_campus_settings():
	return render_template('v2/options/no_campus_settings.j2', campus='Unknown', user_login=session['login'], user_image=session['image'], version=VERSION_INFO)
