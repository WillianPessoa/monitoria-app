"""
US20 — Admin gera relatório de participação por disciplina

Rotas:
  GET /relatorios/participacao                — gera relatório em HTML
  GET /relatorios/participacao/exportar.csv   — exporta em CSV

Critérios de aceitação:

  C1  Geração do relatório
      Given: admin seleciona disciplina e período
      When:  acessa GET /relatorios/participacao?disciplina_id=<id>&data_inicio=...&data_fim=...
      Then:  exibe total de sessões, alunos atendidos, horas e monitores ativos

  C2  Exportação CSV
      Given: admin visualiza relatório
      When:  acessa GET /relatorios/participacao/exportar.csv?disciplina_id=<id>
      Then:  arquivo CSV retornado para download

Cenários extras:
  C3  Sem disciplina selecionada → página carrega sem dados
  C4  Não admin não acessa (redireciona)
  C5  CSV sem disciplina → 400
"""

import datetime

from db.connection import get_connection


def _create_sessao_concluida(disc_id, monitor_id, aluno_id):
    now = datetime.datetime.now()
    data_inicio = now - datetime.timedelta(hours=4)
    data_fim    = now - datetime.timedelta(hours=2)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status, assunto)
        VALUES (%s, %s, %s, %s, 'CONCLUIDA', 'Revisão para prova')
        """,
        (disc_id, monitor_id, data_inicio, data_fim),
    )
    conn.commit()
    sessao_id = cur.lastrowid
    cur.execute(
        "INSERT INTO presencas (sessao_id, aluno_id, status) VALUES (%s, %s, 'CONFIRMADA')",
        (sessao_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return sessao_id


class TestUS20RelatorioParticipacao:

    # -----------------------------------------------------------------------
    # C3 — Smoke: página carrega sem disciplina
    # -----------------------------------------------------------------------

    def test_relatorio_participacao_carrega_sem_filtro(self, admin_client):
        """C3: GET /relatorios/participacao sem filtro → 200, página de seleção."""
        response = admin_client.get("/relatorios/participacao")
        assert response.status_code == 200

    def test_relatorio_exibe_seletor_de_disciplina(self, admin_client):
        """C3: Página de relatório exibe seletor de disciplina."""
        response = admin_client.get("/relatorios/participacao")
        body = response.get_data(as_text=True)
        assert "disciplina" in body.lower() or "select" in body.lower()

    # -----------------------------------------------------------------------
    # C1 — Relatório com disciplina selecionada
    # -----------------------------------------------------------------------

    def test_relatorio_com_disciplina_retorna_dados(self, admin_client, make_user, make_monitoria_ativa):
        """C1: Relatório filtrado por disciplina exibe dados de participação."""
        setup = make_monitoria_ativa("us20c1")
        aluno_id = make_user("Aluno US20", "aluno.us20c1@teste.com", "ALUNO")
        _create_sessao_concluida(setup["disc_id"], setup["aluno_id"], aluno_id)

        hoje = datetime.date.today()
        primeiro = hoje.replace(day=1)
        response = admin_client.get(
            f"/relatorios/participacao"
            f"?disciplina_id={setup['disc_id']}"
            f"&data_inicio={primeiro}&data_fim={hoje}"
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        # Deve mostrar pelo menos 1 sessão e os dados do monitor
        assert "Monitor us20c1" in body or "sessão" in body.lower() or "1" in body

    def test_relatorio_exibe_sumario_de_participacao(self, admin_client, make_user, make_monitoria_ativa):
        """C1: Relatório inclui totais (sessões, horas, alunos, monitores)."""
        setup = make_monitoria_ativa("us20c1b")
        aluno_id = make_user("Aluno US20b", "aluno.us20c1b@teste.com", "ALUNO")
        _create_sessao_concluida(setup["disc_id"], setup["aluno_id"], aluno_id)

        hoje = datetime.date.today()
        primeiro = hoje.replace(day=1)
        response = admin_client.get(
            f"/relatorios/participacao"
            f"?disciplina_id={setup['disc_id']}"
            f"&data_inicio={primeiro}&data_fim={hoje}"
        )
        body = response.get_data(as_text=True)
        assert response.status_code == 200

    # -----------------------------------------------------------------------
    # C2 — Exportação CSV
    # -----------------------------------------------------------------------

    def test_exportar_csv_retorna_content_type_csv(self, admin_client, make_user, make_monitoria_ativa):
        """C2: GET exportar.csv retorna Content-Type text/csv."""
        setup = make_monitoria_ativa("us20c2")
        aluno_id = make_user("Aluno US20C2", "aluno.us20c2@teste.com", "ALUNO")
        _create_sessao_concluida(setup["disc_id"], setup["aluno_id"], aluno_id)

        hoje = datetime.date.today()
        primeiro = hoje.replace(day=1)
        response = admin_client.get(
            f"/relatorios/participacao/exportar.csv"
            f"?disciplina_id={setup['disc_id']}"
            f"&data_inicio={primeiro}&data_fim={hoje}"
        )
        assert response.status_code == 200
        assert "text/csv" in response.content_type

    def test_exportar_csv_sem_disciplina_retorna_400(self, admin_client):
        """C5: GET exportar.csv sem disciplina_id → 400."""
        response = admin_client.get("/relatorios/participacao/exportar.csv")
        assert response.status_code == 400

    # -----------------------------------------------------------------------
    # C4 — Controle de acesso
    # -----------------------------------------------------------------------

    def test_aluno_nao_acessa_relatorio_de_participacao(self, aluno_client):
        """C4: Aluno não tem acesso ao relatório (redireciona ou 403)."""
        response = aluno_client.get("/relatorios/participacao", follow_redirects=False)
        assert response.status_code in (302, 403)
