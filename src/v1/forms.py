from wtforms.validators import Optional, DataRequired, URL as URLValidator
from wtforms import StringField, SelectField, BooleanField, HiddenField
from src.lib.banners import ALLOWED_IMG_TYPES, BANNERS_PATH
from flask_uploads import UploadSet, configure_uploads
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from src import app

images = UploadSet('images', ALLOWED_IMG_TYPES, default_dest=lambda app: BANNERS_PATH)
configure_uploads(app, (images))

# Do not update these settings, as these are the only ones that v3 of Improved Intra supports
class OldSettings(FlaskForm):
	class Meta:
		csrf = False
	access_token = HiddenField('Intra API access token', name='access_token', validators=[DataRequired()])
	username = StringField('Currently logged in user', name='username', validators=[DataRequired()])
	sync = BooleanField('Synchronize my settings', name='sync', validators=[DataRequired()])
	expires_in = HiddenField('Intra API access token expires in', name='expires_in', validators=[DataRequired()])
	refresh_token = HiddenField('Intra API refresh token', name='refresh_token', validators=[DataRequired()])
	ext_version = HiddenField('Improved Intra extension version', name='ext_version', default='unknown')
	theme = SelectField('Theme', name='theme', default='system', choices=[('system', 'Follow system'), ('dark', 'Dark Mode'), ('light', 'Light Mode')])
	colors = SelectField('Color scheme', name='colors', default='default', choices=[('default', 'Intra (default)'), ('cetus', 'Blue'), ('vela', 'Red'), ('pyxis', 'Purple'), ('green', 'Green'), ('yellow', 'Yellow'), ('windows', 'Windows')])
	show_custom_profiles = BooleanField('Allow customized profiles', name='show-custom-profiles', default=True)
	hide_broadcasts = BooleanField('Hide broadcasts button', name='hide-broadcasts', default=False)
	logsum_month = BooleanField('Show monthly logtimes', name='logsum-month', default=True)
	logsum_week = BooleanField('Show weekly logtimes', name='logsum-week', default=True)
	outstandings = BooleanField('Show outstanding flags', name='outstandings', default=True)
	hide_goals = BooleanField('Hide Black Hole absorption', name='hide-goals', default=False)
	holygraph_more_cursuses = BooleanField('Show more cursuses in the Holy Graph', name='holygraph-morecursuses', default=False)
	old_blackhole = BooleanField('Old Black Hole countdown', name='old-blackhole', default=False)
	clustermap = BooleanField('Make logged in location clickable', name='clustermap', default=True)
	custom_banner_url = StringField('Custom profile banner background', name='custom-banner-url', validators=[Optional(), URLValidator(True, 'Invalid URL')])
	custom_banner_upload = FileField('Upload a new custom banner', name='custom-banner-upload', validators=[Optional(), FileAllowed(images, 'Only images are allowed as banners')])
	custom_banner_pos = SelectField('Custom banner image position', name='custom-banner-pos', default='center-center', choices=[('center-top', 'Top'), ('center-center', 'Centered (default)'), ('center-bottom', 'Bottom')])
	link_github = StringField('Your GitHub username', name='link-github')
	codam_monit = BooleanField('Replace Black Hole with Codam\'s Monitoring Progress', name='codam-monit', default=True)
	codam_auto_equip_coa_title = BooleanField('Auto-equip coalition titles', name='codam-auto-equip-coa-title', default=False)
