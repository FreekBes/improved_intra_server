from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from src.lib.config import config


# Set up DB connection
engine = create_engine(f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}")

# Scoped to the current thread: the scheduler runs jobs in a thread pool and a
# plain Session is not safe to share between threads. Callers use this exactly
# like a Session; scheduler.py calls .remove() when a job finishes.
Session = scoped_session(sessionmaker(bind=engine))
session = Session
