from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.lib.config import config


# Set up DB connection
engine = create_engine(f"postgresql+psycopg2://{config['PSQL_USER']}:{config['PSQL_PASS']}@{config['PSQL_HOST']}:{config['PSQL_PORT']}/{config['PSQL_DB']}")
Session = sessionmaker(bind=engine)
session = Session()
