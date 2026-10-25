"""One-shot database setup.

The container entrypoint runs this once, before the scheduler and the web
workers start. Doing it here rather than on import means several gunicorn
workers can never race each other over the DDL or over the default rows, which
sit behind unique constraints and would raise IntegrityError if two processes
inserted them at the same time.
"""

import src.models.models  # noqa: F401 - registers the models on db.metadata

from src.models.defaults import populate_banner_pos, populate_color_schemes
from sqlalchemy_utils import database_exists, create_database
from src import app, db


def main():
	with app.app_context():
		if not database_exists(db.engine.url):
			print('Database does not exist, creating...')
			create_database(db.engine.url, encoding='utf8', template='template0')
			print('Database created')

		print('Initializing database models...')
		db.create_all()
		db.session.commit()
		print('Database models initialized')

		print('Initializing default content...')
		populate_banner_pos(db.session)
		populate_color_schemes(db.session)
		print('Default content initialized')


if __name__ == '__main__':
	main()
