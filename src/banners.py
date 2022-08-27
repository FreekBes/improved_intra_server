import os
import imghdr
from time import time
from PIL import Image
from . import app
from urllib.request import urlopen

ALLOWED_IMG_TYPES = ['jpg', 'jpe', 'jpeg', 'png', 'gif']
BANNERS_PATH = os.path.join(app.instance_path, 'static', 'banners')

def upload_banner(file, file_name:str, username:str):
	try:
		image_data = file.read()
		ext = imghdr.what(None, image_data)
		if ext not in ALLOWED_IMG_TYPES:
			return None, None
		banner_file = os.path.join(BANNERS_PATH, username + '-' + int(time()) + '.' + ext)
		open(banner_file, 'w').write(image_data)
		url = app.config['IINTRA_URL'] + 'banners/' + file_name
		return os.path.basename(banner_file), url
	except Exception as e:
		print(e)
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

