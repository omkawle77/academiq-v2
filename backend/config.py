"""
config.py — Multi-Database Configuration
Supports: SQLite (default) | MySQL | PostgreSQL
"""

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

def get_db_uri():
    if DB_TYPE == "mysql":
        host     = os.getenv("MYSQL_HOST", "localhost")
        port     = os.getenv("MYSQL_PORT", "3306")
        user     = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "academiq")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    elif DB_TYPE == "postgresql":
        host     = os.getenv("PG_HOST", "localhost")
        port     = os.getenv("PG_PORT", "5432")
        user     = os.getenv("PG_USER", "postgres")
        password = os.getenv("PG_PASSWORD", "")
        database = os.getenv("PG_DATABASE", "academiq")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    else:  # sqlite (default)
        db_path  = os.getenv("SQLITE_PATH", "database/academiq.db")
        abs_path = os.path.join(os.path.dirname(__file__), '..', db_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        return f"sqlite:///{abs_path}"

class Config:
    SQLALCHEMY_DATABASE_URI        = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY                     = os.getenv("SECRET_KEY", "dev-secret-key")
    FLASK_PORT                     = int(os.getenv("FLASK_PORT", 5000))
    DB_TYPE                        = DB_TYPE