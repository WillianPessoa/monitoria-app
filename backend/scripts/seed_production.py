#!/usr/bin/env python3
"""
seed_production.py — Popula o banco com estado rico para a apresentação final.

Estado criado (idempotente — pode rodar várias vezes):
  • 2 professores · 3 monitores · 4 alunos comuns · 3 disciplinas
  • Slots futuros (disponíveis, agendados, 1 bloqueado)
  • 1 agendamento com data+22h → badge "Hoje/Amanhã" visível para Fernanda
  • Sessões coletivas passadas (status CONCLUIDA + assunto + presencas)
    → alimenta US18 (painel de horas), US19 (histórico professor), US20 (relatório)
  • Agendamentos individuais passados (CONFIRMADO)
  • 1 ausência registrada para diversificar os dados

Senhas: Demo@2026 (exceto admin existente: monitoria-app)

Uso (Railway):
    MYSQL_HOST=<host> MYSQL_PORT=<porta> MYSQL_USER=<user> \\
    MYSQL_PASSWORD=<senha> MYSQL_DATABASE=railway \\
    python backend/scripts/seed_production.py

Uso (local):
    python backend/scripts/seed_production.py
"""

import datetime
import os
from pathlib import Path

from werkzeug.security import generate_password_hash

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import mysql.connector  # noqa: E402

DB_CONFIG = {
    "host":        os.getenv("MYSQL_HOST", "localhost"),
    "port":        int(os.getenv("MYSQL_PORT", "3306")),
    "user":        os.getenv("MYSQL_USER", "root"),
    "password":    os.getenv("MYSQL_PASSWORD", "monitoria_root"),
    "database":    os.getenv("MYSQL_DATABASE", "monitoria_app"),
    "auth_plugin": "mysql_native_password",
}

DEMO_SENHA = "Demo@2026"


def conn():
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def upsert_user(nome, email, papel, senha=None):
    h = generate_password_hash(senha or DEMO_SENHA)
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, 'ATIVO', 0)
        ON DUPLICATE KEY UPDATE
            nome=VALUES(nome), senha_hash=VALUES(senha_hash),
            papel=VALUES(papel), status='ATIVO', senha_temporaria=0
        """,
        (nome, email, h, papel),
    )
    c.commit()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    uid = cur.fetchone()[0]
    cur.close(); c.close()
    print(f"  👤  {papel:<12} {nome:<32} ({email})")
    return uid


def upsert_disciplina(codigo, nome, professor_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO disciplinas (codigo, nome, professor_id, status)
        VALUES (%s, %s, %s, 'ATIVA')
        ON DUPLICATE KEY UPDATE nome=VALUES(nome), professor_id=VALUES(professor_id), status='ATIVA'
        """,
        (codigo, nome, professor_id),
    )
    c.commit()
    cur.execute("SELECT id FROM disciplinas WHERE codigo = %s", (codigo,))
    did = cur.fetchone()[0]
    cur.close(); c.close()
    print(f"  📚  {codigo:<10} {nome}")
    return did


