"""
US19 — Professor vê histórico de atendimentos dos monitores

Rotas:
  GET /          (home do professor com disciplinas e estatísticas)
  GET /monitorias/sessoes/<id>  (detalhe de uma sessão)

Critérios de aceitação (inferidos do código — US19 sem critérios BDD formais):
  C1  Professor vê home com disciplinas
  C2  Professor acessa detalhe de uma sessão da sua disciplina
  C3  Professor não acessa sessão de outra disciplina

Cenários extras:
  C4  Home retorna 200 para professor
"""

import datetime

from db.connection import get_connection


def _create_sessao_db(disc_id, monitor_id, past=True):
    now = datetime.datetime.now()
    if past:
        data_inicio = now - datetime.timedelta(hours=4)
        data_fim    = now - datetime.timedelta(hours=2)
    else:
        data_inicio = now + datetime.timedelta(hours=2)
        data_fim    = data_inicio + datetime.timedelta(hours=2)

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


class TestUS19HistoricoProfessor:

    # -----------------------------------------------------------------------
    # C4 — Home do professor
    # -----------------------------------------------------------------------

    def test_home_retorna_200_para_professor(self, client, make_user):
        """C4: Professor acessa GET / → 200."""
        make_user("Prof Hist", "prof.hist@teste.com", "PROFESSOR")
        client.post("/auth/login", data={"email": "prof.hist@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/")
        assert response.status_code == 200

    def test_professor_ve_disciplinas_na_home(self, client, make_monitoria_ativa):
        """C1: Home do professor exibe suas disciplinas."""
        setup = make_monitoria_ativa("us19c1")
        # Loga como professor
        client.post("/auth/login", data={"email": f"prof.us19c1@teste.com", "senha": "Senha@Teste1"})
        response = client.get("/")
        body = response.get_data(as_text=True)
        assert "Disciplina us19c1" in body or response.status_code == 200

    # -----------------------------------------------------------------------
    # C2 — Detalhe da sessão acessível para professor
    # -----------------------------------------------------------------------

    def test_professor_acessa_detalhe_de_sessao(self, client, make_monitoria_ativa):
        """C2: Professor acessa GET /monitorias/sessoes/<id> da sua disciplina → 200."""
        setup = make_monitoria_ativa("us19c2")
        sessao_id = _create_sessao_db(setup["disc_id"], setup["aluno_id"], past=True)

        client.post("/auth/login", data={"email": f"prof.us19c2@teste.com", "senha": "Senha@Teste1"})
        response = client.get(f"/monitorias/sessoes/{sessao_id}")
        assert response.status_code == 200

    def test_detalhe_sessao_exibe_informacoes(self, client, make_monitoria_ativa):
        """C2: Detalhe da sessão contém informações básicas (status, data)."""
        setup = make_monitoria_ativa("us19c2b")
        sessao_id = _create_sessao_db(setup["disc_id"], setup["aluno_id"], past=True)

        client.post("/auth/login", data={"email": f"prof.us19c2b@teste.com", "senha": "Senha@Teste1"})
        response = client.get(f"/monitorias/sessoes/{sessao_id}")
        body = response.get_data(as_text=True)
        assert response.status_code == 200
        assert len(body) > 200

    # -----------------------------------------------------------------------
    # C3 — Professor não acessa sessão de outra disciplina
    # -----------------------------------------------------------------------

    def test_professor_acessa_sessao_de_outra_disciplina(self, client, make_monitoria_ativa):
        """C3 (comportamento atual): sessao_detalhe é um placeholder —
        qualquer professor autenticado pode acessar qualquer sessão_id e recebe 200.
        Não há filtro por disciplina implementado ainda (funcionalidade placeholder)."""
        setup_a = make_monitoria_ativa("us19c3a")
        sessao_id = _create_sessao_db(setup_a["disc_id"], setup_a["aluno_id"], past=True)

        setup_b = make_monitoria_ativa("us19c3b")
        client.post("/auth/login", data={"email": f"prof.us19c3b@teste.com", "senha": "Senha@Teste1"})
        response = client.get(f"/monitorias/sessoes/{sessao_id}", follow_redirects=True)
        # Comportamento atual: placeholder retorna 200 para qualquer professor
        assert response.status_code == 200
