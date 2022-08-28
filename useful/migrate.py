# Magic to set the path to one directory up
import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
	sys.path.remove(str(parent))
except ValueError: # Already removed
	pass

# Now the real script begins
import json
import ssl

from src.models.models import User, Campus, Settings, Profile, Runner, BannerImg, BannerPosition, ColorScheme
from src.v1.helpers import parse_github_username
from src.lib.db import session as db_session
from src.banners import BANNERS_PATH
from urllib.request import urlopen
from os.path import basename, join
from urllib.parse import urlparse
from datetime import datetime, timezone
from src.lib.intra import ic

# Disable SSL certificate checking
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Banner image downloader
def download_banner(img_url:str):
	try:
		parsed_url = urlparse(img_url)
		if parsed_url.hostname == 'darkintra.freekb.es' or parsed_url.hostname == 'iintra.freekb.es':
			print('Importing banner from {}...'.format(img_url))
			img_fd = urlopen(img_url, context=ctx)
			image_data = img_fd.read()
			image_file_name = basename(parsed_url.path)
			banner_path = join(BANNERS_PATH, image_file_name)
			open(banner_path, 'wb').write(image_data)
			print('Wrote banner to {}'.format(banner_path))
		return True
	except:
		return False

# Fetch user data
migrate_data_url = 'https://darkintra.freekb.es/migrate.php'
fd = urlopen(migrate_data_url, context=ctx)
migrate_data_raw = fd.read()
migrate_data = json.loads(migrate_data_raw)

# Loop through each user and import
for old_settings in migrate_data:
	print('Importing settings for {}...'.format(old_settings['username']))

	# Get user info from 42 API
	i_user = ic.get('users/{}'.format(old_settings['username']))
	if i_user.status_code == 200:
		user = i_user.json()

		# Add campus(es) to DB
		for campus in user['campus']:
			if not Campus.query.filter_by(intra_id = campus['id']).first():
				i_campus = ic.get('campus/{}'.format(campus['id']))
				campus = i_campus.json()
				db_campus = Campus(campus['id'], campus['name'], campus['city'], campus['country'])
				db_session.add(db_campus)
				db_session.flush()

		# Find primary campus
		primary_campus_id = None
		for campus_user in user['campus_users']:
			if campus_user['is_primary']:
				primary_campus_id = campus_user['campus_id']
				break

		# Add or modify user in DB
		db_user = User(
			intra_id=user['id'],
			login=user['login'],
			campus_id=primary_campus_id,
			email=user['email'],
			first_name=user['first_name'],
			last_name=user['last_name'],
			display_name=user['displayname'],
			staff=user['staff?'] == True,
			anonymize_date=user['anonymize_date']
		)
		db_session.merge(db_user) # Add if not exist, update if exist
		db_session.flush()

		# Create settings for user if not exist
		if not Settings.query.filter_by(user_id = user['id']).first():
			db_settings = Settings(user['id'])
			if 'ext_version' in old_settings:
				db_settings.updated_ver = old_settings['ext_version']
			if 'theme' in old_settings:
				db_settings.theme = 2 if old_settings['theme'] == 'dark' else 3 if old_settings['theme'] == 'light' else 1
			if 'colors' in old_settings:
				db_color_scheme:ColorScheme = db_session.query(ColorScheme.id).filter(ColorScheme.internal_name == old_settings['colors']).first()
				if db_color_scheme:
					db_settings.colors = db_color_scheme.id
			if 'show-custom-profiles' in old_settings:
				db_settings.show_custom_profiles = bool(old_settings['show-custom-profiles'])
			if 'hide-broadcasts' in old_settings:
				db_settings.hide_broadcasts = bool(old_settings['hide-broadcasts'])
			if 'logsum-month' in old_settings:
				db_settings.logsum_month = bool(old_settings['logsum-month'])
			if 'logsum-week' in old_settings:
				db_settings.logsum_week = bool(old_settings['logsum-week'])
			if 'outstandings' in old_settings:
				db_settings.outstandings = bool(old_settings['outstandings'])
			if 'hide-goals' in old_settings:
				db_settings.hide_goals = bool(old_settings['hide-goals'])
			if 'holygraph-morecursuses' in old_settings:
				db_settings.holygraph_more_cursuses = bool(old_settings['holygraph-morecursuses'])
			if 'old-blackhole' in old_settings:
				db_settings.old_blackhole = bool(old_settings['old-blackhole'])
			if 'clustermap' in old_settings:
				db_settings.clustermap = bool(old_settings['clustermap'])
			if 'codam-monit' in old_settings:
				db_settings.codam_monit = bool(old_settings['codam-monit'])
			if 'codam-auto-equip-coa-title' in old_settings:
				db_settings.codam_auto_equip_coa_title = bool(old_settings['codam-auto-equip-coa-title'])
			if 'timestamp' in old_settings:
				db_settings.updated_at = datetime.fromtimestamp(old_settings['timestamp'], timezone.utc)
			else:
				db_settings.updated_at = datetime.utcfromtimestamp(0)
			db_session.add(db_settings)

		# Create profile for user if not exist
		if not Profile.query.filter_by(user_id = user['id']).first():
			db_profile = Profile(user['id'])
			if 'link-github' in old_settings:
				db_profile.link_git = parse_github_username(old_settings['link-github'])
			if 'custom-banner-pos' in old_settings:
				db_banner_pos:BannerPosition = db_session.query(BannerPosition.id).filter(BannerPosition.internal_name == old_settings['custom-banner-pos']).first()
				if db_banner_pos:
					db_profile.banner_pos = db_banner_pos.id
			if 'custom-banner-url' in old_settings:
				if download_banner(old_settings['custom-banner-url']):
					db_banner_img = BannerImg(db_user.intra_id, old_settings['custom-banner-url'])
					db_session.add(db_banner_img)
					db_session.flush()
					db_session.refresh(db_banner_img)
					db_profile.banner_img = db_banner_img.id
			db_session.add(db_profile)

		# Create runners for user if not exist
		if not Runner.query.filter_by(user_id = user['id']).first():
			db_runner = Runner(user['id'])
			db_session.add(db_runner)

		# Commit all DB changes
		db_session.flush()
		db_session.commit()

	else:
		print('[WARNING] Non-OK status code for user fetch (code={})'.format(i_user.status_code))
