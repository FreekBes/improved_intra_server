from wtforms import StringField, SelectField, HiddenField
from .....banners import ALLOWED_IMG_TYPES, BANNERS_PATH
from flask_uploads import UploadSet, configure_uploads
from flask_wtf.file import FileField, FileAllowed
from .....models.models import ColorScheme
from wtforms.validators import Optional
from flask_wtf import FlaskForm
from .validators import *
from ..... import app, db

images = UploadSet('images', ALLOWED_IMG_TYPES, default_dest=lambda app: BANNERS_PATH)
configure_uploads(app, (images))


class ImprovedIntraForm(FlaskForm):
	class Meta:
		csrf = False
	ext_version = HiddenField('Improved Intra extension version', name='ext_version', default='unknown')


class AppearanceForm(ImprovedIntraForm):
	theme = SelectField('Theme', name='theme', choices=[('1', 'Follow system'), ('2', 'Dark Mode'), ('3', 'Light Mode')])
	colors = SelectField('Color scheme', name='colors', choices=[])

	def __init__(self, *args, **kwargs):
		super(ImprovedIntraForm, self).__init__(*args, **kwargs)

		# Get all enabled color schemes from the database and set them as a choice
		db_color_schemes:list[ColorScheme] = db.session.query(ColorScheme.id, ColorScheme.name).filter(ColorScheme.enabled == True).all()
		for db_color_scheme in db_color_schemes:
			self.colors.choices.append((str(db_color_scheme.id), db_color_scheme.name))


class CodamForm(ImprovedIntraForm):
	codam_monit = SelectField('Replace Black Hole with Codam\'s Monitoring Progress', name='codam_monit', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	codam_auto_equip_coa_title = SelectField('Auto-equip coalition titles', name='codam_auto_equip_coa_title', choices=[('true', 'Enabled'), ('false', 'Disabled')])


class ImprovementsForm(ImprovedIntraForm):
	show_custom_profiles = SelectField('Customized profiles', name='show_custom_profiles', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	clustermap = SelectField('Make logged in location clickable', name='clustermap', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	outstandings = SelectField('Show outstanding flags', name='outstandings', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	hide_broadcasts = SelectField('Hide broadcasts button', name='hide_broadcasts', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	holygraph_more_cursuses = SelectField('Show more cursuses in the Holy Graph', name='holygraph_more_cursuses', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	logsum_month = SelectField('Show monthly logtimes', name='logsum_month', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	logsum_week = SelectField('Show weekly logtimes', name='logsum_week', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	old_blackhole = SelectField('Old Black Hole countdown', name='old_blackhole', choices=[('true', 'Enabled'), ('false', 'Disabled')])
	hide_goals = SelectField('Hide Black Hole absorption', name='hide_goals', choices=[('true', 'Enabled'), ('false', 'Disabled')])


class ProfileForm(ImprovedIntraForm):
	custom_banner_upload = FileField('Upload a new custom banner', name='custom_banner_upload', validators=[Optional(), FileAllowed(images, 'Only images are allowed as banners.')])
	banner_img = StringField('Banner image', name='banner_img', default='', validators=[Optional(), validate_banner_img])
	banner_pos = SelectField('Banner position', name='banner_pos', choices=[])
	link_git = StringField('Link to Git profile', name='link_git', default='', validators=[Optional(), validate_git_url])
	link_web = StringField('Personal website', name='link_web', default='', validators=[Optional(), validate_web_url])

	def __init__(self, *args, **kwargs):
		super(ImprovedIntraForm, self).__init__(*args, **kwargs)

		# Get all banner positions from the database and set them as a choice
		db_banner_positions:list[BannerPosition] = db.session.query(BannerPosition.id, BannerPosition.name).all()
		for db_banner_position in db_banner_positions:
			self.banner_pos.choices.append((str(db_banner_position.id), db_banner_position.name))
