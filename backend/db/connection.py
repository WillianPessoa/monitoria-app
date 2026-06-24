import logging
import os

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.pooling import MySQLConnectionPool
from werkzeug.security import generate_password_hash

_pool = None

_SCHEMA = os.path.join(os.path.dirname(__file__), "schema.sql")
_MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")


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
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                aplicado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        applied = set()
        cursor.execute("SELECT filename FROM migrations")
        for (filename,) in cursor.fetchall():
            applied.add(filename)

        if not os.path.isdir(_MIGRATIONS_DIR):
            return

        migration_files = sorted(
            f for f in os.listdir(_MIGRATIONS_DIR) if f.endswith(".sql")
        )
        for filename in migration_files:
            if filename in applied:
                continue

            path = os.path.join(_MIGRATIONS_DIR, filename)
            with open(path, encoding="utf-8") as f:
                sql = f.read()

            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                    if cursor.with_rows:
                        cursor.fetchall()
                except mysql.connector.errors.ProgrammingError as exc:
                    if exc.errno == 1060:
                        # Duplicate column name — coluna já existe no schema.sql.
                        # Acontece em bancos criados do zero a partir do schema atual.
                        logging.warning("Migration %s: coluna já existe, ignorado: %s", filename, exc)
                    elif exc.errno == 1061:
                        # Duplicate key name — índice já existe.
                        logging.warning("Migration %s: índice já existe, ignorado: %s", filename, exc)
                    else:
                        raise

            cursor.execute(
                "INSERT INTO migrations (filename) VALUES (%s)",
                (filename,),
            )
            conn.commit()
            logging.info("Migration aplicada: %s", filename)
    finally:
        cursor.close()


_SEED_ADMINS = [
    ("Willian Pessoa", "willian.pessoa.cs@gmail.com"),
    ("Gabriel", "gabrielrb@ic.ufrj.br"),
    ("Pedro", "pedroaac@ic.ufrj.br"),
    ("Gustavo", "gustavopo@ic.ufrj.br"),
    ("João Pedro", "joaopmab@ic.ufrj.br"),
    ("Product Owner", "product-owner@monitoria-app.com.br"),
]

_SEED_PASSWORD = "monitoria-app"


