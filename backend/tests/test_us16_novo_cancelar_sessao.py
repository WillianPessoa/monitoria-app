"""
US16-novo — Monitor cancela agendamento de sessão confirmada

Rota: POST /monitorias/sessoes/<int:sessao_id>/cancelar

Regras de negócio:
  - Somente o monitor dono da sessão pode cancelar
  - Cancelamento permitido apenas com mais de 6 horas de antecedência
  - Status da sessão vai para CANCELADA

Cenários de aceitação (extraídos do código):

  C1  Cancelamento bem-sucedido (> 6h de antecedência)
      Given: monitor com sessão futura (> 6h)
      When:  cancela a sessão
      Then:  status → CANCELADA, flash de sucesso

  C2  Cancelamento recusado (< 6h de antecedência)
      Given: sessão dentro das próximas 6 horas
      When:  monitor tenta cancelar
      Then:  flash de erro, status permanece AGENDADA

Cenários extras:
  C3  Monitor alheio não pode cancelar sessão de outro monitor
  C4  Sessão inexistente → flash de erro
  C5  Não autenticado → redireciona para login
"""

import datetime

from db.connection import get_connection


def _get_sessao_status(sessao_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM monitoria_sessoes WHERE id = %s", (sessao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


def _create_sessao_db(disc_id, monitor_id, data_inicio, data_fim):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, 'AGENDADA')
        """,
        (disc_id, monitor_id, data_inicio, data_fim),
    )
    conn.commit()
    sessao_id = cur.lastrowid
    cur.close()
    conn.close()
    return sessao_id


class TestUS16NovoCancelarSessao:

    # -----------------------------------------------------------------------
    # C1 — Cancelamento bem-sucedido (> 6h)
    # -----------------------------------------------------------------------

    def test_cancelar_sessao_futura_retorna_flash_sucesso(self, client, make_sessao):
        """C1: Monitor cancela sessão > 6h à frente → flash de sucesso."""
        setup = make_sessao("us16nc1", past=False)  # data_inicio = now + 8h
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/cancelar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "cancelada" in body.lower()

    def test_cancelar_sessao_muda_status_para_cancelada(self, client, make_sessao):
        """C1: Após cancelamento bem-sucedido, status vira CANCELADA no banco."""
        setup = make_sessao("us16nc1b", past=False)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(f"/monitorias/sessoes/{setup['sessao_id']}/cancelar", follow_redirects=True)
        assert _get_sessao_status(setup["sessao_id"]) == "CANCELADA"

    # -----------------------------------------------------------------------
    # C2 — Cancelamento < 6h recusado
    # -----------------------------------------------------------------------

    def test_cancelar_sessao_com_menos_de_6h_rejeitado(self, client, make_monitoria_ativa, make_user):
        """C2: Sessão em 3h não pode ser cancelada → flash de erro, status AGENDADA."""
        setup = make_monitoria_ativa("us16nc2")
        now = datetime.datetime.now()
        data_inicio = now + datetime.timedelta(hours=3)  # menos de 6h
        data_fim = data_inicio + datetime.timedelta(hours=2)
        sessao_id = _create_sessao_db(setup["disc_id"], setup["aluno_id"], data_inicio, data_fim)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/sessoes/{sessao_id}/cancelar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "6 horas" in body or "antecedência" in body.lower() or "não permitido" in body.lower()
        assert _get_sessao_status(sessao_id) == "AGENDADA"

    # -----------------------------------------------------------------------
    # C3 — Monitor alheio não pode cancelar
    # -----------------------------------------------------------------------

    def test_outro_monitor_nao_pode_cancelar_sessao(self, client, make_sessao, make_monitoria_ativa):
        """C3: Monitor diferente do dono não consegue cancelar a sessão."""
        setup = make_sessao("us16nc3a", past=False)          # sessão do monitor A
        setup_b = make_monitoria_ativa("us16nc3b")           # monitor B

        client.post("/auth/login", data={"email": setup_b["monitor_email"], "senha": setup_b["monitor_senha"]})
        response = client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/cancelar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower() or "não encontrada" in body.lower()
        assert _get_sessao_status(setup["sessao_id"]) == "AGENDADA"

    # -----------------------------------------------------------------------
    # C4 — Sessão inexistente
    # -----------------------------------------------------------------------

    def test_cancelar_sessao_inexistente_retorna_erro(self, client, make_monitoria_ativa):
        """C4: POST em sessao_id que não existe → flash de erro."""
        setup = make_monitoria_ativa("us16nc4")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post("/monitorias/sessoes/999999/cancelar", follow_redirects=True)
        body = response.get_data(as_text=True)
        assert "não encontrada" in body.lower() or "nao encontrada" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Segurança
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C5: Sem sessão ativa → redireciona para login."""
        response = client.post("/monitorias/sessoes/1/cancelar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
