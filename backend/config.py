import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "monitoria_app")
    MYSQL_POOL_NAME = os.getenv("MYSQL_POOL_NAME", "monitoria_pool")
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", "5"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
