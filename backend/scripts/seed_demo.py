#!/usr/bin/env python3
"""
seed_demo.py — Limpa o banco e popula com dados de demonstração.

Cria:
  • 1 admin: admin@ufrj.br / senha123
  • 4 alunos: aluno1@ufrj.br ... aluno4@ufrj.br / senha123
  • 2 monitores (papel ALUNO): monitor1@ufrj.br, monitor2@ufrj.br / senha123
  • 2 professores: professor1@ufrj.br, professor2@ufrj.br / senha123
  • 2 disciplinas ativas:
      - Disciplina 1: professor1, monitor1, aluno1, aluno2
      - Disciplina 2: professor2, monitor2, aluno3, aluno4
  • 1 disciplina inativa (encerrada):
      - Programação Linear: professor1, monitor1 (rejeitado), aluno1, aluno2
      - Sessões concluídas de Jul–Dez 2025 (12 sessões, quinzenais)
  • 1 mês de sessões passadas para cada disciplina ativa (4 semanas)
  • Presenças: em cada sessão, apenas 1 aluno presente

Uso:
    cd backend && python scripts/seed_demo.py
"""

import datetime
import os
import sys
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

import mysql.connector

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "monitoria_root"),
    "database": os.environ.get("MYSQL_DATABASE", "monitoria_app"),
    "charset": "utf8mb4",
}

SENHA = "senha123"
HASH = generate_password_hash(SENHA)

