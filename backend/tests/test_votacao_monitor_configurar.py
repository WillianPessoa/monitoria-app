"""
Votação — Monitor configura carga horária e modo de split

Rota: POST /monitorias/votacao/<int:votacao_id>/configurar

Regras de negócio:
  - Apenas o monitor da disciplina pode configurar
  - Carga horária deve ser 1 ou 2
  - Modo 2h aceita CONSECUTIVAS (padrão) ou SEPARADAS
  - Quando carga = 1, modo é forçado para CONSECUTIVAS

Cenários:
  C1  Monitor configura 1h → sucesso, banco atualizado
  C2  Monitor configura 2h/CONSECUTIVAS → sucesso
  C3  Monitor configura 2h/SEPARADAS → sucesso
  C4  Monitor de outra disciplina → permissão negada
  C5  Carga horária inválida (3) → flash de erro
  C6  Votação inexistente → flash de erro
  C7  Não autenticado → redirect para login
"""

from db.connection import get_connection
from utils.time import now_sp_naive, week_bounds_for_votacao


def _create_votacao(disc_id, carga=1, modo="CONSECUTIVAS"):
    semana_inicio, semana_fim = week_bounds_for_votacao(now_sp_naive())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO votacoes (disciplina_id, semana_inicio, semana_fim, status, carga_horaria_semanal, modo_2h)
        VALUES (%s, %s, %s, 'ABERTA', %s, %s)
        """,
        (disc_id, semana_inicio, semana_fim, carga, modo),
    )
    conn.commit()
    votacao_id = cur.lastrowid
    cur.close()
    conn.close()
    return votacao_id


def _get_votacao(votacao_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT carga_horaria_semanal, modo_2h FROM votacoes WHERE id = %s",
        (votacao_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


class TestVotacaoMonitorConfigurar:

    # -----------------------------------------------------------------------
    # C1 — Configura 1h
    # -----------------------------------------------------------------------

    def test_monitor_configura_1h_com_sucesso(self, client, make_monitoria_ativa):
        """C1: Monitor muda para 1h → flash de sucesso e carga atualizada no banco."""
        setup = make_monitoria_ativa("vmc1")
        votacao_id = _create_votacao(setup["disc_id"], carga=2, modo="CONSECUTIVAS")

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/configurar",
            data={"carga_horaria": "1"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "atualizada" in response.get_data(as_text=True).lower()
        votacao = _get_votacao(votacao_id)
        assert int(votacao["carga_horaria_semanal"]) == 1

    # -----------------------------------------------------------------------
    # C2 — Configura 2h CONSECUTIVAS
    # -----------------------------------------------------------------------

    def test_monitor_configura_2h_consecutivas(self, client, make_monitoria_ativa):
        """C2: Monitor configura 2h/CONSECUTIVAS → banco atualizado."""
        setup = make_monitoria_ativa("vmc2")
        votacao_id = _create_votacao(setup["disc_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/configurar",
            data={"carga_horaria": "2", "modo_2h": "CONSECUTIVAS"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        votacao = _get_votacao(votacao_id)
        assert int(votacao["carga_horaria_semanal"]) == 2
        assert votacao["modo_2h"] == "CONSECUTIVAS"

    # -----------------------------------------------------------------------
    # C3 — Configura 2h SEPARADAS
    # -----------------------------------------------------------------------

    def test_monitor_configura_2h_separadas(self, client, make_monitoria_ativa):
        """C3: Monitor configura 2h/SEPARADAS → banco atualizado."""
        setup = make_monitoria_ativa("vmc3")
        votacao_id = _create_votacao(setup["disc_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/configurar",
            data={"carga_horaria": "2", "modo_2h": "SEPARADAS"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        votacao = _get_votacao(votacao_id)
        assert int(votacao["carga_horaria_semanal"]) == 2
        assert votacao["modo_2h"] == "SEPARADAS"

    # -----------------------------------------------------------------------
    # C4 — Monitor de outra disciplina
    # -----------------------------------------------------------------------

    def test_outro_monitor_nao_pode_configurar(self, client, make_monitoria_ativa):
        """C4: Monitor B tenta configurar votação da disciplina A → permissão negada."""
        setup_a = make_monitoria_ativa("vmc4a")
        setup_b = make_monitoria_ativa("vmc4b")
        votacao_id = _create_votacao(setup_a["disc_id"])

        client.post("/auth/login", data={"email": setup_b["monitor_email"], "senha": setup_b["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/configurar",
            data={"carga_horaria": "1"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Carga inválida
    # -----------------------------------------------------------------------

    def test_carga_horaria_invalida_retorna_erro(self, client, make_monitoria_ativa):
        """C5: carga_horaria=3 (fora do domínio 1|2) → flash de erro."""
        setup = make_monitoria_ativa("vmc5")
        votacao_id = _create_votacao(setup["disc_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/configurar",
            data={"carga_horaria": "3"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "inválida" in body.lower() or "invalida" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Votação inexistente
    # -----------------------------------------------------------------------

    def test_votacao_inexistente_retorna_erro(self, client, make_monitoria_ativa):
        """C6: votacao_id que não existe → flash de erro."""
        setup = make_monitoria_ativa("vmc6")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/monitorias/votacao/999999/configurar",
            data={"carga_horaria": "1"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "inválida" in body.lower() or "invalida" in body.lower()

    # -----------------------------------------------------------------------
    # C7 — Segurança
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C7: Sem sessão ativa → redirect para login."""
        response = client.post("/monitorias/votacao/1/configurar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
