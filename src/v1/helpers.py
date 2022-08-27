from ..models import ColorScheme, BannerImg, BannerPosition, Profile, Settings, User, OAuth2Token
from urllib.parse import urlparse
from .. import db
from .forms import OldSettings

def get_v1_settings(login:str):
	try:
		db_user:User = db.session.query(User.intra_id, User.login).filter(User.login == login).one()
		db_settings:Settings = db.session.query(Settings).filter(Settings.user_id == db_user.intra_id).one() # This query can be sped up by selecting only what is needed in the future
		db_colors:ColorScheme = db.session.query(ColorScheme.internal_name).filter(ColorScheme.id == db_settings.colors).one()
		db_profile:Profile = db.session.query(Profile.banner_img, Profile.banner_pos, Profile.link_git).filter(Profile.user_id == db_user.intra_id).one()
		db_banner_pos:BannerPosition = db.session.query(BannerPosition.internal_name).filter(BannerPosition.id == db_profile.banner_pos).one()
		db_banner_img:BannerImg = None
		if db_profile.banner_img:
			db_banner_img = db.session.query(BannerImg.url).filter(BannerImg.id == db_profile.banner_img).first()
	except Exception as e:
		print(e)
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
		'codam-auto-equip-coa-title': True,
		'timestamp': int(db_settings.updated_at.timestamp()),

		'link-github': urlparse(db_profile.link_git).path.lstrip('/') if db_profile.link_git else '',
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

		db.session.merge(db_settings)
		db.session.commit()
	except Exception as e:
		print(e)
		return False
	return True