def upsert_monitoria(disciplina_id, professor_id, aluno_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
        VALUES (%s, %s, %s, 'ATIVO')
        ON DUPLICATE KEY UPDATE status='ATIVO', motivo_rejeicao=NULL
        """,
        (disciplina_id, professor_id, aluno_id),
    )
    c.commit()
    cur.close(); c.close()


def enroll(disciplina_id, aluno_id):
    c = conn()
    cur = c.cursor()
    cur.execute(
        "INSERT IGNORE INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
        (disciplina_id, aluno_id),
    )
    c.commit(); cur.close(); c.close()


def upsert_slot(monitor_id, disciplina_id, data_inicio, duracao_min, local, status="DISPONIVEL"):
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    c = conn()
    cur = c.cursor()
    cur.execute(
        "SELECT id FROM disponibilidades WHERE monitor_id=%s AND data_inicio=%s AND data_fim=%s LIMIT 1",
        (monitor_id, data_inicio, data_fim),
    )
    row = cur.fetchone()
    if row:
        slot_id = row[0]
        cur.execute("UPDATE disponibilidades SET status=%s WHERE id=%s", (status, slot_id))
        c.commit()
    else:
        cur.execute(
            """
            INSERT INTO disponibilidades
                (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (disciplina_id, monitor_id, data_inicio, data_fim, local, status),
        )
        c.commit()
        slot_id = cur.lastrowid
    cur.close(); c.close()
    return slot_id


def book_slot(slot_id, aluno_id):
    """Cria agendamento CONFIRMADO. Retorna ag_id ou None se já agendado."""
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT status FROM disponibilidades WHERE id=%s", (slot_id,))
    row = cur.fetchone()
    if not row or row[0] == "AGENDADO":
        cur.close(); c.close()
        return None
    cur.execute("UPDATE disponibilidades SET status='AGENDADO' WHERE id=%s", (slot_id,))
    cur.execute(
        """
        INSERT IGNORE INTO agendamentos (disponibilidade_id, aluno_id, status)
        VALUES (%s, %s, 'CONFIRMADO')
        """,
        (slot_id, aluno_id),
    )
    c.commit()
    cur.execute(
        "SELECT id FROM agendamentos WHERE disponibilidade_id=%s AND aluno_id=%s LIMIT 1",
        (slot_id, aluno_id),
    )
    ag_id = cur.fetchone()[0]
    cur.close(); c.close()
    return ag_id


def upsert_sessao_concluida(disciplina_id, monitor_id, data_inicio, duracao_min, assunto):
    """
    Cria ou atualiza sessão coletiva passada com status CONCLUIDA e assunto.
    Alimenta US18 (painel de horas) e US19/US20 (relatórios).
    """
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    c = conn()
    cur = c.cursor()
    cur.execute(
        "SELECT id FROM monitoria_sessoes WHERE disciplina_id=%s AND data_inicio=%s LIMIT 1",
        (disciplina_id, data_inicio),
    )
    row = cur.fetchone()
    if row:
        sid = row[0]
        cur.execute(
            "UPDATE monitoria_sessoes SET status='CONCLUIDA', assunto=%s WHERE id=%s",
            (assunto, sid),
        )
        c.commit()
    else:
        cur.execute(
            """
            INSERT INTO monitoria_sessoes
                (disciplina_id, monitor_id, data_inicio, data_fim, status, assunto)
            VALUES (%s, %s, %s, %s, 'CONCLUIDA', %s)
            """,
            (disciplina_id, monitor_id, data_inicio, data_fim, assunto),
        )
        c.commit()
        sid = cur.lastrowid
    cur.close(); c.close()
    return sid


def upsert_presenca(sessao_id, aluno_id, status="CONFIRMADA"):
    """Registra presença/ausência de aluno em sessão coletiva."""
    c = conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO presencas (sessao_id, aluno_id, status)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE status=VALUES(status)
        """,
        (sessao_id, aluno_id, status),
    )
    c.commit(); cur.close(); c.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    now  = datetime.datetime.now().replace(second=0, microsecond=0)
    hoje = now.replace(hour=0, minute=0)

    def past(days, hour=14):
        return hoje - datetime.timedelta(days=days) + datetime.timedelta(hours=hour)

    print(f"\n{'='*64}")
    print("  Seed de apresentação — Monitoria App")
    print(f"  Banco: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"{'='*64}\n")

    # ── Professores ──────────────────────────────────────────────
    print("── Professores")
    ana  = upsert_user("Prof. Ana Lima",   "prof.ana@ic.ufrj.br",   "PROFESSOR")
    brun = upsert_user("Prof. Bruno Melo", "prof.bruno@ic.ufrj.br", "PROFESSOR")

    # ── Disciplinas ──────────────────────────────────────────────
    print("\n── Disciplinas")
    calc = upsert_disciplina("MAT101", "Cálculo I",              ana)
    alg  = upsert_disciplina("MAT201", "Álgebra Linear",         ana)
    poo  = upsert_disciplina("INF101", "Prog. Orientada a Obj.", brun)

    # ── Monitores ────────────────────────────────────────────────
    print("\n── Monitores")
    carlos  = upsert_user("Carlos Alves",  "carlos.monitor@ic.ufrj.br",  "ALUNO")
    diana   = upsert_user("Diana Souza",   "diana.monitor@ic.ufrj.br",   "ALUNO")
    eduardo = upsert_user("Eduardo Costa", "eduardo.monitor@ic.ufrj.br", "ALUNO")

    upsert_monitoria(calc, ana,  carlos)
    upsert_monitoria(alg,  ana,  eduardo)
    upsert_monitoria(poo,  brun, diana)

    # ── Alunos comuns ────────────────────────────────────────────
    print("\n── Alunos comuns")
    fern = upsert_user("Fernanda Gomes", "fernanda@ic.ufrj.br", "ALUNO")
    gabr = upsert_user("Gabriel Rocha",  "gabriel@ic.ufrj.br",  "ALUNO")
    hel  = upsert_user("Helena Martins", "helena@ic.ufrj.br",   "ALUNO")
    igor = upsert_user("Igor Pinto",     "igor@ic.ufrj.br",     "ALUNO")

    for a in [fern, hel, igor]: enroll(calc, a)
    for a in [gabr, hel]:       enroll(alg,  a)
    for a in [gabr, fern, igor]: enroll(poo,  a)

    # ── Slots futuros ────────────────────────────────────────────
    print("\n── Slots futuros")

    # Carlos (Cálculo I) — 3 disponíveis + 1 agendado logo + 1 bloqueado
    sc_badge = upsert_slot(carlos, calc, hoje + datetime.timedelta(hours=20),      60, "Sala B101")
    sc2      = upsert_slot(carlos, calc, hoje + datetime.timedelta(days=2, hours=14), 60, "Sala B101")
    sc3      = upsert_slot(carlos, calc, hoje + datetime.timedelta(days=4, hours=10), 60, "Sala B101")
    sc_blq   = upsert_slot(carlos, calc, hoje + datetime.timedelta(days=3, hours=10), 60, "Sala B101", "BLOQUEADO")

    # Diana (POO) — 2 disponíveis + 1 agendado
    sd1 = upsert_slot(diana, poo, hoje + datetime.timedelta(days=1, hours=16), 60, "Lab de Informática")
    sd2 = upsert_slot(diana, poo, hoje + datetime.timedelta(days=3, hours=16), 60, "Lab de Informática")
    sd3 = upsert_slot(diana, poo, hoje + datetime.timedelta(days=5, hours=14), 60, "Lab de Informática")

    # Eduardo (Álgebra) — 2 disponíveis + 1 agendado
    se1 = upsert_slot(eduardo, alg, hoje + datetime.timedelta(days=2, hours=9), 60, "Sala A205")
    se2 = upsert_slot(eduardo, alg, hoje + datetime.timedelta(days=5, hours=9), 60, "Sala A205")

    # ── Agendamentos futuros ─────────────────────────────────────
    print("\n── Agendamentos futuros")
    book_slot(sc_badge, fern)   # Fernanda → Carlos HOJE+20h  (badge Hoje/Amanhã ativo)
    print(f"    🔔  Fernanda → Carlos em +20h (badge lembrete visível)")
    book_slot(sd1, gabr)        # Gabriel  → Diana amanhã
    book_slot(se1, gabr)        # Gabriel  → Eduardo D+2

    # ── Agendamentos individuais passados ────────────────────────
    print("\n── Agendamentos individuais passados (CONFIRMADO)")

    past_slots_calc = [
        (past(14, 14), fern, "Sala B101"),
        (past(12, 14), hel,  "Sala B101"),
        (past(10, 14), igor, "Sala B101"),
        (past(8,  14), fern, "Sala B101"),
        (past(5,  14), hel,  "Sala B101"),
    ]
    for data, aluno, local in past_slots_calc:
        s = upsert_slot(carlos, calc, data, 60, local, "AGENDADO")
        book_slot(s, aluno)

    past_slots_alg = [
        (past(11, 9), gabr, "Sala A205"),
        (past(7,  9), hel,  "Sala A205"),
        (past(4,  9), gabr, "Sala A205"),
    ]
    for data, aluno, local in past_slots_alg:
        s = upsert_slot(eduardo, alg, data, 60, local, "AGENDADO")
        book_slot(s, aluno)

    past_slots_poo = [
        (past(13, 16), gabr,  "Lab de Informática"),
        (past(9,  16), fern,  "Lab de Informática"),
        (past(6,  16), igor,  "Lab de Informática"),
        (past(3,  16), gabr,  "Lab de Informática"),
    ]
    for data, aluno, local in past_slots_poo:
        s = upsert_slot(diana, poo, data, 60, local, "AGENDADO")
        book_slot(s, aluno)

    print(f"    {len(past_slots_calc)+len(past_slots_alg)+len(past_slots_poo)} atendimentos individuais")

    # ── Sessões coletivas passadas (CONCLUIDA + presencas) ───────
    # Alimenta: US18 painel de horas, US19 histórico professor, US20 relatório
    print("\n── Sessões coletivas passadas (CONCLUIDA)")

    assuntos_calc = [
        "Limites e continuidade — exercícios da lista 3",
        "Derivadas: regra da cadeia e produto",
        "Integrais indefinidas — técnicas de integração",
        "Teorema fundamental do Cálculo",
        "Série de Taylor e aplicações",
    ]
    sessoes_calc = []
    for i, assunto in enumerate(assuntos_calc):
        data = past(28 - i * 5, 15)
        sid = upsert_sessao_concluida(calc, carlos, data, 90, assunto)
        sessoes_calc.append(sid)

    # Presencas Cálculo I
    for sid in sessoes_calc[:3]:
        upsert_presenca(sid, fern)
        upsert_presenca(sid, hel)
        upsert_presenca(sid, igor, "AUSENTE")
    for sid in sessoes_calc[3:]:
        upsert_presenca(sid, fern)
        upsert_presenca(sid, hel)
        upsert_presenca(sid, igor)

    assuntos_alg = [
        "Espaços vetoriais e subespaços",
        "Transformações lineares e núcleo",
        "Autovalores e autovetores",
    ]
    sessoes_alg = []
    for i, assunto in enumerate(assuntos_alg):
        data = past(21 - i * 7, 9)
        sid = upsert_sessao_concluida(alg, eduardo, data, 90, assunto)
        sessoes_alg.append(sid)

    for sid in sessoes_alg:
        upsert_presenca(sid, gabr)
        upsert_presenca(sid, hel)

    assuntos_poo = [
        "Herança, polimorfismo e interfaces",
        "Padrão de projeto Strategy e Observer",
        "Tratamento de exceções — boas práticas",
        "Coleções e generics em Java",
    ]
    sessoes_poo = []
    for i, assunto in enumerate(assuntos_poo):
        data = past(26 - i * 6, 16)
        sid = upsert_sessao_concluida(poo, diana, data, 90, assunto)
        sessoes_poo.append(sid)

    for sid in sessoes_poo[:2]:
        upsert_presenca(sid, gabr)
        upsert_presenca(sid, fern)
        upsert_presenca(sid, igor, "AUSENTE")
    for sid in sessoes_poo[2:]:
        upsert_presenca(sid, gabr)
        upsert_presenca(sid, fern, "AUSENTE")  # 1 ausência para variar
        upsert_presenca(sid, igor)

    total_sessoes = len(sessoes_calc) + len(sessoes_alg) + len(sessoes_poo)
    print(f"    {total_sessoes} sessões concluídas com presenças registradas")

    # ── Resumo ───────────────────────────────────────────────────
    print(f"\n{'='*64}")
    print("  Credenciais de apresentação (senha padrão: Demo@2026):")
    print(f"{'='*64}")
    rows = [
        ("willian.pessoa.cs@gmail.com",  "Admin",     "monitoria-app"),
        ("prof.ana@ic.ufrj.br",          "Professor", DEMO_SENHA),
        ("prof.bruno@ic.ufrj.br",        "Professor", DEMO_SENHA),
        ("carlos.monitor@ic.ufrj.br",    "Monitor",   DEMO_SENHA),
        ("diana.monitor@ic.ufrj.br",     "Monitor",   DEMO_SENHA),
        ("eduardo.monitor@ic.ufrj.br",   "Monitor",   DEMO_SENHA),
        ("fernanda@ic.ufrj.br",          "Aluno",     DEMO_SENHA),
        ("gabriel@ic.ufrj.br",           "Aluno",     DEMO_SENHA),
        ("helena@ic.ufrj.br",            "Aluno",     DEMO_SENHA),
        ("igor@ic.ufrj.br",              "Aluno",     DEMO_SENHA),
    ]
    print(f"  {'Email':<40} {'Papel':<12} Senha")
    print(f"  {'-'*62}")
    for email, papel, senha in rows:
        print(f"  {email:<40} {papel:<12} {senha}")

    horas_carlos  = len(sessoes_calc) * 1.5
    horas_eduardo = len(sessoes_alg)  * 1.5
    horas_diana   = len(sessoes_poo)  * 1.5

    print(f"\n  Estado visível por perfil:")
    print(f"    Admin     — US18: Carlos={horas_carlos}h, Eduardo={horas_eduardo}h, Diana={horas_diana}h")
    print(f"    Admin     — US20: relatório com {total_sessoes} sessões concluídas")
    print(f"    Professor — US19: histórico de sessões + alunos atendidos")
    print(f"    Monitor   — agenda com slots futuros + histórico de horas")
    print(f"    Aluno     — Fernanda tem agendamento em +20h → badge Hoje/Amanhã")
    print(f"    Aluno     — Carlos tem 1 slot BLOQUEADO visível na agenda")
    print(f"{'='*64}\n")


if __name__ == "__main__":
    main()
