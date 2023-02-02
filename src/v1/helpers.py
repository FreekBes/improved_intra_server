import re

from src.models.models import ColorScheme, BannerImg, BannerPosition, Profile, Settings, User, Team
from src.lib.banners import upload_banner, get_banner_info
from src.v1.forms import OldSettings
from flask import request
from src import db


def valid_github_username(username):
	_rex = re.compile('^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$')
	return True if _rex.fullmatch(username.lower()) else False


def unparse_github_username(git_link):
	if '@' in git_link:
		split_git = git_link.split('@')
		if len(split_git[1]) > 0 and valid_github_username(split_git[1]):
			if split_git[0] == 'github.com':
				return 'github@' + split_git[1]
			elif split_git[0] == 'gitlab.com':
				return 'gitlab@' + split_git[1]
			elif split_git[0] == 'bitbucket.org':
				return 'bitbucket.org@' + split_git[1]
			elif split_git[0] == 'codeberg.org':
				return 'codeberg.org@' + split_git[1]
			elif split_git[0] == 'sr.ht':
				return 'sr.ht@' + split_git[1]
	return ''


def parse_github_username(git_user):
	if '@' in git_user:
		split_git = git_user.split('@')
		if len(split_git[1]) == 0 or not valid_github_username(split_git[1]):
			return ''
		if split_git[0] == 'github':
			return 'github.com@' + split_git[1]
		elif split_git[0] == 'gitlab':
			return 'gitlab.com@' + split_git[1]
		else:
			return split_git[0] + '@' + split_git[1]
	return 'github.com@' + git_user


def get_v1_settings(login:str):
	try:
		db_user:User = db.session.query(User.intra_id, User.login).filter(User.login == login).first()
		if not db_user:
			return None
		db_settings:Settings = db.session.query(Settings).filter(Settings.user_id == db_user.intra_id).one() # This query can be sped up by selecting only what is needed in the future
		db_colors:ColorScheme = db.session.query(ColorScheme.internal_name).filter(ColorScheme.id == db_settings.colors).one()
		db_profile:Profile = db.session.query(Profile.banner_img, Profile.banner_pos, Profile.link_git).filter(Profile.user_id == db_user.intra_id).one()
		db_banner_pos:BannerPosition = db.session.query(BannerPosition.internal_name).filter(BannerPosition.id == db_profile.banner_pos).one()
		db_banner_img:BannerImg = None
		if db_profile.banner_img:
			db_banner_img = db.session.query(BannerImg.url).filter(BannerImg.id == db_profile.banner_img).first()
	except Exception as e:
		print("An exception occurred while retrieving v1 settings: {}".format(str(e)))
		return None
	resp = {
		'username': db_user.login,
		'sync': True,

		'ext_version': db_settings.updated_ver,
		'theme': "dark" if db_settings.theme == 2 else 'light' if db_settings.theme == 3 else 'system',
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
		'codam-auto-equip-coa-title': db_settings.codam_auto_equip_coa_title,
		'timestamp': int(db_settings.updated_at.timestamp()),

		'link-github': unparse_github_username(db_profile.link_git) if db_profile.link_git else '',
		'custom-banner-url': db_banner_img.url if db_banner_img else '',
		'custom-banner-pos': db_banner_pos.internal_name
	}
	return resp


def set_v1_settings(form:OldSettings):
	try:
		db_user:User = db.session.query(User.intra_id, User.login).filter(User.login == form.username.data).one()

		# Update basic settings
		db_settings:Settings = db.session.query(Settings).filter(Settings.user_id == db_user.intra_id).one()
		db_settings.clustermap = form.clustermap.data
		db_settings.codam_auto_equip_coa_title = form.codam_auto_equip_coa_title.data
		db_settings.codam_monit = form.codam_monit.data
		db_settings.hide_broadcasts = form.hide_broadcasts.data
		db_settings.hide_goals = form.hide_goals.data
		db_settings.holygraph_more_cursuses = form.holygraph_more_cursuses.data
		db_settings.logsum_month = form.logsum_month.data
		db_settings.logsum_week = form.logsum_week.data
		db_settings.old_blackhole = form.old_blackhole.data
		db_settings.outstandings = form.outstandings.data
		db_settings.show_custom_profiles = form.show_custom_profiles.data
		db_settings.theme = 2 if form.theme.data == 'dark' else 3 if form.theme.data == 'light' else 1
		db_settings.updated_ver = form.ext_version.data

		# Update color scheme
		db_color_scheme:ColorScheme = db.session.query(ColorScheme.id).filter(ColorScheme.internal_name == form.colors.data).first()
		if db_color_scheme:
			db_settings.colors = db_color_scheme.id

		# Update profile
		db_profile:Profile = db.session.query(Profile).filter(Profile.user_id == db_user.intra_id).one()
		db_profile.link_git = parse_github_username(form.link_github.data) if form.link_github.data else None

		# Banner position
		db_banner_pos:BannerPosition = db.session.query(BannerPosition.id).filter(BannerPosition.internal_name == form.custom_banner_pos.data).one()
		db_profile.banner_pos = db_banner_pos.id

		# Banner image from url
		# URL is validated by wtforms already
		if form.custom_banner_url.data:
			db_banner_img_url:BannerImg = db.session.query(BannerImg).filter(BannerImg.user_id == db_user.intra_id, BannerImg.url == form.custom_banner_url.data).first()
			if not db_banner_img_url:
				w, h, s = get_banner_info(form.custom_banner_url.data)
				if w and h and s:
					db_banner_img_url = BannerImg(db_user.intra_id, form.custom_banner_url.data, width=w, height=h, size=s)
					db.session.add(db_banner_img_url)
					db.session.flush()
					db.session.refresh(db_banner_img)
					db_profile.banner_img = db_banner_img.id
		else:
			db_profile.banner_img = None

		# Banner image upload
		if form.custom_banner_upload.data:
			banner_file, url = upload_banner(request.files[form.custom_banner_upload.name], form.custom_banner_upload.data, form.username.data)
			if banner_file and url:
				db_banner_img = BannerImg(db_user.intra_id, url)
				db.session.add(db_banner_img)
				db.session.flush()
				db.session.refresh(db_banner_img)
				db_profile.banner_img = db_banner_img.id

		db.session.merge(db_profile)
		db.session.merge(db_settings)
		db.session.commit()
	except Exception as e:
		print("An exception occurred while setting v1 settings: {}".format(str(e)))
		db.session.rollback()
		return False
	return True
