import imghdr
import os

from urllib.request import urlopen
from PIL import Image
from time import time
from src import app

ALLOWED_IMG_TYPES = ['jpg', 'jpeg', 'png', 'gif']
BANNERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'banners')


def upload_banner(file, file_name, username:str):
	try:
		image_data = file.read()
		ext = imghdr.what(None, image_data)
		if ext not in ALLOWED_IMG_TYPES:
			return None, None
		banner_file = username + '-' + str(int(time())) + '.' + ext
		banner_path = os.path.join(BANNERS_PATH, banner_file)
		open(banner_path, 'wb').write(image_data)
		url = app.config['IINTRA_URL'] + 'banners/' + banner_file
		return banner_file, url
	except Exception as e:
		print("An exception occurred while uploading a banner: {}".format(str(e)))
		return None, None


def get_banner_info(url):
	try:
		fd = urlopen(url)
		file_data = fd.read()
		img = Image.open(file_data)
		width = img.width
		height = img.height
		size = len(file_data)
		return width, height, size
	except:
		return 0, 0, 0


def banner_exists(banner_file):
	banner_path = os.path.join(BANNERS_PATH, banner_file)
	return os.path.exists(banner_path)


# The parameter banner_file should be the file name of the banner only, not a path (so also no /banners/ in front of it)
def delete_banner(banner_file):
	try:
		banner_path = os.path.join(BANNERS_PATH, banner_file)
		if not os.path.exists(banner_path):
			raise FileNotFoundError('Banner file not found: {}'.format(banner_path))
		os.remove(banner_path)
		return True
	except Exception as e:
		print("An exception occurred while deleting a banner: {}".format(str(e)))
		return False
