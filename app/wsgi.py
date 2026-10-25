"""WSGI entrypoint.

Only exposes the Flask application. Database setup lives in init_db.py and the
scheduled runners in scheduler.py, both started by entrypoint.sh, so that
neither is tied to the number of gunicorn workers.
"""

import src.models.models  # noqa: F401 - registers the models on db.metadata

from src import app  # noqa: F401 - gunicorn imports this as wsgi:app
