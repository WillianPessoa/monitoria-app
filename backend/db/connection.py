import logging

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

_pool = None


def _build_pool(app):
    global _pool
    _pool = MySQLConnectionPool(
        pool_name=app.config["MYSQL_POOL_NAME"],
        pool_size=app.config["MYSQL_POOL_SIZE"],
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DATABASE"],
        autocommit=False,
    )


def init_db(app):
    try:
        _build_pool(app)
        conn = get_connection()
        conn.close()
    except mysql.connector.Error:
        logging.exception("Falha ao conectar no MySQL durante a inicializacao")


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool de conexao nao inicializado")
    return _pool.get_connection()
