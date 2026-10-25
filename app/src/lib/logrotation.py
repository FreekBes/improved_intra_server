"""Log rotation, driven from the scheduler process.

The log files are written by several processes at once: the gunicorn master,
every gunicorn worker and the scheduler. Letting each of them rotate through a
TimedRotatingFileHandler means they all try to roll the same file at midnight.
Instead every writer uses a WatchedFileHandler, which notices when the file it
holds has been replaced and reopens it, and this single scheduled job does the
rotating.
"""

import logging
import os
import time

from datetime import datetime


def rotate_logs(log_dir: str, retention_days: int):
	"""Rename today's log files out of the way and drop expired ones.

	Writers reopen on their next record, so the live files reappear by
	themselves; nothing has to be signalled or restarted.
	"""
	if not os.path.isdir(log_dir):
		return

	stamp = datetime.now().strftime('%Y%m%d%H%M%S')
	rotated = 0
	for name in sorted(os.listdir(log_dir)):
		if not name.endswith('.log'):
			continue
		path = os.path.join(log_dir, name)
		try:
			if os.path.getsize(path) == 0: # nothing logged since the last run
				continue
			os.rename(path, '{}.{}'.format(path, stamp))
			rotated += 1
		except OSError as e:
			logging.warning('Could not rotate %s: %s', path, e)

	cutoff = time.time() - (retention_days * 86400)
	removed = 0
	for name in sorted(os.listdir(log_dir)):
		if '.log.' not in name:
			continue
		path = os.path.join(log_dir, name)
		try:
			if os.path.getmtime(path) < cutoff:
				os.remove(path)
				removed += 1
		except OSError as e:
			logging.warning('Could not remove %s: %s', path, e)

	logging.info('Log rotation: rotated %d file(s), removed %d expired file(s)', rotated, removed)
