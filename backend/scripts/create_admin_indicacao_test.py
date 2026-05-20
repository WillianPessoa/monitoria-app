#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from pathlib import Path
from http.client import HTTPConnection

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    with open(ENV_PATH, encoding="utf-8") as env_file:
        for line in env_file:
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "monitoria_app")

SCHEMA_FILE = BASE_DIR / "db" / "schema.sql"
LOG_FILE = Path("/tmp/monitoria-app-test.log")


def connect(database=None):
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        auth_plugin="mysql_native_password",
    )


def run_query(cursor, query, params=None):
    cursor.execute(query, params or ())


def ensure_database():
    conn = connect()
    cursor = conn.cursor()
    run_query(cursor, f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()


def ensure_schema():
    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(cursor, "SHOW TABLES LIKE 'usuarios';")
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return
    cursor.close()
    conn.close()

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    conn = connect()
    cursor = conn.cursor()
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            run_query(cursor, statement)
    conn.commit()
    cursor.close()
    conn.close()


def insert_user(nome, email, senha, papel):
    password_hash = generate_password_hash(senha)
    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(
        cursor,
        """
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, 'ATIVO', FALSE)
        ON DUPLICATE KEY UPDATE
          nome = VALUES(nome),
          senha_hash = VALUES(senha_hash),
          papel = VALUES(papel),
          status = 'ATIVO',
          senha_temporaria = FALSE
        """,
        (nome, email, password_hash, papel),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_id_by_email(email):
    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(cursor, "SELECT id FROM usuarios WHERE email = %s LIMIT 1", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def insert_disciplina(codigo, nome, professor_id):
    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(
        cursor,
        """
        INSERT INTO disciplinas (codigo, nome, professor_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE nome = VALUES(nome), professor_id = VALUES(professor_id)
        """,
        (codigo, nome, professor_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_monitoria(disciplina_id, professor_id, aluno_id):
    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(
        cursor,
        """
        INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
        VALUES (%s, %s, %s, 'PENDENTE_APROVACAO')
        ON DUPLICATE KEY UPDATE status = 'PENDENTE_APROVACAO', motivo_rejeicao = NULL, atualizado_em = CURRENT_TIMESTAMP
        """,
        (disciplina_id, professor_id, aluno_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def wait_for_health(url="127.0.0.1", port=5000, path="/health", timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            conn = HTTPConnection(url, port, timeout=3)
            conn.request("GET", path)
            response = conn.getresponse()
            if response.status == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    print("[1/5] Garantindo banco e schema...")
    ensure_database()
    ensure_schema()

    print("[2/5] Criando admin e usuarios de teste...")
    insert_user("AdminTeste", "admin@teste.com", "AdminSenha123", "ADMIN")
    insert_user("ProfTeste", "prof@teste.com", "ProfSenha123", "PROFESSOR")
    insert_user("AlunoTeste", "aluno@teste.com", "AlunoSenha123", "ALUNO")

    professor_id = get_id_by_email("prof@teste.com")
    aluno_id = get_id_by_email("aluno@teste.com")
    if not professor_id or not aluno_id:
        print("Erro: professor ou aluno de teste nao foi criado.")
        sys.exit(1)

    print("[3/5] Criando disciplina de teste...")
    insert_disciplina("TESTE101", "Disciplina de Teste", professor_id)

    conn = connect(MYSQL_DATABASE)
    cursor = conn.cursor()
    run_query(cursor, "SELECT id FROM disciplinas WHERE codigo = %s LIMIT 1", ("TESTE101",))
    disciplina_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    print("[4/5] Criando indicacao pendente de monitor...")
    insert_monitoria(disciplina_id, professor_id, aluno_id)

    print("[5/5] Inicializando app...")
    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [sys.executable, str(BASE_DIR / "app.py")],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR),
        )

    if wait_for_health():
        print("Aplicacao iniciada com sucesso.")
        print("Admin: AdminTeste / AdminSenha123")
        print("URL: http://localhost:5000")
        print(f"PID do app: {process.pid}")
        print(f"Log: {LOG_FILE}")
        print("Pressione Ctrl+C para manter a aplicacao rodando no terminal atual.")
        process.wait()
    else:
        print("Erro: aplicacao nao respondeu em http://localhost:5000/health no tempo esperado.")
        print(f"Verifique o log em {LOG_FILE}")
        process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
