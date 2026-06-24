"""
Votação — Aluno vota em horário proposto pelo monitor

Rota: POST /disciplinas/<int:disciplina_id>/votar

Regras de negócio:
  - Apenas alunos matriculados na disciplina podem votar (papel ALUNO + disciplina_alunos)
  - Precisa haver votação ABERTA para a semana corrente
  - Pelo menos 1 opção precisa ser selecionada

Cenários:
  C1  Aluno matriculado vota com opção válida → "Voto registrado com sucesso"
  C2  Aluno não matriculado → permissão negada
  C3  Admin (papel != ALUNO) tenta votar → permissão negada
  C4  POST sem opcao_ids → "Escolha ao menos um horário válido"
  C5  Votação inexistente para a semana → "Votação indisponível"
  C6  Não autenticado → redirect para login
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


def _create_votacao(disc_id):
    semana_inicio, semana_fim = week_bounds_for_votacao(now_sp_naive())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO votacoes (disciplina_id, semana_inicio, semana_fim, status, carga_horaria_semanal, modo_2h)
        VALUES (%s, %s, %s, 'ABERTA', 1, 'CONSECUTIVAS')
        """,
        (disc_id, semana_inicio, semana_fim),
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


def _get_votos(votacao_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM votos WHERE votacao_id = %s AND aluno_id = %s",
        (votacao_id, aluno_id),
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


class TestVotacaoAlunoVotar:

    # -----------------------------------------------------------------------
    # C1 — Voto bem-sucedido
    # -----------------------------------------------------------------------

    def test_aluno_matriculado_vota_com_sucesso(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno matriculado com votação aberta → voto registrado."""
        setup = make_monitoria_ativa("vav1")
        aluno_id = make_user("Aluno Votante", "aluno.vav1@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id)

        client.post("/auth/login", data={"email": "aluno.vav1@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [opcao_id]},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "voto registrado" in response.get_data(as_text=True).lower()

    def test_voto_bem_sucedido_salva_no_banco(self, client, make_user, make_monitoria_ativa):
        """C1b: Após voto bem-sucedido, registro existe na tabela votos."""
        setup = make_monitoria_ativa("vav1b")
        aluno_id = make_user("Aluno Banco", "aluno.vav1b@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id)

        client.post("/auth/login", data={"email": "aluno.vav1b@teste.com", "senha": "Senha@Teste1"})
        client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [opcao_id]},
            follow_redirects=True,
        )
        assert _get_votos(votacao_id, aluno_id) == 1

    # -----------------------------------------------------------------------
    # C2 — Aluno não matriculado
    # -----------------------------------------------------------------------

    def test_aluno_nao_matriculado_nao_pode_votar(self, client, make_user, make_monitoria_ativa):
        """C2: Aluno sem disciplina_alunos → permissão negada."""
        setup = make_monitoria_ativa("vav2")
        aluno_id = make_user("Aluno Externo", "aluno.vav2@teste.com", "ALUNO")
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id)

        client.post("/auth/login", data={"email": "aluno.vav2@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [opcao_id]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Papel inválido
    # -----------------------------------------------------------------------

    def test_admin_nao_pode_votar(self, admin_client, make_monitoria_ativa):
        """C3: Admin (papel != ALUNO) → permissão negada."""
        setup = make_monitoria_ativa("vav3")
        votacao_id = _create_votacao(setup["disc_id"])
        opcao_id = _create_opcao(votacao_id)

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [opcao_id]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Nenhuma opção selecionada
    # -----------------------------------------------------------------------

    def test_voto_sem_opcao_retorna_erro(self, client, make_user, make_monitoria_ativa):
        """C4: POST sem opcao_ids → flash de erro exigindo ao menos 1 opção."""
        setup = make_monitoria_ativa("vav4")
        aluno_id = make_user("Aluno Sem Opcao", "aluno.vav4@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        _create_votacao(setup["disc_id"])

        client.post("/auth/login", data={"email": "aluno.vav4@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "ao menos" in body.lower() or "válido" in body.lower() or "valido" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Votação inexistente
    # -----------------------------------------------------------------------

    def test_votacao_inexistente_retorna_indisponivel(self, client, make_user, make_monitoria_ativa):
        """C5: Sem votação aberta para a semana → "Votação indisponível"."""
        setup = make_monitoria_ativa("vav5")
        aluno_id = make_user("Aluno Sem Votacao", "aluno.vav5@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        # Não cria votação

        client.post("/auth/login", data={"email": "aluno.vav5@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [999]},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "indisponível" in body.lower() or "indisponivel" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Segurança
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client, make_monitoria_ativa):
        """C6: Sem sessão ativa → redirect para login."""
        setup = make_monitoria_ativa("vav6")
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/votar",
            data={"opcao_ids": [1]},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
