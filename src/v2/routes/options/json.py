from src.models.models import User, BannerImg, BannerPosition, Campus, ColorScheme, Profile, Settings, THEMES
from src.lib.auth.decorators import ext_token_required_json
from src.models.helpers import row_to_dict
from flask import session
from src import app, db


def fetch_profile(user_id:int):
	# Fetch profile
	profile:Profile = db.session.query(Profile).filter(Profile.user_id == user_id).first()
	if not profile:
		return None
	profile_dict = row_to_dict(profile)

	# Fetch banner image
	if profile.banner_img:
		banner_img:BannerImg = db.session.query(BannerImg).filter(BannerImg.id == profile.banner_img).first()
		if banner_img:
			profile_dict['banner_img'] = row_to_dict(banner_img)
		else:
			profile_dict['banner_img'] = None

	# Fetch banner position
	banner_position:BannerPosition = db.session.query(BannerPosition).filter(BannerPosition.id == profile.banner_pos).one()
	profile_dict['banner_pos'] = row_to_dict(banner_position)
	return profile_dict


def fetch_settings(user_id:int):
	# Fetch settings
	settings:Settings = db.session.query(Settings).filter(Settings.user_id == user_id).first()
	if not settings:
		return None
	settings_dict = row_to_dict(settings)

	# Fetch theme
	for theme in THEMES:
		if theme.id == int(settings_dict['theme']):
			settings_dict['theme'] = theme.to_dict()
			break

	# Fetch color scheme
	color_scheme:ColorScheme = db.session.query(ColorScheme).filter(ColorScheme.id == settings.colors).one()
	settings_dict['colors'] = row_to_dict(color_scheme)
	return settings_dict


@app.route('/v2/profile/<login>.json')
def profile_json(login:str):
	try:
		# Fetch user
		user:User = db.session.query(User.intra_id).filter(User.login == login).first()
		if not user:
			return { 'type': 'error', 'message': 'User is not an Improved Intra user, so no profile exists', 'data': {} }, 404

		# Fetch profile
		profile_dict = fetch_profile(user.intra_id)
		if not profile_dict:
			return { 'type': 'error', 'message': 'No custom profile found', 'data': {} }, 404

		# Return data
		return { 'type': 'success', 'message': 'Custom profile found', 'data': profile_dict }, 200
	except Exception as e:
		return { 'type': 'error', 'message': str(e), 'data': {} }, 500


@app.route('/v2/options.json')
@ext_token_required_json
def my_options_json():
	try:
		# Fetch profile
		profile_dict = fetch_profile(session['uid'])

		# Fetch settings
		settings_dict = fetch_settings(session['uid'])

		# Fetch user because why not
		user:User = db.session.query(User).filter(User.intra_id == session['uid']).first()
		user_dict = {
			'login': user.login,
			'intra_id': user.intra_id,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'display_name': user.display_name,
			'staff': user.staff,
			'campus': row_to_dict(db.session.query(Campus).filter(Campus.intra_id == user.campus_id).first())
		}

		# Return both
		return { 'type': 'success', 'message': 'Custom options fetched', 'data': { 'profile': profile_dict, 'settings': settings_dict, 'user': user_dict } }, 200
	except Exception as e:
		return { 'type': 'error', 'message': str(e), 'data': {} }, 500
