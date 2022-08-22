from flask_wtf import Form
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired

# Do not update these settings, as these are the only ones that v2 of Improved Intra supports
class OldSettings(Form):
	access_token = StringField('access_token', validators=[DataRequired()])
	username = StringField('username', validators=[DataRequired()])
	sync = BooleanField('sync', validators=[DataRequired()])
	expires_in = StringField('expires_in', validators=[DataRequired()])
	refresh_token = StringField('refresh_token', validators=[DataRequired()])
	ext_version = StringField('ext_version', default='unknown')
	theme = SelectField('theme', default='system', choices=[('system', 'Follow system'), ('dark', 'Dark Mode'), ('light', 'Light Mode')])
	colors = SelectField('colors', default='default', choices=[('default', 'Intra (default)'), ('cetus', 'Blue'), ('vela', 'Red'), ('pyxis', 'Purple'), ('green', 'Green'), ('yellow', 'Yellow'), ('windows', 'Windows')])
	show_custom_profiles = BooleanField('show-custom-profiles', default=True)
	hide_broadcasts = BooleanField('hide-broadcasts', default=False)
	logsum_month = BooleanField('logsum-month', default=True)
	logsum_week = BooleanField('logsum-week', default=True)
	outstandings = BooleanField('outstandings', default=True)
	hide_goals = BooleanField('hide-goals', default=False)
	holygraph_more_cursuses = BooleanField('holygraph-morecursuses', default=False)
	old_blackhole = BooleanField('old-blackhole', default=False)
	clustermap = BooleanField('clustermap', default=True)
	custom_banner_url = StringField('custom-banner-url')
	custom_banner_pos = SelectField('custom-banner-pos', default='center-center', choices=[('center-top', 'Top'), ('center-center', 'Centered (default)'), ('center-bottom', 'Bottom')])
	link_github = StringField('link-github')
	codam_monit = BooleanField('codam-monit', default=True)
	codam_auto_equip_coa_title = BooleanField('codam-auto-equip-coa-title', default=False)
