"""
US16 — Monitor registra presença ou ausência do aluno
US17 — Monitor registra o assunto tratado no atendimento

Rota: POST /monitorias/sessoes/<int:sessao_id>/registrar
Form: presentes[] (lista de aluno_ids presentes), assunto (texto)

Ambas US usam o mesmo endpoint. O mesmo POST registra:
  - Presença (CONFIRMADA/AUSENTE) para cada participante da sessão
  - Assunto tratado
  - Status da sessão → CONCLUIDA

Critérios de aceitação:

US16:
  C1  Registro de presença
      Given: horário passado, monitor registra aluno como "presente"
      Then:  registro salvo, contabilizado em horas do monitor

  C2  Registro de ausência
      Given: monitor registra aluno como "ausente"
      Then:  registro salvo, mas não contabilizado em horas

  C3  Registro antes do horário
      Given: sessão ainda no futuro
      When:  monitor tenta registrar
      Then:  sistema rejeita com mensagem

US17:
  C1  Assunto registrado junto à sessão
      When:  monitor submete assunto e presenças
      Then:  assunto salvo na sessão, status → CONCLUIDA

Cenários extras:
  C4  Assunto em branco → rejeitado
  C5  Monitor alheio não pode registrar
  C6  Não autenticado → redireciona
"""

from db.connection import get_connection


def _get_sessao(sessao_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status, assunto FROM monitoria_sessoes WHERE id = %s", (sessao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def _get_presenca(sessao_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT status FROM presencas WHERE sessao_id = %s AND aluno_id = %s",
        (sessao_id, aluno_id),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def _monitor_hours(monitor_id):
    from monitorias import service as monitoria_service
    return monitoria_service.get_monitor_hours_count(monitor_id)


class TestUS16US17RegistrarSessao:

    # -----------------------------------------------------------------------
    # C1 (US17) — Registro com assunto → CONCLUIDA
    # -----------------------------------------------------------------------

    def test_registrar_sessao_retorna_flash_sucesso(self, client, make_user, make_sessao):
        """C1/US17: Monitor registra sessão passada com assunto → flash de sucesso."""
        aluno_id = make_user("Aluno Reg", "aluno.reg@teste.com", "ALUNO")
        setup = make_sessao("us16c1", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [str(aluno_id)], "assunto": "Derivadas e integrais"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "salvo com sucesso" in body.lower() or "registro" in body.lower()

    def test_registrar_sessao_muda_status_para_concluida(self, client, make_user, make_sessao):
        """C1: Após registro, sessão vira CONCLUIDA no banco."""
        aluno_id = make_user("Aluno Conc", "aluno.conc@teste.com", "ALUNO")
        setup = make_sessao("us16c1b", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [str(aluno_id)], "assunto": "Matrizes"},
            follow_redirects=True,
        )
        assert _get_sessao(setup["sessao_id"])["status"] == "CONCLUIDA"

    def test_registrar_salva_assunto(self, client, make_user, make_sessao):
        """C1/US17: Assunto informado é persistido na sessão."""
        aluno_id = make_user("Aluno Ass", "aluno.ass@teste.com", "ALUNO")
        setup = make_sessao("us17c1", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [str(aluno_id)], "assunto": "Limites e continuidade"},
            follow_redirects=True,
        )
        sessao = _get_sessao(setup["sessao_id"])
        assert "Limites e continuidade" in (sessao["assunto"] or "")

    # -----------------------------------------------------------------------
    # C1 (US16) — Presença registrada
    # -----------------------------------------------------------------------

    def test_registrar_presenca_confirmada(self, client, make_user, make_sessao):
        """C1/US16: Aluno marcado como presente → status CONFIRMADA na tabela presencas."""
        aluno_id = make_user("Aluno Pres", "aluno.pres@teste.com", "ALUNO")
        setup = make_sessao("us16pres", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [str(aluno_id)], "assunto": "POO"},
            follow_redirects=True,
        )
        presenca = _get_presenca(setup["sessao_id"], aluno_id)
        assert presenca is not None
        assert presenca["status"] == "CONFIRMADA"

    # -----------------------------------------------------------------------
    # C2 (US16) — Ausência registrada
    # -----------------------------------------------------------------------

    def test_registrar_presenca_ausente(self, client, make_user, make_sessao):
        """C2/US16: Aluno NÃO marcado em presentes → status AUSENTE."""
        aluno_id = make_user("Aluno Aus", "aluno.aus@teste.com", "ALUNO")
        setup = make_sessao("us16aus", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        # Não inclui aluno_id em presentes → ausente
        client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"assunto": "Grafos"},
            follow_redirects=True,
        )
        presenca = _get_presenca(setup["sessao_id"], aluno_id)
        assert presenca is not None
        assert presenca["status"] == "AUSENTE"

    # -----------------------------------------------------------------------
    # C3 (US16) — Registro antes do horário recusado
    # -----------------------------------------------------------------------

    def test_registrar_sessao_futura_rejeitado(self, client, make_sessao):
        """C3/US16: Tentar registrar sessão no futuro → flash de erro."""
        setup = make_sessao("us16c3", past=False)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [], "assunto": "Ainda não aconteceu"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "realizadas" in body.lower() or "ainda" in body.lower() or "futuro" in body.lower()
        assert _get_sessao(setup["sessao_id"])["status"] == "AGENDADA"

    # -----------------------------------------------------------------------
    # C4 — Assunto em branco rejeitado
    # -----------------------------------------------------------------------

    def test_registrar_sem_assunto_rejeitado(self, client, make_user, make_sessao):
        """C4: Registrar sem informar assunto → flash de erro, sessão permanece AGENDADA."""
        aluno_id = make_user("Aluno Vazio", "aluno.vazio@teste.com", "ALUNO")
        setup = make_sessao("us16c4", past=True, aluno_id=aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/sessoes/{setup['sessao_id']}/registrar",
            data={"presentes": [str(aluno_id)], "assunto": ""},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "assunto" in body.lower()
        assert _get_sessao(setup["sessao_id"])["status"] == "AGENDADA"

    # -----------------------------------------------------------------------
    # C5 — Monitor alheio não registra
    # -----------------------------------------------------------------------

    def test_outro_monitor_nao_pode_registrar(self, client, make_sessao, make_monitoria_ativa):
        """C5: Monitor B não pode registrar sessão pertencente ao monitor A."""
        setup_a = make_sessao("us16c5a", past=True)
        setup_b = make_monitoria_ativa("us16c5b")

        client.post("/auth/login", data={"email": setup_b["monitor_email"], "senha": setup_b["monitor_senha"]})
        response = client.post(
            f"/monitorias/sessoes/{setup_a['sessao_id']}/registrar",
            data={"presentes": [], "assunto": "Invasão"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()
        assert _get_sessao(setup_a["sessao_id"])["status"] == "AGENDADA"

    # -----------------------------------------------------------------------
    # C6 — Segurança
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C6: Sem sessão ativa → redireciona para login."""
        response = client.post("/monitorias/sessoes/1/registrar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
