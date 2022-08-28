from .models import BannerPosition, ColorScheme


def populate_banner_pos(db_session):
	defaultBannerPositions = [
		BannerPosition('center center', 'center-center', 'Centered (default)'),
		BannerPosition('center top', 'center-top', 'Top'),
		BannerPosition('center bottom', 'center-bottom', 'Bottom')
	]
	for bannerPos in defaultBannerPositions:
		if not BannerPosition.query.filter_by(css_val = bannerPos.css_val).first():
			db_session.add(bannerPos)
	db_session.commit()


def populate_color_schemes(db_session):
	defaultColorSchemes = [
		ColorScheme('default', 'Intra (default)'),
		ColorScheme('cetus', 'Blue'),
		ColorScheme('vela', 'Red'),
		ColorScheme('pyxis', 'Purple'),
		ColorScheme('green', 'Green'),
		ColorScheme('yellow', 'Yellow'),
		ColorScheme('windows', 'Windows')
	]
	for colorScheme in defaultColorSchemes:
		if not ColorScheme.query.filter_by(internal_name = colorScheme.internal_name).first():
			db_session.add(colorScheme)
	db_session.commit()
