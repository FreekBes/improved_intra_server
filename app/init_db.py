"""One-shot database setup.

The container entrypoint runs this once, before the scheduler and the web
workers start. Doing it here rather than on import means several gunicorn
workers can never race each other over the DDL or over the default rows, which
sit behind unique constraints and would raise IntegrityError if two processes
inserted them at the same time.

It also applies the SQL files in migrations/, once each, for the schema
changes create_all() cannot make: it only ever adds tables and columns, so
anything dropped or altered needs a migration.
"""

import src.models.models  # noqa: F401 - registers the models on db.metadata

from src.models.defaults import populate_banner_pos, populate_color_schemes
from sqlalchemy_utils import database_exists, create_database
from pathlib import Path
from src import app, db

MIGRATIONS_DIR = Path(__file__).resolve().parent / 'migrations'


def run_migrations():
	"""Apply every migration that has not been applied yet, in filename order."""
	with db.engine.begin() as conn:
		conn.exec_driver_sql(
			'CREATE TABLE IF NOT EXISTS schema_migrations ('
			'filename VARCHAR(255) PRIMARY KEY, '
			'applied_at TIMESTAMP NOT NULL DEFAULT now())'
		)
		applied = {row[0] for row in conn.exec_driver_sql('SELECT filename FROM schema_migrations')}

	for path in sorted(MIGRATIONS_DIR.glob('*.sql')):
		if path.name in applied:
			continue
		print('Applying migration {}...'.format(path.name))
		# One transaction per migration, so a failure leaves the rest unapplied
		# rather than half-applied.
		with db.engine.begin() as conn:
			conn.exec_driver_sql(path.read_text())
			conn.exec_driver_sql(
				'INSERT INTO schema_migrations (filename) VALUES (%s)', (path.name,)
			)


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

		print('Applying migrations...')
		run_migrations()
		print('Migrations up to date')

		print('Initializing default content...')
		populate_banner_pos(db.session)
		populate_color_schemes(db.session)
		print('Default content initialized')


if __name__ == '__main__':
	main()
