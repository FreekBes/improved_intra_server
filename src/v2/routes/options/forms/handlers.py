import traceback
import re

from src.models.models import BannerImg, Profile, Settings, User
from src.v1.helpers import valid_github_username
from src.lib.banners import upload_banner
from urllib.parse import urlparse
from flask import request
from src import db

# Table distribution
# This dictionary specifies which user setting is saved in which table
# and how the POST body request value should be translated to a database value
TABLE_DISTRIBUTION = {
	'settings': {
		'theme': 'id',
		'colors': 'id',
		'show_custom_profiles': 'boolean',
		'hide_broadcasts': 'boolean',
		'logsum_month': 'boolean',
		'logsum_week': 'boolean',
		'outstandings': 'boolean',
		'hide_goals': 'boolean',
		'holygraph_more_cursuses': 'boolean',
		'old_blackhole': 'boolean',
		'clustermap': 'boolean',
		'codam_monit': 'boolean',
		'codam_auto_equip_coa_title': 'boolean',
		'sort_projects_date': 'boolean',
	},
	'profiles': {
		'banner_img': 'banner_img',
		'banner_pos': 'id',
		'link_git': 'git',
		'link_web': 'url'
	}
}


def handle_boolean(value:str):
	if value == 'true':
		return True
	return False


def handle_id(value:str):
	return int(value)


def handle_string(value:str):
	if not value:
		return None
	value = value.strip()
	if value == '':
		return None
	return value


def handle_url(value:str):
	value = handle_string(value)
	if not value or value == '':
		return None
	if not re.match(r'https?://', value):
		value = 'http://' + value
	return value


def handle_git(value:str):
	try:
		value = handle_url(value)
		parsed_url = urlparse(value)
		username = parsed_url.path.strip('/').split('/')[0]
		if not valid_github_username(username):
			return None
		if parsed_url.netloc == 'github.com':
			return 'github.com@' + username
		elif parsed_url.netloc == 'gitlab.com':
			return 'gitlab.com@' + username
		elif parsed_url.netloc == 'bitbucket.org':
			return 'bitbucket.org@' + username
		elif parsed_url.netloc == 'codeberg.org':
			return 'codeberg.org@' + username
		elif parsed_url.netloc == 'sr.ht':
			return 'sr.ht@' + username
	except:
		return None


def handle_banner_img(form, user_id:int, value:str):
	if value.startswith('new_upload-'):
		# User wants to upload a new banner to use for their profile
		db_user:User = db.session.query(User).filter(User.intra_id == user_id).one()
		if 'custom_banner_upload' not in form or not form['custom_banner_upload']:
			raise Exception("No file was uploaded")
		banner_file, url = upload_banner(request.files[form.custom_banner_upload.name], form.custom_banner_upload.data, db_user.login)
		if banner_file and url:
			db_banner_img = BannerImg(db_user.intra_id, url)
			db.session.add(db_banner_img)
			db.session.flush()
			db.session.refresh(db_banner_img)
			return handle_id(db_banner_img.id)
		else:
			raise Exception("Failed to upload banner")
	elif value.strip() != '':
		return handle_id(value)
	return None


# Wrapper for above handler functions
def handle(form, user_id:int, type:str, value:str):
	if type == 'boolean':
		return handle_boolean(value)
	elif type == 'id':
		return handle_id(value)
	elif type == 'string':
		return handle_string(value)
	elif type == 'url':
		return handle_url(value)
	elif type == 'git':
		return handle_git(value)
	elif type == 'banner_img':
		return handle_banner_img(form, user_id, value)
	else:
		raise Exception(f"Unknown type {type}")


def set_v2_settings(form, user_id:int):
	updated_settings = {}

	try:
		# Go over settings table
		db_settings:Settings = db.session.query(Settings).filter(Settings.user_id == user_id).one()
		for setting_key in TABLE_DISTRIBUTION['settings']:
			if setting_key in form and form[setting_key].raw_data:
				setting_value = handle(form, user_id, TABLE_DISTRIBUTION['settings'][setting_key], form[setting_key].data)
				if getattr(db_settings, setting_key) != setting_value:
					setattr(db_settings, setting_key, setting_value)
					updated_settings[setting_key] = setting_value

		# Update the extension version for the user in the database
		if 'ext_version' in form and form['ext_version'].raw_data and form['ext_version'] != 'unknown':
			db_settings.updated_ver = form['ext_version'].data

		# Go over profile table
		db_profile:Profile = db.session.query(Profile).filter(Profile.user_id == user_id).one()
		for setting_key in TABLE_DISTRIBUTION['profiles']:
			if setting_key in form and form[setting_key].raw_data:
				setting_value = handle(form, user_id, TABLE_DISTRIBUTION['profiles'][setting_key], form[setting_key].data)
				if getattr(db_profile, setting_key) != setting_value:
					setattr(db_profile, setting_key, setting_value)
					updated_settings[setting_key] = setting_value

		db.session.merge(db_settings)
		db.session.merge(db_profile)
		db.session.commit()
	except Exception as e:
		print("An exception occurred while setting v2 settings: {}".format(str(e)))
		traceback.print_exc()
		db.session.rollback()
		return False, str(e), {}
	return True, 'Settings saved', updated_settings
