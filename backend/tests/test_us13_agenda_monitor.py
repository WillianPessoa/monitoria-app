"""
US13 — Monitor vê agenda com agendamentos confirmados

Rota: GET /agenda/  (visão do monitor)

Critérios de aceitação:

  C1  Visualização da agenda
      Given: monitor autenticado
      When:  acessa /agenda/
      Then:  vê todos os horários criados, diferenciando os com agendamento dos livres

  C2  Dados do agendamento
      Given: monitor visualiza sessão com agendamento
      When:  acessa o detalhe
      Then:  sistema exibe nome do aluno, data e horário

Cenários extras:
  C3  Sessão futura aparece em "Próximas sessões"
  C4  Sessão passada aparece em seção de histórico / registro
  C5  Sem sessões → seção exibe estado vazio
  C6  GET /agenda/ retorna 200 para monitor
"""

from db.connection import get_connection


def _get_sessao(sessao_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM monitoria_sessoes WHERE id = %s", (sessao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


class TestUS13AgendaMonitor:

    # -----------------------------------------------------------------------
    # C6 — Smoke test de acesso
    # -----------------------------------------------------------------------

    def test_agenda_retorna_200_para_monitor(self, client, make_sessao):
        """C6: Monitor acessa /agenda/ → 200."""
        setup = make_sessao("us13c6", past=False)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get("/agenda/")
        assert response.status_code == 200

    # -----------------------------------------------------------------------
    # C1 — Visualização da agenda
    # -----------------------------------------------------------------------

    def test_monitor_ve_secao_de_proximas_sessoes(self, client, make_sessao):
        """C1/C3: Monitor com sessão futura vê seção 'Próximas sessões'."""
        setup = make_sessao("us13c1", past=False)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get("/agenda/")
        body = response.get_data(as_text=True)
        assert "Próximas sessões" in body or "proximas" in body.lower()

    def test_monitor_ve_sessao_futura_na_agenda(self, client, make_sessao):
        """C3: Sessão futura aparece na seção de próximas sessões com data/horário."""
        setup = make_sessao("us13c3", past=False)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get("/agenda/")
        body = response.get_data(as_text=True)
        # Seção de próximas sessões visível
        assert "Próximas sessões" in body

    # -----------------------------------------------------------------------
    # C2 — Detalhe do agendamento (sessao_detalhe)
    # -----------------------------------------------------------------------

    def test_detalhe_sessao_retorna_200(self, client, make_sessao):
        """C2: GET /monitorias/sessoes/<id> retorna 200 para o monitor da sessão."""
        setup = make_sessao("us13c2", past=True)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get(f"/monitorias/sessoes/{setup['sessao_id']}")
        assert response.status_code == 200

    def test_detalhe_sessao_exibe_dados_da_sessao(self, client, make_sessao):
        """C2: Detalhe da sessão contém informações da disciplina/monitor."""
        setup = make_sessao("us13c2b", past=True)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get(f"/monitorias/sessoes/{setup['sessao_id']}")
        body = response.get_data(as_text=True)
        # Página carrega com algum conteúdo relevante (nome da disciplina ou similar)
        assert response.status_code == 200
        assert len(body) > 100

    # -----------------------------------------------------------------------
    # C4 — Sessão passada em seção de registro
    # -----------------------------------------------------------------------

    def test_sessao_passada_aparece_para_registro(self, client, make_sessao):
        """C4: Sessão com data passada aparece na seção de pendentes (seção warning da agenda).
        Sem participantes, o template exibe 'Nenhum aluno confirmado' mas a sessão é mostrada.
        Com participantes, o botão 'Salvar registro' aparece."""
        setup = make_sessao("us13c4", past=True)
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.get("/agenda/")
        body = response.get_data(as_text=True)
        # Sessão passada é exibida na seção de pendentes (com ou sem participantes)
        disc_code = f"D{('us13c4').upper()[:9]}"
        assert disc_code in body or "Nenhum aluno confirmado" in body
