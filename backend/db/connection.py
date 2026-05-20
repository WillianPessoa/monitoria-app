import logging
import os

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

_pool = None

_SCHEMA = os.path.join(os.path.dirname(__file__), "schema.sql")


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


def _apply_schema(conn):
    with open(_SCHEMA, encoding="utf-8") as f:
        sql = f.read()
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    cursor = conn.cursor()
    for stmt in statements:
        first = stmt.split()[0].upper() if stmt.split() else ""
        if first in ("CREATE", "ALTER", "DROP"):
            cursor.execute(stmt)
    conn.commit()
    cursor.close()


def init_db(app):
    try:
        _build_pool(app)
        conn = get_connection()
        _apply_schema(conn)
        conn.close()
    except mysql.connector.Error as exc:
        logging.exception("Falha ao conectar no MySQL durante a inicializacao")
        raise RuntimeError("Falha ao inicializar o pool de conexao MySQL") from exc


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool de conexao nao inicializado")
    return _pool.get_connection()
