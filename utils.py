import os

user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "")
server = os.getenv("POSTGRES_SERVER", "db")
db = os.getenv("POSTGRES_DB", "app")

if user and password and server and db:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{db}"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("sqlalchemy_database_url")  #  eg. "sqlite:///netflix.db"


def get_database_url():
    return SQLALCHEMY_DATABASE_URL
