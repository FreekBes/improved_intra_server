"""Gunicorn configuration.

Gunicorn picks this file up automatically when it is started from this
directory, so both gunicorn.sh and the container CMD share these settings.

Access and error logs are written to stdout/stderr (so `docker logs` works)
*and* to files under logs/, which the logrotate service trims.
"""

import os

LOG_DIR = os.environ.get('LOG_DIR', 'logs')

bind = '0.0.0.0:8000'
workers = 1

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
			# WatchedFileHandler reopens the file if logrotate moves it.
			'class': 'logging.handlers.WatchedFileHandler',
			'formatter': 'generic',
			'filename': os.path.join(LOG_DIR, 'error.log'),
		},
		'access_console': {
			'class': 'logging.StreamHandler',
			'formatter': 'access',
			'stream': 'ext://sys.stdout',
		},
		'access_file': {
			'class': 'logging.handlers.WatchedFileHandler',
			'formatter': 'access',
			'filename': os.path.join(LOG_DIR, 'access.log'),
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
