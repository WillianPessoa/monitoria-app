"""
US21 — Aluno recebe confirmação ao agendar horário
US22 — Lembrete visual para atendimentos nas próximas 24 horas

US21 Critérios de aceitação:
  C1  Flash message após booking inclui data, hora e nome do monitor
  C2  Agendamento aparece listado em "Horários agendados" com dados completos

US22 Critérios de aceitação:
  C1  Badge "Hoje/Amanhã" exibido quando agendamento está nas próximas 24h
  C2  Badge "Hoje/Amanhã" não exibido para agendamentos além de 24h
"""

import datetime

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future(hours=24):
    return datetime.datetime.now() + datetime.timedelta(hours=hours)


def _create_slot_db(monitor_id, disc_id, data_inicio, duracao_min, local=None):
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disponibilidades
            (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
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
    """Cria agendamento diretamente no banco sem passar pela rota."""
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


# ---------------------------------------------------------------------------
# US21 — Confirmação ao agendar
# ---------------------------------------------------------------------------


class TestUS21Confirmacao:

    def test_flash_contem_nome_do_monitor(self, client, make_user, make_monitoria_ativa):
        """C1: Flash message após booking inclui nome do monitor."""
        setup = make_monitoria_ativa("us21c1")
        make_user("Aluno US21a", "aluno.us21c1@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60)

        client.post("/auth/login", data={"email": "aluno.us21c1@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/agenda/slots/{slot_id}/book", follow_redirects=True
        )

        body = response.get_data(as_text=True)
        assert "Monitor us21c1" in body
        assert "confirmado" in body.lower()

    def test_flash_contem_hora_formatada(self, client, make_user, make_monitoria_ativa):
        """C1: Flash message após booking inclui o horário no formato HH:MM."""
        setup = make_monitoria_ativa("us21c2")
        make_user("Aluno US21b", "aluno.us21c2@teste.com", "ALUNO")
        data_inicio = _future(24).replace(second=0, microsecond=0)
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], data_inicio, 60)

        client.post("/auth/login", data={"email": "aluno.us21c2@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/agenda/slots/{slot_id}/book", follow_redirects=True
        )

        body = response.get_data(as_text=True)
        hora_str = data_inicio.strftime("%H:%M")
        assert hora_str in body

    def test_agendamento_aparece_listado_na_agenda(self, client, make_user, make_monitoria_ativa):
        """C2: Após booking, agendamento aparece em 'Horários agendados' com monitor e local."""
        setup = make_monitoria_ativa("us21c3")
        aluno_id = make_user("Aluno US21c", "aluno.us21c3@teste.com", "ALUNO")
        slot_id = _create_slot_db(
            setup["aluno_id"], setup["disc_id"], _future(48), 60, local="Sala 101"
        )
        _book_slot_direct(slot_id, aluno_id)

        client.post("/auth/login", data={"email": "aluno.us21c3@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Monitor us21c3" in body
        assert "Sala 101" in body
        assert "Horários agendados" in body

    def test_agendamento_aparece_com_hora_na_agenda(self, client, make_user, make_monitoria_ativa):
        """C2: Agendamento listado exibe o horário correto."""
        setup = make_monitoria_ativa("us21c4")
        aluno_id = make_user("Aluno US21d", "aluno.us21c4@teste.com", "ALUNO")
        data_inicio = _future(36).replace(second=0, microsecond=0)
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], data_inicio, 60)
        _book_slot_direct(slot_id, aluno_id)

        client.post("/auth/login", data={"email": "aluno.us21c4@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        hora_str = data_inicio.strftime("%H:%M")
        assert hora_str in body


# ---------------------------------------------------------------------------
# US22 — Lembrete visual (badge Hoje/Amanhã)
# ---------------------------------------------------------------------------


class TestUS22Lembrete:

    def test_badge_exibido_para_agendamento_nas_proximas_24h(
        self, client, make_user, make_monitoria_ativa
    ):
        """C1: Agendamento dentro de 24h → badge 'Hoje/Amanhã' visível."""
        setup = make_monitoria_ativa("us22c1")
        aluno_id = make_user("Aluno US22a", "aluno.us22c1@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(12), 60)
        _book_slot_direct(slot_id, aluno_id)

        client.post("/auth/login", data={"email": "aluno.us22c1@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Hoje/Amanhã" in body

    def test_badge_nao_exibido_para_agendamento_alem_de_24h(
        self, client, make_user, make_monitoria_ativa
    ):
        """C2: Agendamento além de 24h → badge 'Hoje/Amanhã' não aparece."""
        setup = make_monitoria_ativa("us22c2")
        aluno_id = make_user("Aluno US22b", "aluno.us22c2@teste.com", "ALUNO")
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(48), 60)
        _book_slot_direct(slot_id, aluno_id)

        client.post("/auth/login", data={"email": "aluno.us22c2@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Hoje/Amanhã" not in body

    def test_sem_agendamentos_proximos_sem_badge(self, aluno_client):
        """C2: Aluno sem agendamentos nas próximas 24h → sem badge."""
        response = aluno_client.get("/agenda/")
        body = response.get_data(as_text=True)
        assert "Hoje/Amanhã" not in body
