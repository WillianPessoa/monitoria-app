"""
US15 — Monitor bloqueia um horário da agenda

Rotas:
  POST /agenda/slots/<int:slot_id>/bloquear
  POST /agenda/slots/<int:slot_id>/desbloquear

Critérios de aceitação (inferidos do código):

  C1  Bloquear slot disponível → status BLOQUEADO
  C2  Desbloquear slot bloqueado → status DISPONIVEL
  C3  Não é possível bloquear slot já agendado
  C4  Não é possível bloquear slot de outro monitor
  C5  Não autenticado → redireciona
"""

import datetime

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_slot_db(disc_id, monitor_id, status="DISPONIVEL"):
    now = datetime.datetime.now()
    data_inicio = now + datetime.timedelta(hours=8)
    data_fim    = data_inicio + datetime.timedelta(hours=2)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (disc_id, monitor_id, data_inicio, data_fim, status),
    )
    conn.commit()
    slot_id = cur.lastrowid
    cur.close()
    conn.close()
    return slot_id


def _get_slot_status(slot_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM disponibilidades WHERE id = %s", (slot_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS15BloquearSlot:

    # -----------------------------------------------------------------------
    # C1 — Bloquear slot disponível
    # -----------------------------------------------------------------------

    def test_bloquear_slot_disponivel_retorna_flash_sucesso(self, client, make_monitoria_ativa):
        """C1: Monitor bloqueia slot DISPONIVEL → flash de sucesso."""
        setup = make_monitoria_ativa("us15c1")
        slot_id = _create_slot_db(setup["disc_id"], setup["aluno_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(f"/agenda/slots/{slot_id}/bloquear", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "bloqueado" in body.lower()

    def test_bloquear_slot_muda_status_para_bloqueado(self, client, make_monitoria_ativa):
        """C1: Após bloqueio, status muda para BLOQUEADO no banco."""
        setup = make_monitoria_ativa("us15c1b")
        slot_id = _create_slot_db(setup["disc_id"], setup["aluno_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(f"/agenda/slots/{slot_id}/bloquear", follow_redirects=True)

        assert _get_slot_status(slot_id) == "BLOQUEADO"

    # -----------------------------------------------------------------------
    # C2 — Desbloquear slot bloqueado
    # -----------------------------------------------------------------------

    def test_desbloquear_slot_bloqueado_retorna_flash_sucesso(self, client, make_monitoria_ativa):
        """C2: Monitor desbloqueia slot BLOQUEADO → flash de sucesso."""
        setup = make_monitoria_ativa("us15c2")
        slot_id = _create_slot_db(setup["disc_id"], setup["aluno_id"], status="BLOQUEADO")

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(f"/agenda/slots/{slot_id}/desbloquear", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "desbloqueado" in body.lower()

    def test_desbloquear_muda_status_para_disponivel(self, client, make_monitoria_ativa):
        """C2: Após desbloqueio, status volta a DISPONIVEL."""
        setup = make_monitoria_ativa("us15c2b")
        slot_id = _create_slot_db(setup["disc_id"], setup["aluno_id"], status="BLOQUEADO")

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(f"/agenda/slots/{slot_id}/desbloquear", follow_redirects=True)

        assert _get_slot_status(slot_id) == "DISPONIVEL"

    # -----------------------------------------------------------------------
    # C3 — Não pode bloquear slot AGENDADO
    # -----------------------------------------------------------------------

    def test_bloquear_slot_agendado_rejeitado(self, client, make_monitoria_ativa):
        """C3: Slot já AGENDADO não pode ser bloqueado."""
        setup = make_monitoria_ativa("us15c3")
        slot_id = _create_slot_db(setup["disc_id"], setup["aluno_id"], status="AGENDADO")

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(f"/agenda/slots/{slot_id}/bloquear", follow_redirects=True)

        body = response.get_data(as_text=True)
        assert "disponíveis" in body.lower() or "indisponível" in body.lower() or "agendamento" in body.lower()
        assert _get_slot_status(slot_id) == "AGENDADO"

    # -----------------------------------------------------------------------
    # C4 — Monitor alheio não pode bloquear
    # -----------------------------------------------------------------------

    def test_outro_monitor_nao_pode_bloquear_slot(self, client, make_monitoria_ativa):
        """C4: Monitor B não pode bloquear slot pertencente ao monitor A."""
        setup_a = make_monitoria_ativa("us15c4a")
        setup_b = make_monitoria_ativa("us15c4b")
        slot_id = _create_slot_db(setup_a["disc_id"], setup_a["aluno_id"])

        client.post("/auth/login", data={"email": setup_b["monitor_email"], "senha": setup_b["monitor_senha"]})
        client.post(f"/agenda/slots/{slot_id}/bloquear", follow_redirects=True)

        assert _get_slot_status(slot_id) == "DISPONIVEL"

    # -----------------------------------------------------------------------
    # C5 — Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_bloquear(self, client):
        """C5: Sem sessão → redireciona para login."""
        response = client.post("/agenda/slots/1/bloquear", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location

    def test_nao_autenticado_redireciona_desbloquear(self, client):
        """C5: Sem sessão → redireciona para login."""
        response = client.post("/agenda/slots/1/desbloquear", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
