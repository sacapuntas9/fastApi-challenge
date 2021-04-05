import os

user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "")
server = os.getenv("POSTGRES_SERVER", "db")
db = os.getenv("POSTGRES_DB", "app")

# Unix socket connection configuration for google cloud
db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME", None)

if user and password and server and db:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{db}"
    if cloud_sql_connection_name:
        SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL}?host={db_socket_dir}/{cloud_sql_connection_name}"

else:
    SQLALCHEMY_DATABASE_URL = os.getenv("sqlalchemy_database_url")  #  eg. "sqlite:///netflix.db"


def get_database_url():
    return SQLALCHEMY_DATABASE_URL
