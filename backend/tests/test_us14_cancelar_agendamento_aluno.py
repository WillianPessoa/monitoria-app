"""
US14 — Aluno cancela um agendamento

Rota: POST /agenda/agendamentos/<int:agendamento_id>/cancelar

Regra do PO: cancelamento permitido apenas com mais de 6 horas de antecedência.

Critérios de aceitação:

  C1  Cancelamento com mais de 6h → sucesso
      Given: aluno tem agendamento confirmado em horário > 6h à frente
      When:  solicita cancelamento
      Then:  agendamento cancelado, slot volta a DISPONIVEL, flash de sucesso

  C2  Cancelamento com menos de 6h → bloqueado — REQUISITO DO PO
      Given: horário dentro de 6h
      When:  aluno solicita cancelamento
      Then:  sistema rejeita com mensagem de antecedência mínima, slot permanece AGENDADO

Cenários extras:
  C3  Aluno não pode cancelar agendamento de outro aluno
  C4  Não autenticado → redireciona para login
"""

import datetime

import pytest

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_slot_with_booking(disc_id, monitor_id, aluno_id, data_inicio, duracao_min=120):
    """Cria disponibilidade e agendamento direto no banco."""
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, 'AGENDADO')
        """,
        (disc_id, monitor_id, data_inicio, data_fim),
    )
    conn.commit()
    slot_id = cur.lastrowid
    cur.execute(
        "INSERT INTO agendamentos (disponibilidade_id, aluno_id, status) VALUES (%s, %s, 'CONFIRMADO')",
        (slot_id, aluno_id),
    )
    conn.commit()
    agendamento_id = cur.lastrowid
    cur.close()
    conn.close()
    return slot_id, agendamento_id


def _get_slot_status(slot_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM disponibilidades WHERE id = %s", (slot_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


def _get_agendamento_status(agendamento_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM agendamentos WHERE id = %s", (agendamento_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS14CancelarAgendamentoAluno:

    # -----------------------------------------------------------------------
    # C1 — Cancelamento com mais de 6h → sucesso
    # -----------------------------------------------------------------------

    def test_aluno_cancela_agendamento_com_mais_de_6h(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno cancela agendamento > 6h à frente → flash de sucesso."""
        setup = make_monitoria_ativa("us14c1")
        aluno_id = make_user("Aluno US14", "aluno.us14c1@teste.com", "ALUNO")
        data_inicio = datetime.datetime.now() + datetime.timedelta(hours=8)
        slot_id, agendamento_id = _create_slot_with_booking(
            setup["disc_id"], setup["aluno_id"], aluno_id, data_inicio
        )

        client.post("/auth/login", data={"email": "aluno.us14c1@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/agenda/agendamentos/{agendamento_id}/cancelar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "cancelado" in body.lower()

    def test_cancelamento_mais_de_6h_slot_volta_disponivel(self, client, make_user, make_monitoria_ativa):
        """C1: Após cancelamento com > 6h, slot volta a DISPONIVEL e agendamento vira CANCELADO."""
        setup = make_monitoria_ativa("us14c1b")
        aluno_id = make_user("Aluno US14b", "aluno.us14c1b@teste.com", "ALUNO")
        data_inicio = datetime.datetime.now() + datetime.timedelta(hours=8)
        slot_id, agendamento_id = _create_slot_with_booking(
            setup["disc_id"], setup["aluno_id"], aluno_id, data_inicio
        )

        client.post("/auth/login", data={"email": "aluno.us14c1b@teste.com", "senha": "Senha@Teste1"})
        client.post(f"/agenda/agendamentos/{agendamento_id}/cancelar", follow_redirects=True)

        assert _get_slot_status(slot_id) == "DISPONIVEL"
        assert _get_agendamento_status(agendamento_id) == "CANCELADO"

    # -----------------------------------------------------------------------
    # C2 — Cancelamento com menos de 6h → bloqueado (REQUISITO DO PO)
    # -----------------------------------------------------------------------

    def test_aluno_nao_pode_cancelar_com_menos_de_6h(self, client, make_user, make_monitoria_ativa):
        """C2 — REQUISITO DO PO: Cancelamento com < 6h de antecedência é bloqueado."""
        setup = make_monitoria_ativa("us14c2")
        aluno_id = make_user("Aluno US14c2", "aluno.us14c2@teste.com", "ALUNO")
        data_inicio = datetime.datetime.now() + datetime.timedelta(hours=3)  # < 6h
        slot_id, agendamento_id = _create_slot_with_booking(
            setup["disc_id"], setup["aluno_id"], aluno_id, data_inicio
        )

        client.post("/auth/login", data={"email": "aluno.us14c2@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/agenda/agendamentos/{agendamento_id}/cancelar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "6 horas" in body or "antecedência" in body.lower() or "não permitido" in body.lower()
        assert _get_slot_status(slot_id) == "AGENDADO"

    def test_slot_permanece_agendado_quando_cancelamento_bloqueado(
        self, client, make_user, make_monitoria_ativa
    ):
        """C2: Quando bloqueado por < 6h, o slot NÃO volta a DISPONIVEL."""
        setup = make_monitoria_ativa("us14c2b")
        aluno_id = make_user("Aluno US14c2b", "aluno.us14c2b@teste.com", "ALUNO")
        data_inicio = datetime.datetime.now() + datetime.timedelta(hours=2)
        slot_id, agendamento_id = _create_slot_with_booking(
            setup["disc_id"], setup["aluno_id"], aluno_id, data_inicio
        )

        client.post("/auth/login", data={"email": "aluno.us14c2b@teste.com", "senha": "Senha@Teste1"})
        client.post(f"/agenda/agendamentos/{agendamento_id}/cancelar", follow_redirects=True)
        assert _get_slot_status(slot_id) == "AGENDADO"
        assert _get_agendamento_status(agendamento_id) == "CONFIRMADO"

    # -----------------------------------------------------------------------
    # C3 — Aluno não cancela agendamento de outro aluno
    # -----------------------------------------------------------------------

    def test_aluno_nao_cancela_agendamento_alheio(self, client, make_user, make_monitoria_ativa):
        """C3: Aluno B não consegue cancelar agendamento do aluno A."""
        setup = make_monitoria_ativa("us14c3")
        aluno_a = make_user("Aluno A US14", "alunoA.us14@teste.com", "ALUNO")
        aluno_b = make_user("Aluno B US14", "alunoB.us14@teste.com", "ALUNO")
        data_inicio = datetime.datetime.now() + datetime.timedelta(hours=8)
        slot_id, agendamento_id = _create_slot_with_booking(
            setup["disc_id"], setup["aluno_id"], aluno_a, data_inicio
        )

        client.post("/auth/login", data={"email": "alunoB.us14@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/agenda/agendamentos/{agendamento_id}/cancelar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()
        assert _get_slot_status(slot_id) == "AGENDADO"

    # -----------------------------------------------------------------------
    # C4 — Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C4: Sem sessão ativa → redireciona para login."""
        response = client.post("/agenda/agendamentos/1/cancelar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
