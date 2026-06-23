#!/usr/bin/env python3
"""
seed_production.py — Popula o banco com dados realistas para a apresentação final.

Cria (idempotente — pode rodar múltiplas vezes sem duplicar):
  • 2 professores
  • 3 alunos-monitores (ALUNO + monitoria ATIVA)
  • 3 alunos comuns
  • 3 disciplinas
  • Matrículas dos alunos nas disciplinas
  • Disponibilidades futuras para cada monitor
  • Agendamentos de alunos

Uso (Railway):
    Defina as variáveis de ambiente com as credenciais do Railway e rode:

    MYSQL_HOST=<host-railway> MYSQL_PORT=<porta> \
    MYSQL_USER=<user> MYSQL_PASSWORD=<senha> \
    MYSQL_DATABASE=railway \
    python backend/scripts/seed_production.py

    As credenciais estão em: Railway → seu serviço MySQL → Variables
    (DATABASE_URL ou as variáveis MYSQL_HOST, MYSQL_PORT, etc.)

Uso (local):
    python backend/scripts/seed_production.py
    (usa defaults: root / monitoria_root / monitoria_app)

Credenciais de apresentação (senha padrão para todos): Demo@2026
"""

import datetime
import os
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

# Lê .env local se existir
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import mysql.connector  # noqa: E402  (import after env setup)


# ---------------------------------------------------------------------------
# Configuração de conexão
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "monitoria_root"),
    "database": os.getenv("MYSQL_DATABASE", "monitoria_app"),
    "auth_plugin": "mysql_native_password",
}

DEMO_SENHA = "Demo@2026"


def conn():
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def upsert_user(nome, email, papel):
    """Cria ou atualiza usuário com senha Demo@2026 e status ATIVO."""
    h = generate_password_hash(DEMO_SENHA)
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, 'ATIVO', 0)
        ON DUPLICATE KEY UPDATE
            nome          = VALUES(nome),
            senha_hash    = VALUES(senha_hash),
            papel         = VALUES(papel),
            status        = 'ATIVO',
            senha_temporaria = 0
        """,
        (nome, email, h, papel),
    )
    c.commit()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    uid = cur.fetchone()[0]
    cur.close()
    c.close()
    print(f"  👤  {papel:<12} {nome:<30} ({email})")
    return uid


def upsert_disciplina(codigo, nome, professor_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO disciplinas (codigo, nome, professor_id, status)
        VALUES (%s, %s, %s, 'ATIVA')
        ON DUPLICATE KEY UPDATE
            nome         = VALUES(nome),
            professor_id = VALUES(professor_id),
            status       = 'ATIVA'
        """,
        (codigo, nome, professor_id),
    )
    c.commit()
    cur.execute("SELECT id FROM disciplinas WHERE codigo = %s", (codigo,))
    did = cur.fetchone()[0]
    cur.close()
    c.close()
    print(f"  📚  {codigo:<10} {nome}")
    return did


