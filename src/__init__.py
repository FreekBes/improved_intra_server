from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import dotenv_values

# Load config from .env files
config = {
	**dotenv_values(".shared.env", verbose=True),  # load shared development variables
	**dotenv_values(".secret.env", verbose=True),  # load sensitive variables
	**os.environ,  # override loaded values with environment variables
}
config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}"

# Set up Flask
print('Initializing Flask...')
app = Flask(__name__)
app.config.from_mapping(config)
print(config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)
print('Flask initialized')

# Set up database
if not database_exists(db.engine.url):
	print('Database \'iintra\' does not exist, creating...')
	print('If the program hangs here for a long time, please check your PostgreSQL installation. Especially on WSL!')
	create_database(db.engine.url)
	print('Database created')

# Set up tables
print('Initializing database models...')
from src import models
db.create_all()
db.session.commit()
print('Database models initialized')

# Import routes
from src.v1 import routes
from src.v2 import routes
