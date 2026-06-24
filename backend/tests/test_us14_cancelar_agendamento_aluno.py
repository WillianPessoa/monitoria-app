"""
B3 — Aluno reverte ausência: AUSENTE → CONFIRMADA

Rota: POST /disciplinas/<id>/presenca  (status=CONFIRMADA)

Critérios de aceitação:

  C1  Aluno com status AUSENTE pode reverter para CONFIRMADA antes da sessão começar
  C2  Após reverter, presença fica CONFIRMADA no banco
  C3  Sessão já iniciada não permite reversão
"""

import datetime

import pytest

from db.connection import get_connection
from utils.time import now_sp_naive


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_sessao(disciplina_id, monitor_id, data_inicio, duracao_min=60):
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, 'AGENDADA')
        """,
        (disciplina_id, monitor_id, data_inicio, data_fim),
    )
    conn.commit()
    sessao_id = cur.lastrowid
    cur.close()
    conn.close()
    return sessao_id


def _set_presenca(sessao_id, aluno_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO presencas (sessao_id, aluno_id, status)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """,
        (sessao_id, aluno_id, status),
    )
    conn.commit()
    cur.close()
    conn.close()


def _get_presenca_status(sessao_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT status FROM presencas WHERE sessao_id = %s AND aluno_id = %s",
        (sessao_id, aluno_id),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


def _matricular(disciplina_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT IGNORE INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
        (disciplina_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestB3ReverterAusencia:

    def test_aluno_ausente_pode_confirmar_novamente(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno com AUSENTE pode enviar CONFIRMADA antes da sessão começar → flash de sucesso."""
        setup = make_monitoria_ativa("b3c1")
        aluno_email = "aluno.b3c1@teste.com"
        aluno_id = make_user("Aluno B3C1", aluno_email, "ALUNO")
        _matricular(setup["disc_id"], aluno_id)

        data_inicio = now_sp_naive() + datetime.timedelta(hours=8)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], data_inicio)
        _set_presenca(sessao_id, aluno_id, "AUSENTE")

        client.post("/auth/login", data={"email": aluno_email, "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "atualizado" in body.lower() or "sucesso" in body.lower()

    def test_aluno_ausente_vira_confirmada_no_banco(self, client, make_user, make_monitoria_ativa):
        """C2: Após reversão, status no banco é CONFIRMADA."""
        setup = make_monitoria_ativa("b3c2")
        aluno_email = "aluno.b3c2@teste.com"
        aluno_id = make_user("Aluno B3C2", aluno_email, "ALUNO")
        _matricular(setup["disc_id"], aluno_id)

        data_inicio = now_sp_naive() + datetime.timedelta(hours=8)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], data_inicio)
        _set_presenca(sessao_id, aluno_id, "AUSENTE")

        client.post("/auth/login", data={"email": aluno_email, "senha": "Senha@Teste1"})
        client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        assert _get_presenca_status(sessao_id, aluno_id) == "CONFIRMADA"

    def test_sessao_ja_iniciada_nao_permite_reversao(self, client, make_user, make_monitoria_ativa):
        """C3: Sessão já iniciada (data_inicio no passado em SP) → não permite atualizar presença."""
        setup = make_monitoria_ativa("b3c3")
        aluno_email = "aluno.b3c3@teste.com"
        aluno_id = make_user("Aluno B3C3", aluno_email, "ALUNO")
        _matricular(setup["disc_id"], aluno_id)

        data_inicio = now_sp_naive() - datetime.timedelta(hours=1)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], data_inicio)
        _set_presenca(sessao_id, aluno_id, "AUSENTE")

        client.post("/auth/login", data={"email": aluno_email, "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "já começou" in body.lower() or "erro" in body.lower() or response.status_code in (200, 302)
        assert _get_presenca_status(sessao_id, aluno_id) == "AUSENTE"
