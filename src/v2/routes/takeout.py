from src.models.models import BannerImg, Campus, Evaluation, OAuth2Token, Profile, Settings, Team, User, UserToken
from src.models.helpers import row_to_json_str, rows_to_json_str, row_to_dict, keyedtuple_rows_to_dict
from src.lib.auth.decorators import session_required_redirect
from flask import session, send_file, request
from src.lib.banners import BANNERS_PATH
from sqlalchemy import literal
from datetime import datetime
from src import app, db
import zipfile
import json
import io
import os


@app.route('/v2/takeout')
@session_required_redirect
def takeout():
	try:
		# Get current time
		now = datetime.now()

		# Retrieve user data
		user:User = User.query.filter_by(intra_id=session['uid']).first()
		if not user:
			return 'User not found', 404

		# Retrieve user's settings
		settings = Settings.query.filter_by(user_id=user.intra_id).first()

		# Retrieve the user's campus information (bit of a stretch, but hey, it's related to the user?)
		campus:Campus = Campus.query.filter_by(intra_id=user.campus_id).first()

		# Retrieve the user's profile information
		profile:Profile = Profile.query.filter_by(user_id=user.intra_id).first()

		# Retrieve the user's banner image(s)
		banners:list[BannerImg] = BannerImg.query.filter_by(user_id=user.intra_id).all()

		# Retrieve the user's teams and its evaluations
		# Store them by projects user for easier human-readability
		project_users = dict()
		teams:list[Team] = Team.query.filter_by(user_id=user.intra_id).all()
		for team in teams:
			if not team.projects_user_id in project_users:
				project_users[team.projects_user_id] = []
			team_dict = row_to_dict(team)
			team_dict['evaluations'] = []
			evals:list[Evaluation] = Evaluation.query.filter_by(intra_team_id=team.intra_id).all()
			for eval in evals:
				team_dict['evaluations'].append(row_to_dict(eval))
			project_users[team.projects_user_id].append(team_dict)

		# Retrieve the user's tokens (not OAuth, but the user tokens used to authenticate the user to the Improved Intra server from the extension)
		# Do not retrieve the token value, only the creation date and last used date - for security's sake
		user_tokens:list = db.session.query(UserToken.user_id, UserToken.created_at, UserToken.last_used_at, literal('***').label('token')).filter_by(user_id=user.intra_id).all()

		# Retrieve the user's OAuth tokens
		# Do not retrieve the token value nor the refresh token, for security's sake
		oauth_tokens:list = db.session.query(OAuth2Token.user_id, OAuth2Token.name, OAuth2Token.token_type, OAuth2Token.expires_at, literal('***').label('access_token'), literal('***').label('refresh_token')).filter_by(user_id=user.intra_id).all()

		# Create a zip file with the user data
		data = io.BytesIO()
		with zipfile.ZipFile(data, 'w') as zip:
			with zip.open("readme.txt", 'w') as f:
				f.write(bytes(f"This archive contains the data that the Improved Intra browser extension had stored about the user '{user.login}' on {now.strftime('%A %B %-d %Y')}, at {now.strftime('%-I:%M:%S.%f %p')}. It was downloaded from the URL {request.base_url} by {user.display_name}, who requested this information using IP address {request.remote_addr}.", encoding='utf-8'))
			with zip.open("user.json", 'w') as f:
				f.write(row_to_json_str(user))
			with zip.open("campus.json", 'w') as f:
				f.write(row_to_json_str(campus))
			with zip.open("settings.json", 'w') as f:
				f.write(row_to_json_str(settings))
			with zip.open("profile.json", 'w') as f:
				f.write(row_to_json_str(profile))
			if banners:
				with zip.open("banners.json", 'w') as f:
					f.write(rows_to_json_str(banners))
			if project_users:
				with zip.open("project_users.json", 'w') as f:
					# Only write the values of the projects_users dict: we do not care about the keys - they are the projects_user ids, which are already stored in each team object's values
					f.write(json.dumps(list(project_users.values()), indent=2, sort_keys=True, default=str).encode('utf-8'))
			if user_tokens:
				with zip.open("user_tokens.json", 'w') as f:
					f.write(json.dumps(keyedtuple_rows_to_dict(user_tokens), indent=2, sort_keys=True, default=str).encode('utf-8'))
			if oauth_tokens:
				with zip.open("oauth_tokens.json", 'w') as f:
					f.write(json.dumps(keyedtuple_rows_to_dict(oauth_tokens), indent=2, sort_keys=True, default=str).encode('utf-8'))

			# Add banner images to the zip file if they are hosted on our server
			if banners:
				for banner in banners:
					if banner.url.startswith(app.config['IINTRA_URL']):
						# Get banner file name from url
						banner_file = banner.url.split('/')[-1]
						banner_path = os.path.join(BANNERS_PATH, banner_file)
						if os.path.exists(banner_path):
							with zip.open(f"banners/{banner_file}", 'w') as f:
								f.write(open(banner_path, 'rb').read())

		# Send the zip file to the user
		data.seek(0)
		return send_file(data, mimetype='application/zip', as_attachment=True, download_name=f"improved_intra_takeout_{user.login}_{now.strftime('%Y_%d_%m_%H_%M_%S_%f')}.zip", last_modified=now)
	except Exception as e:
		app.logger.exception(f"An error occurred while trying to take-out {session['uid']}'s data: {str(e)}")
		return 'An error occurred while trying to retrieve your data. We assure you that this is NOT by design and this is a true problem. Please let us know immediately by creating an issue on the Improved Intra (Server) GitHub repository, or by sending an e-mail to fbes@student.codam.nl.', 500
