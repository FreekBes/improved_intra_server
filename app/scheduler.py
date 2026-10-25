"""Scheduled runners.

Runs as its own process inside the container, started by entrypoint.sh. Keeping
it out of the WSGI application means the jobs fire exactly once however many
gunicorn workers are serving requests.
"""

import os
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from src.runners.outstandings import outstandingsRunner
from src.runners.bannercleaning import bannerCleaningRunner
from src.runners.anonymization import anonymizationRunner
from src.runners.events import eventsRunner
from src.lib.logrotation import rotate_logs
from src.lib.db import session

LOG_DIR = os.environ.get('LOG_DIR', 'logs')
LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))


def job(runner):
	"""Release the thread-local session once the job is done.

	APScheduler runs jobs in a thread pool and reuses those threads, so without
	this a job would keep its session, and the data it has already loaded, for
	the lifetime of the process.
	"""
	def run():
		try:
			runner()
		finally:
			session.remove()
	return run


def main():
	scheduler = BlockingScheduler({
		'apscheduler.job_defaults.coalesce': 'false'
	})
	scheduler.add_job(
		job(outstandingsRunner.run), # Sync outstandings
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
	scheduler.add_job(
		job(eventsRunner.run), # Sync events
		'cron',
		month='*',
		day='*',
		hour='1,4,7,10,13,16,19,22', # Every 3 hours (more time-sensitive data)
		id='events-rnr',
		name='events-runner',
		replace_existing=True,
		coalesce=True,
		misfire_grace_time=1800 # 30 minutes
	)
	scheduler.add_job(
		job(bannerCleaningRunner.run), # Delete unused banners
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
	scheduler.add_job(
		job(anonymizationRunner.run), # Anonymize users that have passed their anonymization date
		'cron',
		month='*',
		day='*',
		hour='3', # Every day at 3 AM
		id='anonymization-rnr',
		name='anonymization-runner',
		replace_existing=True,
		coalesce=True,
		misfire_grace_time=43200 # 12 hours
	)

	scheduler.add_job(
		lambda: rotate_logs(LOG_DIR, LOG_RETENTION_DAYS), # Rotate the log files every process writes to
		'cron',
		month='*',
		day='*',
		hour='0',
		minute='5', # Just after midnight, so a day's logs land in one file
		id='logrotate-rnr',
		name='logrotate-runner',
		replace_existing=True,
		coalesce=True,
		misfire_grace_time=43200 # 12 hours
	)

	def shutdown(signum, frame):
		scheduler.shutdown(wait=False)

	signal.signal(signal.SIGTERM, shutdown)
	signal.signal(signal.SIGINT, shutdown)

	print('Scheduler started')
	scheduler.start()


if __name__ == '__main__':
	main()
