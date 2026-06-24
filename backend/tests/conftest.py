"""
Fixtures compartilhadas por todos os testes.

Setup de sessão:
  - Dropa e recria o banco `monitoria_test` (isolado de `monitoria_app`)
  - Sobe o Flask apontando para esse banco
  - Aplica schema + migrations + seed de admins (via create_app → init_db)

Isolamento por teste (autouse):
  - Após cada teste, trunca todas as tabelas e restaura os admins seed
  - Cada teste começa com estado limpo e previsível

Uso:
  - `client`       → test client limpo (sem sessão)
  - `admin_client` → test client já logado como admin
  - `make_user`    → cria usuário direto no banco para montar pré-condições
"""

import os

import mysql.connector
import pytest
from werkzeug.security import generate_password_hash

# Define o banco de testes ANTES de qualquer import da aplicação.
# Config() lê os env vars no momento em que o módulo é importado.
os.environ.setdefault("MYSQL_DATABASE", "monitoria_test")
os.environ.setdefault("MYSQL_POOL_NAME", "monitoria_test_pool")

from app import create_app  # noqa: E402
from db.connection import _MIGRATIONS_DIR, _seed_admins, get_connection  # noqa: E402

ADMIN_EMAIL = "willian.pessoa.cs@gmail.com"
ADMIN_PASSWORD = "monitoria-app"

# Configuração de conexão raiz (sem banco definido)
_DB_ROOT = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "monitoria_root"),
}

# Ordem de truncagem respeita as FKs (filhos antes dos pais)
_TABLES = [
    "votos",
    "votacao_opcoes",
    "votacoes",
    "presencas",
    "monitoria_sessoes",
    "agendamentos",
    "disponibilidades",
    "monitor_disponibilidade",
    "disciplina_alunos",
    "monitorias",
    "disciplinas",
    "password_reset_tokens",
    "usuarios",
]