NOW = datetime.datetime.now()


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("Limpando banco de dados...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in [
        "sessao_materiais", "presencas", "monitoria_sessoes",
        "votos", "votacao_opcoes", "votacoes",
        "agendamentos", "disponibilidades", "monitor_disponibilidade",
        "monitorias", "disciplina_alunos", "disciplinas",
        "password_reset_tokens", "usuarios",
    ]:
        cur.execute(f"TRUNCATE TABLE {table}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("Banco limpo.")

    def create_user(nome, email, papel):
        cur.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
            VALUES (%s, %s, %s, %s, 'ATIVO', FALSE)
            """,
            (nome, email, HASH, papel),
        )
        return cur.lastrowid

    print("Criando usuários...")
    admin_id = create_user("Admin UFRJ", "admin@ufrj.br", "ADMIN")

    prof1_id = create_user("Professor Um", "professor1@ufrj.br", "PROFESSOR")
    prof2_id = create_user("Professor Dois", "professor2@ufrj.br", "PROFESSOR")

    mon1_id = create_user("Monitor Um", "monitor1@ufrj.br", "ALUNO")
    mon2_id = create_user("Monitor Dois", "monitor2@ufrj.br", "ALUNO")

    aluno1_id = create_user("Aluno Um", "aluno1@ufrj.br", "ALUNO")
    aluno2_id = create_user("Aluno Dois", "aluno2@ufrj.br", "ALUNO")
    aluno3_id = create_user("Aluno Três", "aluno3@ufrj.br", "ALUNO")
    aluno4_id = create_user("Aluno Quatro", "aluno4@ufrj.br", "ALUNO")
    conn.commit()
    print("  Usuários criados.")

    print("Configurando contato e disponibilidade dos monitores...")
    # monitor1: celular (21) 99999-0001, disponível Seg 10h e Ter 14h
    cur.execute(
        "UPDATE usuarios SET contato = %s, carga_horaria_semanal = 1 WHERE id = %s",
        ("(21) 99999-0001", mon1_id),
    )
    for weekday, hora in [(1, "10:00:00"), (2, "14:00:00")]:
        cur.execute(
            "INSERT INTO monitor_disponibilidade (monitor_id, weekday, hora_inicio, status) VALUES (%s, %s, %s, 'LIVRE')",
            (mon1_id, weekday, hora),
        )

    # monitor2: celular (21) 99999-0002, disponível Qua 10h e Qui 14h
    cur.execute(
        "UPDATE usuarios SET contato = %s, carga_horaria_semanal = 1 WHERE id = %s",
        ("(21) 99999-0002", mon2_id),
    )
    for weekday, hora in [(3, "10:00:00"), (4, "14:00:00")]:
        cur.execute(
            "INSERT INTO monitor_disponibilidade (monitor_id, weekday, hora_inicio, status) VALUES (%s, %s, %s, 'LIVRE')",
            (mon2_id, weekday, hora),
        )
    conn.commit()
    print("  Contato e disponibilidade configurados.")

    print("Criando disciplinas...")
    criado_em_ativas = (NOW - datetime.timedelta(days=21)).replace(hour=9, minute=0, second=0, microsecond=0)
    cur.execute(
        "INSERT INTO disciplinas (codigo, nome, professor_id, status, criado_em) VALUES (%s, %s, %s, 'ATIVA', %s)",
        ("MAB001", "Cálculo I", prof1_id, criado_em_ativas),
    )
    disc1_id = cur.lastrowid

    cur.execute(
        "INSERT INTO disciplinas (codigo, nome, professor_id, status, criado_em) VALUES (%s, %s, %s, 'ATIVA', %s)",
        ("MAB002", "Álgebra Linear", prof2_id, criado_em_ativas),
    )
    disc2_id = cur.lastrowid

    # Disciplina inativa: encerrada ao fim do semestre 2025/2
    cur.execute(
        "INSERT INTO disciplinas (codigo, nome, professor_id, status, criado_em) VALUES (%s, %s, %s, 'INATIVA', %s)",
        ("MAB003", "Programação Linear", prof1_id, datetime.datetime(2025, 7, 1, 9, 0)),
    )
    disc3_id = cur.lastrowid
    conn.commit()
    print("  Disciplinas criadas.")

    print("Criando monitorias ativas...")
    cur.execute(
        "INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status) VALUES (%s,%s,%s,'ATIVO')",
        (disc1_id, prof1_id, mon1_id),
    )
    cur.execute(
        "INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status) VALUES (%s,%s,%s,'ATIVO')",
        (disc2_id, prof2_id, mon2_id),
    )
    # Disciplina inativa: monitoria encerrada (REJEITADO)
    cur.execute(
        "INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status, motivo_rejeicao) VALUES (%s,%s,%s,'REJEITADO','Disciplina desativada pelo admin.')",
        (disc3_id, prof1_id, mon1_id),
    )
    conn.commit()
    print("  Monitorias criadas.")

    print("Matriculando alunos...")
    for aluno_id in [aluno1_id, aluno2_id]:
        cur.execute(
            "INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
            (disc1_id, aluno_id),
        )
    for aluno_id in [aluno3_id, aluno4_id]:
        cur.execute(
            "INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
            (disc2_id, aluno_id),
        )
    # Disciplina inativa: alunos 1 e 2 permanecem matriculados
    for aluno_id in [aluno1_id, aluno2_id]:
        cur.execute(
            "INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
            (disc3_id, aluno_id),
        )
    conn.commit()
    print("  Matrículas criadas.")

    print("Criando sessões...")

    def create_session(disciplina_id, monitor_id, data_inicio, data_fim, status, assunto=None):
        cur.execute(
            """
            INSERT INTO monitoria_sessoes
                (disciplina_id, monitor_id, data_inicio, data_fim, status, assunto)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (disciplina_id, monitor_id, data_inicio, data_fim, status, assunto),
        )
        return cur.lastrowid

    def add_presenca(sessao_id, aluno_id, status):
        cur.execute(
            "INSERT INTO presencas (sessao_id, aluno_id, status) VALUES (%s, %s, %s)",
            (sessao_id, aluno_id, status),
        )

    # Disciplina 1: 4 sessões CONCLUIDAS (3, 8, 15, 21 dias atrás — todas no mês corrente)
    for days_ago in [3, 8, 15, 21]:
        dt = (NOW - datetime.timedelta(days=days_ago)).replace(hour=14, minute=0, second=0, microsecond=0)
        sid = create_session(disc1_id, mon1_id, dt, dt + datetime.timedelta(hours=1), "CONCLUIDA", "Revisão de conteúdo")
        add_presenca(sid, aluno1_id, "CONFIRMADA")
        add_presenca(sid, aluno2_id, "AUSENTE")

    # Disciplina 2: 2 sessões CONCLUIDAS (5, 12 dias atrás) — NÃO cumpre mínimo de 4h
    for days_ago in [5, 12]:
        dt = (NOW - datetime.timedelta(days=days_ago)).replace(hour=10, minute=0, second=0, microsecond=0)
        sid = create_session(disc2_id, mon2_id, dt, dt + datetime.timedelta(hours=1), "CONCLUIDA", "Revisão de conteúdo")
        add_presenca(sid, aluno3_id, "CONFIRMADA")
        add_presenca(sid, aluno4_id, "AUSENTE")

    # Sessões futuras (2 dias à frente)
    fut1 = (NOW + datetime.timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
    create_session(disc1_id, mon1_id, fut1, fut1 + datetime.timedelta(hours=1), "AGENDADA")
    fut2 = (NOW + datetime.timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    create_session(disc2_id, mon2_id, fut2, fut2 + datetime.timedelta(hours=1), "AGENDADA")

    # Sessões pendentes de finalização (ontem, ainda AGENDADA)
    pend1 = (NOW - datetime.timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    create_session(disc1_id, mon1_id, pend1, pend1 + datetime.timedelta(hours=1), "AGENDADA")
    pend2 = (NOW - datetime.timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    create_session(disc2_id, mon2_id, pend2, pend2 + datetime.timedelta(hours=1), "AGENDADA")

    # Disciplina inativa (MAB003): 12 sessões quinzenais de Jul a Dez 2025
    assuntos_disc3 = [
        "Introdução à Programação Linear",
        "Modelagem de problemas de otimização",
        "Método Simplex — fundamentos",
        "Método Simplex — tableau e pivotamento",
        "Dualidade e interpretação econômica",
        "Análise de sensibilidade",
        "Programação inteira — introdução",
        "Branch and Bound",
        "Programação linear aplicada à logística",
        "Revisão geral e exercícios",
        "Simulado de prova",
        "Encerramento e avaliação do semestre",
    ]
    # Quinzenalmente: 1/7, 15/7, 1/8, 15/8, 1/9, 15/9, 1/10, 15/10, 3/11, 17/11, 1/12, 15/12 de 2025
    datas_disc3 = [
        datetime.datetime(2025, 7, 1, 14, 0),
        datetime.datetime(2025, 7, 15, 14, 0),
        datetime.datetime(2025, 8, 5, 14, 0),
        datetime.datetime(2025, 8, 19, 14, 0),
        datetime.datetime(2025, 9, 2, 14, 0),
        datetime.datetime(2025, 9, 16, 14, 0),
        datetime.datetime(2025, 10, 7, 14, 0),
        datetime.datetime(2025, 10, 21, 14, 0),
        datetime.datetime(2025, 11, 4, 14, 0),
        datetime.datetime(2025, 11, 18, 14, 0),
        datetime.datetime(2025, 12, 2, 14, 0),
        datetime.datetime(2025, 12, 16, 14, 0),
    ]
    # Aluno1 presente nas ímpares, ausente nas pares; Aluno2 o inverso
    for i, dt in enumerate(datas_disc3):
        sid = create_session(
            disc3_id, mon1_id,
            dt, dt + datetime.timedelta(hours=2),
            "CONCLUIDA",
            assuntos_disc3[i],
        )
        add_presenca(sid, aluno1_id, "CONFIRMADA" if i % 2 == 0 else "AUSENTE")
        add_presenca(sid, aluno2_id, "AUSENTE" if i % 2 == 0 else "CONFIRMADA")

    conn.commit()
    print("  Sessões e presenças criadas.")

    cur.close()
    conn.close()

    print("\n✓ Seed concluído com sucesso!")
    print("\nCredenciais (senha: senha123):")
    print("  admin@ufrj.br           → ADMIN")
    print("  professor1@ufrj.br      → PROFESSOR (Cálculo I + Programação Linear [inativa])")
    print("  professor2@ufrj.br      → PROFESSOR (Álgebra Linear)")
    print("  monitor1@ufrj.br        → MONITOR (Cálculo I) — horas OK; ex-monitor de Prog. Linear")
    print("  monitor2@ufrj.br        → MONITOR (Álgebra Linear) — horas INSUFICIENTES")
    print("  aluno1@ufrj.br          → ALUNO (Cálculo I + Programação Linear [inativa])")
    print("  aluno2@ufrj.br          → ALUNO (Cálculo I + Programação Linear [inativa])")
    print("  aluno3@ufrj.br          → ALUNO (Álgebra Linear)")
    print("  aluno4@ufrj.br          → ALUNO (Álgebra Linear)")


if __name__ == "__main__":
    main()
