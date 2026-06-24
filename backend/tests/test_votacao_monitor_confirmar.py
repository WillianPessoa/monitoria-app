"""
Votação — Monitor confirma resultado e cria sessões da semana

Rota: POST /monitorias/votacao/<int:votacao_id>/confirmar

Regras de negócio:
  - Apenas o monitor da disciplina pode confirmar
  - Precisa selecionar pelo menos 1 slot via monitor_slots=["weekday|hora"]
  - O slot precisa ter votos suficientes (≥ ceil(total_alunos / 2))
  - Slot inexistente na votação → OPCAO_INVALIDA
  - Confirmação bem-sucedida cria monitoria_sessoes e fecha a votação

Cenários:
  C1  Monitor confirma slot com votos suficientes → sessão criada, votação FECHADA
  C2  Monitor confirma antes dos 50% de votos → "50% dos alunos votarem"
  C3  Slot não cadastrado na votação → "Seleção inválida"
  C4  POST sem monitor_slots → flash de erro
  C5  Monitor de outra disciplina → permissão negada
  C6  Votação inexistente → flash de erro
  C7  Não autenticado → redirect para login
"""

from db.connection import get_connection
from utils.time import now_sp_naive, week_bounds_for_votacao


def _enroll_aluno(disc_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO disciplina_alunos (disciplina_id, aluno_id) VALUES (%s, %s)",
        (disc_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()


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


def _create_opcao(votacao_id, slot1_weekday=1, slot1_hora="10:00:00"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO votacao_opcoes (votacao_id, modo, slot1_weekday, slot1_hora_inicio)
        VALUES (%s, 'SLOT_1H', %s, %s)
        """,
        (votacao_id, slot1_weekday, slot1_hora),
    )
    conn.commit()
    opcao_id = cur.lastrowid
    cur.close()
    conn.close()
    return opcao_id


def _cast_vote(votacao_id, opcao_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO votos (votacao_id, opcao_id, aluno_id) VALUES (%s, %s, %s)",
        (votacao_id, opcao_id, aluno_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def _get_votacao_status(votacao_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM votacoes WHERE id = %s", (votacao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


def _count_sessoes_agendadas(disc_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM monitoria_sessoes WHERE disciplina_id = %s AND status = 'AGENDADA'",
        (disc_id,),
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


class TestVotacaoMonitorConfirmar:

    # -----------------------------------------------------------------------
    # C1 — Confirmação bem-sucedida
    # -----------------------------------------------------------------------

    def test_confirmar_cria_sessao_e_fecha_votacao(self, client, make_user, make_monitoria_ativa):
        """C1: 1 aluno enrollado, 1 voto (required=1) → sessão criada e votação FECHADA."""
        setup = make_monitoria_ativa("vmco1")
        aluno_id = make_user("Aluno Confirma", "aluno.vmco1@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id, slot1_weekday=1, slot1_hora="10:00:00")
        _cast_vote(votacao_id, opcao_id, aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={"monitor_slots": ["1|10"]},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "confirmada" in response.get_data(as_text=True).lower()
        assert _count_sessoes_agendadas(setup["disc_id"]) == 1
        assert _get_votacao_status(votacao_id) == "FECHADA"

    def test_confirmar_fecha_votacao(self, client, make_user, make_monitoria_ativa):
        """C1b: Após confirmação bem-sucedida, votação muda para FECHADA."""
        setup = make_monitoria_ativa("vmco1b")
        aluno_id = make_user("Aluno Fecha", "aluno.vmco1b@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id, slot1_weekday=2, slot1_hora="14:00:00")
        _cast_vote(votacao_id, opcao_id, aluno_id)

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={"monitor_slots": ["2|14"]},
            follow_redirects=True,
        )
        assert _get_votacao_status(votacao_id) == "FECHADA"

    # -----------------------------------------------------------------------
    # C2 — Votos insuficientes
    # -----------------------------------------------------------------------

    def test_votos_insuficientes_impede_confirmacao(self, client, make_user, make_monitoria_ativa):
        """C2: 3 alunos enrollados (required=2), só 1 voto → "50% dos alunos votarem"."""
        setup = make_monitoria_ativa("vmco2")
        aluno1_id = make_user("Aluno A", "aluno.vmco2a@teste.com", "ALUNO")
        aluno2_id = make_user("Aluno B", "aluno.vmco2b@teste.com", "ALUNO")
        aluno3_id = make_user("Aluno C", "aluno.vmco2c@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno1_id)
        _enroll_aluno(setup["disc_id"], aluno2_id)
        _enroll_aluno(setup["disc_id"], aluno3_id)
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id, slot1_weekday=1, slot1_hora="10:00:00")
        _cast_vote(votacao_id, opcao_id, aluno1_id)  # só 1 voto, mas required=2

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={"monitor_slots": ["1|10"]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "50%" in body or "alunos votarem" in body.lower()
        assert _get_votacao_status(votacao_id) == "ABERTA"

    # -----------------------------------------------------------------------
    # C3 — Slot inválido
    # -----------------------------------------------------------------------

    def test_slot_invalido_retorna_selecao_invalida(self, client, make_user, make_monitoria_ativa):
        """C3: Weekday/hora não cadastrados na votação → "Seleção inválida"."""
        setup = make_monitoria_ativa("vmco3")
        aluno_id = make_user("Aluno Inv", "aluno.vmco3@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        votacao_id = _create_votacao(setup["disc_id"])
        _create_opcao(votacao_id, slot1_weekday=1, slot1_hora="10:00:00")

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={"monitor_slots": ["3|15"]},  # dia/hora sem opção cadastrada
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "inválida" in body.lower() or "invalida" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Nenhum slot enviado
    # -----------------------------------------------------------------------

    def test_nenhum_slot_enviado_retorna_erro(self, client, make_monitoria_ativa):
        """C4: POST sem monitor_slots → flash pedindo seleção."""
        setup = make_monitoria_ativa("vmco4")
        votacao_id = _create_votacao(setup["disc_id"])

        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "selecione" in body.lower() or "opção" in body.lower() or "opcao" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Monitor de outra disciplina
    # -----------------------------------------------------------------------

    def test_outro_monitor_nao_pode_confirmar(self, client, make_monitoria_ativa):
        """C5: Monitor B tenta confirmar votação da disciplina A → permissão negada."""
        setup_a = make_monitoria_ativa("vmco5a")
        setup_b = make_monitoria_ativa("vmco5b")
        votacao_id = _create_votacao(setup_a["disc_id"])

        client.post("/auth/login", data={"email": setup_b["monitor_email"], "senha": setup_b["monitor_senha"]})
        response = client.post(
            f"/monitorias/votacao/{votacao_id}/confirmar",
            data={"monitor_slots": ["1|10"]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Votação inexistente
    # -----------------------------------------------------------------------

    def test_votacao_inexistente_retorna_erro(self, client, make_monitoria_ativa):
        """C6: votacao_id que não existe → flash de erro."""
        setup = make_monitoria_ativa("vmco6")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/monitorias/votacao/999999/confirmar",
            data={"monitor_slots": ["1|10"]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "inválida" in body.lower() or "invalida" in body.lower()

    # -----------------------------------------------------------------------
    # C7 — Segurança
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C7: Sem sessão ativa → redirect para login."""
        response = client.post("/monitorias/votacao/1/confirmar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
