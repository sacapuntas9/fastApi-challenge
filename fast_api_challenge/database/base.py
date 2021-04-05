from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from utils import get_database_url


SQLALCHEMY_DATABASE_URL = get_database_url()

connection_args = {}

if not "postgres" in SQLALCHEMY_DATABASE_URL:  # Add specific option for SQLite database usage
    connection_args["check_same_thread"]: False

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connection_args
)

DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
