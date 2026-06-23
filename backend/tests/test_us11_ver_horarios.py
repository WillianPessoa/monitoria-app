"""
US11 — Aluno vê horários disponíveis de um monitor

Rota: GET /agenda/  (seção de horários disponíveis na visão do aluno)

Pré-condição para um slot aparecer:
  - Aluno matriculado na disciplina (disciplina_alunos)
  - Disciplina tem monitoria ATIVA (monitorias.status = 'ATIVO')
  - Disponibilidade com status = 'DISPONIVEL' e data_inicio > NOW()
  - Disciplina com status = 'ATIVA'

Critérios de aceitação:

  C1  Busca por disciplina
      Given: aluno matriculado em disciplina com monitor ativo e slot futuro
      When:  acessa /agenda/
      Then:  vê o slot com nome do monitor, data, horário e local

  C2  Horário lotado não aparece
      Given: slot com agendamento CONFIRMADO (status AGENDADO)
      When:  aluno busca horários disponíveis
      Then:  esse slot não aparece na listagem

  C3  Horário passado não aparece
      Given: slot com data_inicio no passado
      When:  aluno busca horários disponíveis
      Then:  esse slot não aparece na listagem

Cenários extras:
  C4  Aluno não matriculado em nenhuma disciplina → lista vazia
  C5  Disciplina inativa → slots não aparecem
  C6  GET /agenda/ retorna 200 para aluno autenticado
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


def _create_slot_db(monitor_id, disc_id, data_inicio, duracao_min, local="Sala Teste"):
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


def _enroll_aluno(disc_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT IGNORE INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
        (disc_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def _book_slot_direct(slot_id, aluno_id):
    """Marca slot como AGENDADO e cria agendamento no banco (sem passar pela rota)."""
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


def _set_disciplina_inativa(disc_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE disciplinas SET status = 'INATIVA' WHERE id = %s", (disc_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS11VerHorariosDisponiveis:

    # -----------------------------------------------------------------------
    # C6 — Acesso básico (smoke)
    # -----------------------------------------------------------------------

    def test_agenda_retorna_200_para_aluno(self, aluno_client):
        """C6: GET /agenda/ retorna 200 para aluno autenticado."""
        response = aluno_client.get("/agenda/")
        assert response.status_code == 200

    # -----------------------------------------------------------------------
    # C1 — Aluno matriculado vê o slot
    # -----------------------------------------------------------------------

    def test_aluno_matriculado_ve_slot_disponivel(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno matriculado na disciplina vê slot futuro do monitor (com local)."""
        setup = make_monitoria_ativa("us11c1")
        aluno_id = make_user("Aluno US11", "aluno.us11c1@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60, "Sala Espelho")

        client.post("/auth/login", data={"email": "aluno.us11c1@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "slot-card" in body
        assert "Sala Espelho" in body  # local agora exibido no template (BUG-04 corrigido)

    def test_slot_exibe_nome_do_monitor(self, client, make_user, make_monitoria_ativa):
        """C1: O slot exibido contém o nome do monitor."""
        setup = make_monitoria_ativa("us11c1b")
        aluno_id = make_user("Aluno C1b", "aluno.us11c1b@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60, "Sala A")

        client.post("/auth/login", data={"email": "aluno.us11c1b@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Monitor us11c1b" in body

    # -----------------------------------------------------------------------
    # C2 — Slot lotado não aparece
    # -----------------------------------------------------------------------

    def test_slot_agendado_nao_aparece_na_listagem(self, client, make_user, make_monitoria_ativa):
        """C2: Slot com status AGENDADO não aparece para o aluno como disponível."""
        setup = make_monitoria_ativa("us11c2")
        aluno_id = make_user("Aluno C2", "aluno.us11c2@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        slot_id = _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60)
        _book_slot_direct(slot_id, aluno_id)

        client.post("/auth/login", data={"email": "aluno.us11c2@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        # Único slot da disciplina foi agendado: seção de disponíveis fica vazia
        assert "slot-card" not in body or "Nenhum horário" in body

    # -----------------------------------------------------------------------
    # C3 — Slot passado não aparece
    # -----------------------------------------------------------------------

    def test_slot_passado_nao_aparece_na_listagem(self, client, make_user, make_monitoria_ativa):
        """C3: Slot com data_inicio no passado não aparece na listagem."""
        setup = make_monitoria_ativa("us11c3")
        aluno_id = make_user("Aluno C3", "aluno.us11c3@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], _past(2), 60, "Sala Passada")

        client.post("/auth/login", data={"email": "aluno.us11c3@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Sala Passada" not in body

    # -----------------------------------------------------------------------
    # C4 — Aluno não matriculado em nenhuma disciplina
    # -----------------------------------------------------------------------

    def test_aluno_nao_matriculado_nao_ve_slots(self, client, make_user, make_monitoria_ativa):
        """C4: Aluno sem matrícula em disciplinas nenhuma vê lista vazia."""
        setup = make_monitoria_ativa("us11c4")
        aluno_sem_matricula = make_user("Aluno Sem Matricula", "aluno.us11c4@teste.com", "ALUNO")
        _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60, "Sala Invisivel")

        client.post("/auth/login", data={"email": "aluno.us11c4@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Sala Invisivel" not in body
        assert "nenhum horário" in body.lower() or "nenhum" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Disciplina inativa
    # -----------------------------------------------------------------------

    def test_slot_de_disciplina_inativa_nao_aparece(self, client, make_user, make_monitoria_ativa):
        """C5: Slots de disciplina INATIVA não aparecem para o aluno."""
        setup = make_monitoria_ativa("us11c5")
        aluno_id = make_user("Aluno C5", "aluno.us11c5@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], _future(24), 60, "Sala Inativa")
        _set_disciplina_inativa(setup["disc_id"])

        client.post("/auth/login", data={"email": "aluno.us11c5@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/agenda/")

        body = response.get_data(as_text=True)
        assert "Sala Inativa" not in body
