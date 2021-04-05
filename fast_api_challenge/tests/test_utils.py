import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import functools

SQLALCHEMY_DATABASE_URL = 'sqlite://'  # Uses in-memory ephemeral database
os.environ["sqlalchemy_database_url"] = SQLALCHEMY_DATABASE_URL  # Retrieved in the import below to set up the local DB

from fast_api_challenge.database.orm import Base, NetflixShow


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def inject_in_memory_db_with_netflix_show_table(function):
    """Decorator for tests which uses the in-memory database declared in the above `engine` and `DbSession`,
    creating a new NetflixShow table configured according to the ORM/Pydantic model SQLAlchemy setup before each
    decorated function call, and clearing the table after."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        Base.metadata.create_all(bind=engine)
        db = DbSession()
        result = function(db=db, *args, **kwargs)
        db.query(NetflixShow).delete()  # Clear database table after execution
        db.commit()
        return result
    return wrapper
