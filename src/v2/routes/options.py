from src.models.models import BannerImg, BannerPosition, Campus, ColorScheme, Profile, Settings
from flask import render_template, session, redirect, url_for
from ...oauth import authstart
from ... import app

FETCH_DISTRIBUTION = {
	'improvements': [ 'settings' ],
	'appearance': [ 'settings', 'color_scheme' ],
	'profile': [ 'profile' ],
	'14': [ 'settings' ], # Codam campus, Amsterdam
	'help': []
}


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
			return render_template('v2/options/no_campus_settings.j2', campus='Unknown')
		dist_key = str(campus.intra_id)

	# Fetch table rows based on the fetch_dist_key
	settings:Settings = None
	if 'settings' in FETCH_DISTRIBUTION[dist_key]:
		settings:Settings = Settings.query.filter_by(user_id=session['uid']).first()

	# Fetch color scheme if required for the page
	# Dependancy on settings, add it to FETCH_DISTRIBUTION
	color_scheme:ColorScheme = None
	if 'color_scheme' in FETCH_DISTRIBUTION[dist_key]:
		color_scheme:ColorScheme = ColorScheme.query.filter_by(id=settings.colors).first()

	# Fetch profile data if required for the page
	profile:Profile = None
	banner_img:BannerImg = None
	banner_pos:BannerPosition = None
	if 'profile' in FETCH_DISTRIBUTION[dist_key]:
		profile:Profile = Profile.query.filter_by(user_id=session['uid']).first()
		banner_pos = BannerPosition.query.filter_by(id=profile.banner_pos).first()
		if profile.banner_img:
			banner_img = BannerImg.query.filter_by(id=profile.banner_img).first()

	# Render page
	user_settings:tuple = (settings, color_scheme, profile, banner_img, banner_pos)
	if section == 'campus':
		return render_campus_settings(dist_key, campus, user_settings)
	return render_template(f"v2/options/{section}.j2", user_settings=user_settings)


@app.route('/v2/options/<section>/save', methods=['POST'])
def options_section_save(section:str):
	return 'Not implemented', 501


# Campus-specific settings
def render_campus_settings(dist_key:str, campus:Campus, user_settings:tuple[Settings, ColorScheme, Profile, BannerImg, BannerPosition]):
	if campus.intra_id == 14: # Codam, Amsterdam
		return render_template('v2/options/codam.j2', user_settings=user_settings)
	return render_template('v2/options/no_campus_settings.j2', campus=campus.name)