def upsert_monitoria_ativa(disciplina_id, professor_id, aluno_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
        VALUES (%s, %s, %s, 'ATIVO')
        ON DUPLICATE KEY UPDATE status = 'ATIVO', motivo_rejeicao = NULL
        """,
        (disciplina_id, professor_id, aluno_id),
    )
    c.commit()
    cur.close()
    c.close()


def enroll_aluno(disciplina_id, aluno_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        "INSERT IGNORE INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
        (disciplina_id, aluno_id),
    )
    c.commit()
    cur.close()
    c.close()


def upsert_slot(monitor_id, disciplina_id, data_inicio, duracao_min, local):
    """Cria disponibilidade se não existe uma do mesmo monitor no mesmo horário."""
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    c = conn()
    cur = c.cursor()
    # Verifica overlap exato para idempotência
    cur.execute(
        """
        SELECT id FROM disponibilidades
        WHERE monitor_id = %s AND data_inicio = %s AND data_fim = %s
        LIMIT 1
        """,
        (monitor_id, data_inicio, data_fim),
    )
    row = cur.fetchone()
    if row:
        slot_id = row[0]
    else:
        cur.execute(
            """
            INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
            VALUES (%s, %s, %s, %s, %s, 'DISPONIVEL')
            """,
            (disciplina_id, monitor_id, data_inicio, data_fim, local),
        )
        c.commit()
        slot_id = cur.lastrowid
        print(f"  🕐  Slot {data_inicio.strftime('%d/%m %H:%M')}–{data_fim.strftime('%H:%M')} @ {local}")
    cur.close()
    c.close()
    return slot_id


def book_slot(slot_id, aluno_id):
    """Cria agendamento se slot ainda está disponível."""
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT status FROM disponibilidades WHERE id = %s", (slot_id,))
    row = cur.fetchone()
    if not row or row[0] != "DISPONIVEL":
        cur.close()
        c.close()
        return
    cur.execute("UPDATE disponibilidades SET status = 'AGENDADO' WHERE id = %s", (slot_id,))
    cur.execute(
        "INSERT IGNORE INTO agendamentos (disponibilidade_id, aluno_id, status) VALUES (%s, %s, 'CONFIRMADO')",
        (slot_id, aluno_id),
    )
    c.commit()
    cur.close()
    c.close()
    print(f"  ✅  Agendamento slot {slot_id} → aluno {aluno_id}")


# ---------------------------------------------------------------------------
# Dados de apresentação
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'='*58}")
    print("  Seed de apresentação — Monitoria App")
    print(f"  Banco: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"{'='*58}\n")

    # ── Professores ─────────────────────────────────────────────
    print("── Professores")
    ana  = upsert_user("Prof. Ana Lima",  "prof.ana@ic.ufrj.br",   "PROFESSOR")
    brun = upsert_user("Prof. Bruno Melo","prof.bruno@ic.ufrj.br", "PROFESSOR")

    # ── Disciplinas ─────────────────────────────────────────────
    print("\n── Disciplinas")
    calc = upsert_disciplina("MAT101", "Cálculo I",             ana)
    alg  = upsert_disciplina("MAT201", "Álgebra Linear",        ana)
    poo  = upsert_disciplina("INF101", "Prog. Orientada a Obj.",brun)

    # ── Alunos-monitores ────────────────────────────────────────
    print("\n── Alunos-monitores (papel=ALUNO + monitoria ATIVA)")
    carlos  = upsert_user("Carlos Alves",   "carlos.monitor@ic.ufrj.br",  "ALUNO")
    diana   = upsert_user("Diana Souza",    "diana.monitor@ic.ufrj.br",   "ALUNO")
    eduardo = upsert_user("Eduardo Costa",  "eduardo.monitor@ic.ufrj.br", "ALUNO")

    upsert_monitoria_ativa(calc, ana,  carlos)
    upsert_monitoria_ativa(poo,  brun, diana)
    upsert_monitoria_ativa(alg,  ana,  eduardo)

    # ── Alunos comuns ───────────────────────────────────────────
    print("\n── Alunos comuns")
    fern = upsert_user("Fernanda Gomes", "fernanda@ic.ufrj.br", "ALUNO")
    gabr = upsert_user("Gabriel Rocha",  "gabriel@ic.ufrj.br",  "ALUNO")
    hel  = upsert_user("Helena Martins", "helena@ic.ufrj.br",   "ALUNO")

    # Matrículas
    enroll_aluno(calc, fern); enroll_aluno(calc, hel)
    enroll_aluno(poo,  gabr); enroll_aluno(poo,  hel)
    enroll_aluno(alg,  gabr)

    # ── Disponibilidades ────────────────────────────────────────
    print("\n── Disponibilidades (horários futuros)")
    hoje = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Carlos (Cálculo I)
    s1 = upsert_slot(carlos,  calc, hoje + datetime.timedelta(days=1, hours=14), 120, "Sala B101")
    s2 = upsert_slot(carlos,  calc, hoje + datetime.timedelta(days=2, hours=10), 120, "Sala B101")
    s3 = upsert_slot(carlos,  calc, hoje + datetime.timedelta(days=4, hours=14), 120, "Sala B101")

    # Diana (POO)
    s4 = upsert_slot(diana,   poo,  hoje + datetime.timedelta(days=1, hours=16), 120, "Lab de Informática")
    s5 = upsert_slot(diana,   poo,  hoje + datetime.timedelta(days=3, hours=16), 120, "Lab de Informática")

    # Eduardo (Álgebra)
    s6 = upsert_slot(eduardo, alg,  hoje + datetime.timedelta(days=2, hours=9),  120, "Sala A205")
    s7 = upsert_slot(eduardo, alg,  hoje + datetime.timedelta(days=5, hours=9),  120, "Sala A205")

    # ── Agendamentos ────────────────────────────────────────────
    print("\n── Agendamentos")
    book_slot(s1, fern)   # Fernanda agenda Carlos amanhã 14h
    book_slot(s4, gabr)   # Gabriel agenda Diana amanhã 16h
    book_slot(s6, gabr)   # Gabriel agenda Eduardo depois de amanhã 9h

    # ── Resumo ──────────────────────────────────────────────────
    print(f"\n{'='*58}")
    print("  Seed concluído! Credenciais de apresentação:")
    print(f"{'='*58}")
    print(f"  {'Email':<35} {'Papel':<12} Senha")
    print(f"  {'-'*55}")
    users = [
        ("willian.pessoa.cs@gmail.com",   "Admin",    "monitoria-app"),
        ("prof.ana@ic.ufrj.br",           "Professor",DEMO_SENHA),
        ("prof.bruno@ic.ufrj.br",         "Professor",DEMO_SENHA),
        ("carlos.monitor@ic.ufrj.br",     "Monitor",  DEMO_SENHA),
        ("diana.monitor@ic.ufrj.br",      "Monitor",  DEMO_SENHA),
        ("eduardo.monitor@ic.ufrj.br",    "Monitor",  DEMO_SENHA),
        ("fernanda@ic.ufrj.br",           "Aluno",    DEMO_SENHA),
        ("gabriel@ic.ufrj.br",            "Aluno",    DEMO_SENHA),
        ("helena@ic.ufrj.br",             "Aluno",    DEMO_SENHA),
    ]
    for email, papel, senha in users:
        print(f"  {email:<35} {papel:<12} {senha}")
    print(f"{'='*58}\n")


if __name__ == "__main__":
    main()