def _seed_admins(conn):
    senha_hash = generate_password_hash(_SEED_PASSWORD)
    cursor = conn.cursor()
    for nome, email in _SEED_ADMINS:
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            continue
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
            VALUES (%s, %s, %s, 'ADMIN', 'ATIVO', FALSE)
            """,
            (nome, email, senha_hash),
        )
        logging.info("Admin seed criado: %s", email)
    conn.commit()
    cursor.close()


def _seed_demo(conn):
    """Insere dados de demonstração se admin@ufrj.br ainda não existir."""
    import datetime as _dt
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@ufrj.br'")
    if cursor.fetchone():
        cursor.close()
        return

    senha_hash = generate_password_hash("senha123")
    now = _dt.datetime.now()

    def _user(nome, email, papel):
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria) VALUES (%s,%s,%s,%s,'ATIVO',FALSE)",
            (nome, email, senha_hash, papel),
        )
        return cursor.lastrowid

    admin_id = _user("Admin UFRJ", "admin@ufrj.br", "ADMIN")
    prof1_id = _user("Professor Um", "professor1@ufrj.br", "PROFESSOR")
    prof2_id = _user("Professor Dois", "professor2@ufrj.br", "PROFESSOR")
    mon1_id = _user("Monitor Um", "monitor1@ufrj.br", "ALUNO")
    mon2_id = _user("Monitor Dois", "monitor2@ufrj.br", "ALUNO")
    aluno1_id = _user("Aluno Um", "aluno1@ufrj.br", "ALUNO")
    aluno2_id = _user("Aluno Dois", "aluno2@ufrj.br", "ALUNO")
    aluno3_id = _user("Aluno Três", "aluno3@ufrj.br", "ALUNO")
    aluno4_id = _user("Aluno Quatro", "aluno4@ufrj.br", "ALUNO")

    cursor.execute("INSERT INTO disciplinas (codigo, nome, professor_id, status) VALUES (%s,%s,%s,'ATIVA')", ("MAB001", "Cálculo I", prof1_id))
    disc1_id = cursor.lastrowid
    cursor.execute("INSERT INTO disciplinas (codigo, nome, professor_id, status) VALUES (%s,%s,%s,'ATIVA')", ("MAB002", "Álgebra Linear", prof2_id))
    disc2_id = cursor.lastrowid

    cursor.execute("INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status) VALUES (%s,%s,%s,'ATIVO')", (disc1_id, prof1_id, mon1_id))
    cursor.execute("INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status) VALUES (%s,%s,%s,'ATIVO')", (disc2_id, prof2_id, mon2_id))

    for aluno_id in [aluno1_id, aluno2_id]:
        cursor.execute("INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s,%s)", (disc1_id, aluno_id))
    for aluno_id in [aluno3_id, aluno4_id]:
        cursor.execute("INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s,%s)", (disc2_id, aluno_id))

    def _session(disc_id, mon_id, dt_inicio, dt_fim, status, assunto=None):
        cursor.execute(
            "INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status, assunto) VALUES (%s,%s,%s,%s,%s,%s)",
            (disc_id, mon_id, dt_inicio, dt_fim, status, assunto),
        )
        return cursor.lastrowid

    def _presenca(sessao_id, aluno_id, status):
        cursor.execute("INSERT INTO presencas (sessao_id, aluno_id, status) VALUES (%s,%s,%s)", (sessao_id, aluno_id, status))

    # disc1: 4 sessões CONCLUIDAS (3, 8, 15, 21 dias atrás — todas no mês corrente)
    for days_ago in [3, 8, 15, 21]:
        dt = (now - _dt.timedelta(days=days_ago)).replace(hour=14, minute=0, second=0, microsecond=0)
        sid = _session(disc1_id, mon1_id, dt, dt + _dt.timedelta(hours=1), "CONCLUIDA", "Revisão de conteúdo")
        _presenca(sid, aluno1_id, "CONFIRMADA")
        _presenca(sid, aluno2_id, "AUSENTE")

    # disc2: 2 sessões CONCLUIDAS (5, 12 dias atrás) — não cumpre mínimo de 4h
    for days_ago in [5, 12]:
        dt = (now - _dt.timedelta(days=days_ago)).replace(hour=10, minute=0, second=0, microsecond=0)
        sid = _session(disc2_id, mon2_id, dt, dt + _dt.timedelta(hours=1), "CONCLUIDA", "Revisão de conteúdo")
        _presenca(sid, aluno3_id, "CONFIRMADA")
        _presenca(sid, aluno4_id, "AUSENTE")

    # Sessões futuras (2 dias à frente)
    fut = (now + _dt.timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
    _session(disc1_id, mon1_id, fut, fut + _dt.timedelta(hours=1), "AGENDADA")
    fut2 = (now + _dt.timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    _session(disc2_id, mon2_id, fut2, fut2 + _dt.timedelta(hours=1), "AGENDADA")

    # Sessões pendentes de finalização (ontem, ainda AGENDADA)
    pend = (now - _dt.timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    _session(disc1_id, mon1_id, pend, pend + _dt.timedelta(hours=1), "AGENDADA")
    pend2 = (now - _dt.timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    _session(disc2_id, mon2_id, pend2, pend2 + _dt.timedelta(hours=1), "AGENDADA")

    conn.commit()
    cursor.close()
    logging.info("Dados de demo inseridos: admin@ufrj.br e usuários de teste.")


def init_db(app):
    try:
        _build_pool(app)
        conn = get_connection()
        _apply_schema(conn)
        _apply_migrations(conn)
        _seed_admins(conn)
        _seed_demo(conn)
        conn.close()
    except mysql.connector.Error as exc:
        logging.exception("Falha ao conectar no MySQL durante a inicializacao")
        raise RuntimeError("Falha ao inicializar o pool de conexao MySQL") from exc


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool de conexao nao inicializado")
    return _pool.get_connection()
