"""
US12 — Aluno agenda um horário disponível

Rota: POST /agenda/slots/<int:slot_id>/book

Critérios de aceitação:

  C1  Agendamento bem-sucedido
      Given: aluno visualiza horário DISPONIVEL futuro
      When:  confirma o agendamento
      Then:  agendamento criado, slot vira AGENDADO, flash de sucesso

  C2  Conflito de horário do aluno
      Given: aluno já tem agendamento CONFIRMADO num período
      When:  tenta agendar outro atendimento no mesmo período
      Then:  sistema rejeita com mensagem de conflito

Cenários extras:
  C3  Slot inexistente → rejeitado
  C4  Slot já AGENDADO → rejeitado
  C5  Slot no passado → rejeitado
  C6  Não autenticado → redireciona para login
  C7  Booking cria registro em agendamentos
"""

import datetime

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future(hours=24):
    return datetime.datetime.now() + datetime.timedelta(hours=hours)


def _past(hours=1):
    return datetime.datetime.now() - datetime.timedelta(hours=hours)


def _create_slot_db(monitor_id, disc_id, data_inicio, duracao_min, local=None):
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
        VALUES (%s, %s, %s, %s, %s, 'DISPONIVEL')
        """,
        (disc_id, monitor_id, data_inicio, data_fim, local),
    )
    conn.commit()
    slot_id = cur.lastrowid
    cur.close()
    conn.close()
    return slot_id


def _book_slot_direct(slot_id, aluno_id):
    """Marca slot como AGENDADO e cria agendamento diretamente no banco."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE disponibilidades SET status = 'AGENDADO' WHERE id = %s",
        (slot_id,),
    )
    cur.execute(
        "INSERT INTO agendamentos (disponibilidade_id, aluno_id, status) VALUES (%s, %s, 'CONFIRMADO')",
        (slot_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def _get_slot_status(slot_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM disponibilidades WHERE id = %s", (slot_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


def _get_agendamento(slot_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM agendamentos WHERE disponibilidade_id = %s AND aluno_id = %s",
        (slot_id, aluno_id),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS12AgendarHorario:

    # -----------------------------------------------------------------------
    # C1 — Agendamento bem-sucedido
    # -----------------------------------------------------------------------

    def test_agendar_slot_retorna_flash_sucesso(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno agenda slot DISPONIVEL futuro → flash de sucesso."""
        setup = make_monitoria_ativa("us12c1")
        aluno_id = make_user("Aluno US12", "aluno.us12c1@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60)

        client.post("/auth/login", data={"email": "aluno.us12c1@teste.com", "senha": "Senha@Teste1"})
        response = client.post(f"/agenda/slots/{slot_id}/book", follow_redirects=True)

        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "agendado com sucesso" in body.lower()

    def test_agendar_slot_muda_status_para_agendado(self, client, make_user, make_monitoria_ativa):
        """C1: Após booking, disponibilidade muda para status AGENDADO no banco."""
        setup = make_monitoria_ativa("us12c1b")
        aluno_id = make_user("Aluno C1b", "aluno.us12c1b@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(48), 60)

        client.post("/auth/login", data={"email": "aluno.us12c1b@teste.com", "senha": "Senha@Teste1"})
        client.post(f"/agenda/slots/{slot_id}/book", follow_redirects=True)

        assert _get_slot_status(slot_id) == "AGENDADO"

    def test_agendar_slot_cria_agendamento_no_banco(self, client, make_user, make_monitoria_ativa):
        """C7: Booking cria registro em agendamentos com status CONFIRMADO."""
        setup = make_monitoria_ativa("us12c7")
        aluno_id = make_user("Aluno C7", "aluno.us12c7@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(72), 60)

        client.post("/auth/login", data={"email": "aluno.us12c7@teste.com", "senha": "Senha@Teste1"})
        client.post(f"/agenda/slots/{slot_id}/book", follow_redirects=True)

        agendamento = _get_agendamento(slot_id, aluno_id)
        assert agendamento is not None
        assert agendamento["status"] == "CONFIRMADO"

    # -----------------------------------------------------------------------
    # C2 — Conflito de horário
    # -----------------------------------------------------------------------

    def test_agendar_slot_com_conflito_rejeitado(self, client, make_user, make_monitoria_ativa):
        """C2: Aluno com agendamento às 14h–16h tenta agendar às 15h–17h → rejeitado."""
        base = (_future(24)).replace(hour=14, minute=0, second=0, microsecond=0)

        # Monitor A: slot 14h–16h, aluno já agendou
        setup_a = make_monitoria_ativa("us12c2a")
        aluno_id = make_user("Aluno Conflito", "aluno.us12c2@teste.com", "ALUNO")
        slot_a = _create_slot_db(setup_a["aluno_id"], setup_a["disc_id"], base, 120)
        _book_slot_direct(slot_a, aluno_id)

        # Monitor B: slot 15h–17h (sobrepõe com slot A)
        setup_b = make_monitoria_ativa("us12c2b")
        slot_b = _create_slot_db(setup_b["aluno_id"], setup_b["disc_id"], base.replace(hour=15), 120)

        client.post("/auth/login", data={"email": "aluno.us12c2@teste.com", "senha": "Senha@Teste1"})
        response = client.post(f"/agenda/slots/{slot_b}/book", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "conflito" in body.lower() or "período" in body.lower() or "agendamento" in body.lower()

    def test_agendar_com_conflito_nao_altera_banco(self, client, make_user, make_monitoria_ativa):
        """C2: Quando há conflito, o banco não cria novo agendamento."""
        base = (_future(24)).replace(hour=10, minute=0, second=0, microsecond=0)

        setup_a = make_monitoria_ativa("us12c2c")
        aluno_id = make_user("Aluno Conflito2", "aluno.us12c2c@teste.com", "ALUNO")
        slot_a = _create_slot_db(setup_a["aluno_id"], setup_a["disc_id"], base, 120)
        _book_slot_direct(slot_a, aluno_id)

        setup_b = make_monitoria_ativa("us12c2d")
        slot_b = _create_slot_db(setup_b["aluno_id"], setup_b["disc_id"], base.replace(hour=11), 120)

        client.post("/auth/login", data={"email": "aluno.us12c2c@teste.com", "senha": "Senha@Teste1"})
        client.post(f"/agenda/slots/{slot_b}/book", follow_redirects=True)

        assert _get_agendamento(slot_b, aluno_id) is None
        assert _get_slot_status(slot_b) == "DISPONIVEL"

    # -----------------------------------------------------------------------
    # C3 — Slot inexistente
    # -----------------------------------------------------------------------

    def test_agendar_slot_inexistente_rejeitado(self, aluno_client):
        """C3: POST em slot_id que não existe → flash de indisponível."""
        response = aluno_client.post("/agenda/slots/999999/book", follow_redirects=True)
        body = response.get_data(as_text=True)
        assert "indisponível" in body.lower() or "indisponivel" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Slot já AGENDADO
    # -----------------------------------------------------------------------

    def test_agendar_slot_ja_agendado_rejeitado(self, client, make_user, make_monitoria_ativa):
        """C4: Slot com status AGENDADO não pode ser reservado novamente."""
        setup = make_monitoria_ativa("us12c4")
        aluno_id = make_user("Aluno C4", "aluno.us12c4@teste.com", "ALUNO")
        outro_aluno = make_user("Outro Aluno", "outro.us12c4@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60)
        _book_slot_direct(slot_id, outro_aluno)

        client.post("/auth/login", data={"email": "aluno.us12c4@teste.com", "senha": "Senha@Teste1"})
        response = client.post(f"/agenda/slots/{slot_id}/book", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "indisponível" in body.lower() or "indisponivel" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Slot no passado
    # -----------------------------------------------------------------------

    def test_agendar_slot_no_passado_rejeitado(self, client, make_user, make_monitoria_ativa):
        """C5: Slot com data_inicio no passado não pode ser agendado."""
        setup = make_monitoria_ativa("us12c5")
        aluno_id = make_user("Aluno C5", "aluno.us12c5@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _past(2), 60)

        client.post("/auth/login", data={"email": "aluno.us12c5@teste.com", "senha": "Senha@Teste1"})
        response = client.post(f"/agenda/slots/{slot_id}/book", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "passado" in body.lower() or "indisponível" in body.lower() or "não é possível" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C6: Sem sessão ativa → redireciona para login."""
        response = client.post("/agenda/slots/1/book", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
