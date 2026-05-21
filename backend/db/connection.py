import logging
import os

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.pooling import MySQLConnectionPool
from werkzeug.security import generate_password_hash

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


def _apply_migrations(conn):
        cursor = conn.cursor()
        try:
                try:
                        cursor.execute(
                                """
                                ALTER TABLE disciplinas
                                    ADD COLUMN status ENUM('ATIVA','INATIVA') NOT NULL DEFAULT 'ATIVA'
                                """
                        )
                        conn.commit()
                except mysql.connector.Error as exc:
                        if exc.errno != errorcode.ER_DUP_FIELDNAME:
                                raise

                cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS disciplina_alunos (
                            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                            disciplina_id BIGINT UNSIGNED NOT NULL,
                            aluno_id BIGINT UNSIGNED NOT NULL,
                            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            CONSTRAINT fk_disciplina_aluno_disciplina
                                FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
                                ON DELETE CASCADE,
                            CONSTRAINT fk_disciplina_aluno_usuario
                                FOREIGN KEY (aluno_id) REFERENCES usuarios (id)
                                ON DELETE CASCADE,
                            CONSTRAINT uq_disciplina_aluno
                                UNIQUE (disciplina_id, aluno_id)
                        )
                        """
                )
                conn.commit()
        finally:
                cursor.close()


def _seed_admin(conn):
    nome = os.getenv("SEED_ADMIN_NAME")
    email = os.getenv("SEED_ADMIN_EMAIL")
    senha = os.getenv("SEED_ADMIN_PASSWORD")
    if not (nome and email and senha):
        return
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email.lower(),))
    if cursor.fetchone():
        cursor.close()
        return
    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, 'ADMIN', 'ATIVO', FALSE)
        """,
        (nome, email.lower(), generate_password_hash(senha)),
    )
    conn.commit()
    cursor.close()
    logging.info("Admin seed criado: %s", email)


def init_db(app):
    try:
        _build_pool(app)
        conn = get_connection()
        _apply_schema(conn)
        _apply_migrations(conn)
        _seed_admin(conn)
        conn.close()
    except mysql.connector.Error as exc:
        logging.exception("Falha ao conectar no MySQL durante a inicializacao")
        raise RuntimeError("Falha ao inicializar o pool de conexao MySQL") from exc


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool de conexao nao inicializado")
    return _pool.get_connection()
