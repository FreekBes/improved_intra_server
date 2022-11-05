from .....models.models import ColorScheme, BannerPosition, BannerImg
from wtforms.validators import ValidationError
from urllib.parse import urlparse
from ..... import db


# Unused
def validate_color_scheme(form, field):
	try:
		color_scheme_id = int(field.data)
		db_color_scheme:ColorScheme = db.session.query(ColorScheme).filter(ColorScheme.id == color_scheme_id, ColorScheme.enabled == True).one()
	except:
		raise ValidationError('Invalid color scheme.')


# Unused
def validate_banner_pos(form, field):
	try:
		banner_pos_id = int(field.data)
		db_banner_pos:BannerPosition = db.session.query(BannerPosition).filter(BannerPosition.id == banner_pos_id).one()
	except:
		raise ValidationError('Invalid banner position.')


def validate_banner_img(form, field):
	if not field.data.startswith("new_upload-"):
		try:
			banner_img_id = int(field.data)
			db_banner_img:BannerImg = db.session.query(BannerImg).filter(BannerImg.id == banner_img_id).one()
		except:
			raise ValidationError('Invalid banner image.')


def validate_web_url(form, field):
	try:
		parsed_url = urlparse(field.data)
	except:
		raise ValidationError('Invalid URL.')
	if not parsed_url.scheme in [ 'http', 'https' ]:
		raise ValidationError('Invalid URL scheme. Only HTTP and HTTPS are allowed.')
	if parsed_url.netloc in [ '', 'localhost', '::1', '127.0.0.1', '::1', '0.0.0.0' ]:
		raise ValidationError('Very funny! But no.')
	return parsed_url


def validate_git_url(form, field):
	# Validate the git URL like the general web URL, but also check for whitelisted domains
	parsed_url = validate_web_url(form, field)
	allowed_hostnames = [ 'github.com', 'gitlab.com', 'codeberg.org' ]
	if not parsed_url.hostname in allowed_hostnames:
		raise ValidationError('This domain is not whitelisted as a git service.')


