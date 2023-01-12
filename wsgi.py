import src.models.models
import platform
import os

from src.models.defaults import populate_banner_pos, populate_color_schemes
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy_utils import database_exists, create_database
from src.runners.outstandings import outstandingsRunner
from src.runners.bannercleaning import bannerCleaningRunner
from src.lib.config import config
from src import app, db


# Set up database
if not database_exists(db.engine.url):
	print('Database \'iintra\' does not exist, creating...')
	if 'microsoft' in platform.uname()[2].lower():
		print('You are using Microsoft\'s Windows Subsystem for Linux, which under WSL1 has problems with PostgreSQL.')
		print('If the program hangs here, you will need to switch to WSL2 to continue.')
	create_database(db.engine.url, encoding='utf8', template='template0')
	print('Database created')

# Set up tables
print('Initializing database models...') # Models come from src.models.models import on line 1
db.create_all()
db.session.commit()
print('Database models initialized')

# Set up default content
print('Initializing default content...')

populate_banner_pos(db.session)
populate_color_schemes(db.session)
print('Default content initialized')

# Set up scheduled jobs (runners)
runner_scheduler = BackgroundScheduler({
	'apscheduler.job_defaults.coalesce': 'false'
})
runner_scheduler.add_job(
	outstandingsRunner.run, # Sync outstandings
	'cron',
	month='*',
	day='*',
	hour='2,10,18', # Every 8 hours
	id='outst-rnr',
	name='outstandings-runner',
	replace_existing=True,
	coalesce=True,
	misfire_grace_time=7200 # 2 hours
)
runner_scheduler.add_job(
	bannerCleaningRunner.run, # Delete unused banners
	'cron',
	month='*',
	day='*',
	hour='4', # Every day at 4 AM
	id='bannercleaning-rnr',
	name='bannercleaning-runner',
	replace_existing=True,
	coalesce=True,
	misfire_grace_time=43200 # 12 hours
)


if __name__ == '__main__':
	# Start the web server
	print('Running in debug mode, starting app in wsgi.py')
	app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=True)
else:
	# Only start the runner in production
	runner_scheduler.start()
