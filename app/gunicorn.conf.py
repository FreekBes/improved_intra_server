"""Gunicorn configuration.

Gunicorn picks this file up automatically when it is started from this
directory, so the container CMD does not have to repeat any of it.

Access and error logs are written to stdout/stderr (so `docker logs` works)
*and* to files under logs/, rotated daily and kept for 30 days.
"""

import os

LOG_DIR = os.environ.get('LOG_DIR', 'logs')
LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))

bind = '0.0.0.0:8000'

# A single process, because wsgi.py starts an in-process APScheduler: more
# workers would run every scheduled job once per worker. Threads give the
# concurrency instead, which matters now that this process also serves the
# static files.
workers = 1
worker_class = 'gthread'
threads = 4

# Gunicorn only emits an access log when accesslog is set; the handlers below
# decide where it actually goes.
accesslog = '-'
errorlog = '-'

logconfig_dict = {
	'version': 1,
	# The application reconfigures the root logger when it is imported.
	'disable_existing_loggers': False,
	'formatters': {
		'generic': {
			'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
		},
		'access': {
			'format': '%(message)s',
		},
	},
	'handlers': {
		'error_console': {
			'class': 'logging.StreamHandler',
			'formatter': 'generic',
			'stream': 'ext://sys.stderr',
		},
		'error_file': {
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'formatter': 'generic',
			'filename': os.path.join(LOG_DIR, 'error.log'),
			'when': 'midnight',
			'backupCount': LOG_RETENTION_DAYS,
		},
		'access_console': {
			'class': 'logging.StreamHandler',
			'formatter': 'access',
			'stream': 'ext://sys.stdout',
		},
		'access_file': {
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'formatter': 'access',
			'filename': os.path.join(LOG_DIR, 'access.log'),
			'when': 'midnight',
			'backupCount': LOG_RETENTION_DAYS,
		},
	},
	'loggers': {
		'gunicorn.error': {
			'level': 'INFO',
			'handlers': ['error_console', 'error_file'],
			'propagate': False,
		},
		'gunicorn.access': {
			'level': 'INFO',
			'handlers': ['access_console', 'access_file'],
			'propagate': False,
		},
	},
	'root': {
		'level': 'INFO',
		'handlers': ['error_console'],
	},
}