# ---------------------------------------------------------------------------
# Fixtures de infraestrutura
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app():
    """
    Cria o banco `monitoria_test` do zero e sobe o Flask uma única vez por sessão.

    Problema: schema.sql já inclui colunas que algumas migrations adicionariam
    (ex: carga_horaria_semanal). Criar o banco do zero a partir do schema e depois
    rodar as migrations causa "Duplicate column name".

    Solução: pré-marcar todas as migrations como aplicadas antes de chamar
    create_app(). Assim _apply_migrations() as ignora e apenas o schema.sql é
    executado, que é exatamente o estado correto para um banco recém-criado.
    """
    # 1. Cria banco de teste do zero
    root = mysql.connector.connect(**_DB_ROOT)
    cur = root.cursor()
    cur.execute("DROP DATABASE IF EXISTS monitoria_test")
    cur.execute(
        "CREATE DATABASE monitoria_test "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.close()
    root.close()

    # 2. Pré-marca todas as migrations como aplicadas
    seed_conn = mysql.connector.connect(**_DB_ROOT, database="monitoria_test")
    seed_cur = seed_conn.cursor()
    seed_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            aplicado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    if os.path.isdir(_MIGRATIONS_DIR):
        for filename in sorted(
            f for f in os.listdir(_MIGRATIONS_DIR) if f.endswith(".sql")
        ):
            seed_cur.execute(
                "INSERT IGNORE INTO migrations (filename) VALUES (%s)", (filename,)
            )
    seed_conn.commit()
    seed_cur.close()
    seed_conn.close()

    # 3. Sobe o Flask — init_db aplica schema + pula migrations (já marcadas) + seed admins
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    yield flask_app


@pytest.fixture
def client(app):
    """Test client limpo — sem sessão ativa."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db(app):
    """
    Teardown: após cada teste trunca todas as tabelas e restaura os admins seed.
    O `yield` garante que o banco não é limpo ANTES do teste — apenas depois.
    """
    yield
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in _TABLES:
        cur.execute(f"TRUNCATE TABLE {table}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    conn.close()

    conn = get_connection()
    _seed_admins(conn)
    conn.close()


# ---------------------------------------------------------------------------
# Fixtures de autenticação e dados
# ---------------------------------------------------------------------------


@pytest.fixture
def admin_client(client):
    """Test client já autenticado como admin (seed: willian.pessoa.cs@gmail.com)."""
    client.post("/auth/login", data={"email": ADMIN_EMAIL, "senha": ADMIN_PASSWORD})
    return client


@pytest.fixture
def monitor_client(client, make_user):
    """
    Client já autenticado como monitor.
    Insere papel=MONITOR direto no banco — monitores reais são ALUNOs
    com indicação aprovada, mas para testar o comportamento da rota
    o papel=MONITOR na sessão é suficiente.
    """
    make_user("Monitor Teste", "monitor@teste.com", "MONITOR")
    client.post("/auth/login", data={"email": "monitor@teste.com", "senha": "Senha@Teste1"})
    return client


@pytest.fixture
def aluno_client(client, make_user):
    """Client já autenticado como aluno comum (sem monitoria ativa)."""
    make_user("Aluno Teste", "aluno@teste.com", "ALUNO")
    client.post("/auth/login", data={"email": "aluno@teste.com", "senha": "Senha@Teste1"})
    return client


@pytest.fixture
def make_user():
    """
    Cria um usuário diretamente no banco, sem passar pela rota HTTP.
    Útil para montar pré-condições de testes que não testam o cadastro em si.

    Parâmetros:
        nome    — nome completo
        email   — email único
        papel   — "ALUNO" | "PROFESSOR" | "ADMIN" | "MONITOR"
        status  — "ATIVO" (padrão) | "PENDENTE" | "INATIVO"
        senha   — senha em texto claro (será hasheada)

    Retorna o id do usuário criado.
    """
    def _create(nome, email, papel, status="ATIVO", senha="Senha@Teste1"):
        password_hash = generate_password_hash(senha)
        temporaria = 1 if status == "PENDENTE" else 0
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nome, email, password_hash, papel.upper(), status.upper(), temporaria),
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        conn.close()
        return user_id

    return _create


@pytest.fixture
def make_monitoria_ativa(make_user):
    """
    Factory: cria professor + disciplina + aluno com monitoria ATIVA.
    Retorna dict com IDs e credenciais para login do aluno-monitor.

    Uso:
        setup = make_monitoria_ativa("us10c1")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
    """
    def _create(prefix="agenda"):
        prof_id = make_user(f"Prof {prefix}", f"prof.{prefix}@teste.com", "PROFESSOR")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO disciplinas (codigo, nome, professor_id) VALUES (%s, %s, %s)",
            (f"D{prefix.upper()[:9]}", f"Disciplina {prefix}", prof_id),
        )
        conn.commit()
        disc_id = cur.lastrowid
        cur.close()
        conn.close()

        aluno_id = make_user(f"Monitor {prefix}", f"mon.{prefix}@teste.com", "ALUNO")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
            VALUES (%s, %s, %s, 'ATIVO')
            """,
            (disc_id, prof_id, aluno_id),
        )
        conn.commit()
        cur.close()
        conn.close()

        return {
            "prof_id": prof_id,
            "disc_id": disc_id,
            "aluno_id": aluno_id,
            "monitor_email": f"mon.{prefix}@teste.com",
            "monitor_senha": "Senha@Teste1",
        }

    return _create


@pytest.fixture
def make_sessao(make_monitoria_ativa):
    """
    Factory: cria professor + disciplina + aluno-monitor com monitoria ATIVA + monitoria_sessao.

    Parâmetros:
        prefix   — string única por teste (ex: "us13c1")
        past     — True  → sessão no passado (para registrar presença)
                   False → sessão no futuro 8h à frente (para testar cancelamento)
        aluno_id — se informado, cria uma presença CONFIRMADA para esse aluno

    Retorna dict com: prof_id, disc_id, aluno_id, monitor_email, monitor_senha, sessao_id
    """
    import datetime as _dt

    def _create(prefix, past=True, aluno_id=None):
        from utils.time import now_sp_naive as _now_sp
        setup = make_monitoria_ativa(prefix)
        now = _now_sp()

        if past:
            data_inicio = now - _dt.timedelta(hours=4)
            data_fim    = now - _dt.timedelta(hours=2)
        else:
            data_inicio = now + _dt.timedelta(hours=8)
            data_fim    = data_inicio + _dt.timedelta(hours=2)

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status)
            VALUES (%s, %s, %s, %s, 'AGENDADA')
            """,
            (setup["disc_id"], setup["aluno_id"], data_inicio, data_fim),
        )
        conn.commit()
        sessao_id = cur.lastrowid

        if aluno_id is not None:
            cur.execute(
                """
                INSERT IGNORE INTO presencas (sessao_id, aluno_id, status)
                VALUES (%s, %s, 'CONFIRMADA')
                """,
                (sessao_id, aluno_id),
            )
            conn.commit()

        cur.close()
        conn.close()

        return {**setup, "sessao_id": sessao_id}

    return _create
