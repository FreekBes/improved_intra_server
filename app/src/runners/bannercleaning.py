import logging

from src.models.models import BannerImg, Profile
from src.lib.db import session
from datetime import datetime, timedelta
from src.lib.banners import delete_banner
from src import app


class BannerCleaningRunner:
	def run(self):
		banners:list[BannerImg] = session.query(BannerImg).all()

		for banner in banners:
			# Check if banner was uploaded less than a month ago. If so, skip it.
			if banner.created_at > datetime.now() - timedelta(days=30):
				continue

			# Check if banner is being used anywhere
			profiles:list[Profile] = session.query(Profile).where(Profile.banner_img == banner.id).all()
			if len(profiles) == 0:
				# Delete file from disk
				if banner.url.startswith(app.config['IINTRA_URL']):
					# Get banner file name from url
					banner_file = banner.url.split('/')[-1]
					if not delete_banner(banner_file):
						logging.error('Could not delete banner file: {}'.format(banner_file))
						continue # otherwise we lose track of this file

					try:
						# Delete banner from database
						session.delete(banner)
						session.commit()
						logging.info('Deleted unused banner from DB: {}'.format(banner.id))
					except Exception as e:
						logging.error('Error deleting unused banner from DB: {}'.format(str(e)))
						session.rollback()
				else:
					continue # Do not delete banners that are not hosted on our server, these do not take up much disk space anyways

		session.flush()


bannerCleaningRunner = BannerCleaningRunner()
