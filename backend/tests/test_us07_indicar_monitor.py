"""
US07 — Professor indica aluno como monitor

Rota:  POST /monitorias/indicar  (requer papel PROFESSOR)

Critérios de aceitação (GitHub issue #12):

  C1  Indicação bem-sucedida
      Given: professor autenticado com disciplina própria, aluno ativo existente
      When:  professor submete o formulário de indicação
      Then:  flash "Indicação enviada para aprovação.", vínculo criado com status PENDENTE_APROVACAO

  C2  Indicação de usuário sem papel aluno
      Given: professor tenta indicar ID de usuário que não é aluno
      When:  confirma a indicação
      Then:  flash "Aluno inválido."

  C3  Disciplina de outro professor
      Given: professor tenta indicar para disciplina que não é de sua responsabilidade
      When:  confirma a indicação
      Then:  flash "Disciplina inválida."
"""

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers diretos ao banco
# ---------------------------------------------------------------------------


def _create_disciplina(codigo, nome, professor_id):
    """Cria disciplina diretamente no banco para montar pré-condição."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO disciplinas (codigo, nome, professor_id) VALUES (%s, %s, %s)",
        (codigo, nome, professor_id),
    )
    conn.commit()
    disc_id = cur.lastrowid
    cur.close()
    conn.close()
    return disc_id


def _get_indicacao(disciplina_id, aluno_id):
    """Retorna a indicação de monitoria para um par disciplina/aluno."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM monitorias WHERE disciplina_id = %s AND aluno_id = %s",
        (disciplina_id, aluno_id),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def _login_as(client, email, senha="Senha@Teste1"):
    """Faz login com as credenciais informadas e retorna o client."""
    client.post("/auth/login", data={"email": email, "senha": senha})
    return client


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS07IndicarMonitor:

    # -----------------------------------------------------------------------
    # C1 — Indicação bem-sucedida
    # -----------------------------------------------------------------------

    def test_professor_indica_aluno_com_sucesso(self, client, make_user):
        """C1: Professor indica aluno da sua disciplina → flash de sucesso."""
        prof_id = make_user("Prof Indica", "prof.indica@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB200", "Cálculo II", prof_id)
        aluno_id = make_user("Aluno Indica", "aluno.indica@teste.com", "ALUNO")

        _login_as(client, "prof.indica@teste.com")
        response = client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": aluno_id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "indicação enviada" in body.lower() or "indicacao enviada" in body.lower()

    def test_indicacao_criada_com_status_pendente(self, client, make_user):
        """C1: Indicação criada tem status PENDENTE_APROVACAO no banco."""
        prof_id = make_user("Prof Pendente", "prof.pendente@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB201", "Álgebra II", prof_id)
        aluno_id = make_user("Aluno Pendente", "aluno.pendente@teste.com", "ALUNO")

        _login_as(client, "prof.pendente@teste.com")
        client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": aluno_id},
            follow_redirects=True,
        )
        indicacao = _get_indicacao(disc_id, aluno_id)
        assert indicacao is not None
        assert indicacao["status"] == "PENDENTE_APROVACAO"
        assert indicacao["professor_id"] == prof_id

    def test_indicacao_reenvio_reutiliza_registro(self, client, make_user):
        """C1: Reenviar indicação do mesmo par disciplina/aluno reusa o registro existente."""
        prof_id = make_user("Prof Reenv", "prof.reenv@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB202", "Física II", prof_id)
        aluno_id = make_user("Aluno Reenv", "aluno.reenv@teste.com", "ALUNO")

        _login_as(client, "prof.reenv@teste.com")
        client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": aluno_id},
            follow_redirects=True,
        )
        client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": aluno_id},
            follow_redirects=True,
        )

        # Deve existir apenas um registro no banco (ON DUPLICATE KEY UPDATE)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM monitorias WHERE disciplina_id = %s AND aluno_id = %s",
            (disc_id, aluno_id),
        )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        assert count == 1

    # -----------------------------------------------------------------------
    # C2 — Usuário sem papel aluno
    # -----------------------------------------------------------------------

    def test_indicar_professor_como_aluno_retorna_erro(self, client, make_user):
        """C2: Tentar indicar usuário com papel PROFESSOR → flash 'Aluno inválido.'"""
        prof1_id = make_user("Prof Válido", "prof.valido@teste.com", "PROFESSOR")
        prof2_id = make_user("Prof Fake Aluno", "prof.fakealuno@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB203", "Discreta", prof1_id)

        _login_as(client, "prof.valido@teste.com")
        response = client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": prof2_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "aluno inválido" in body.lower() or "aluno invalido" in body.lower()

    def test_indicar_admin_como_aluno_retorna_erro(self, admin_client, make_user, client):
        """C2: Tentar indicar usuário com papel ADMIN como aluno → rejeitado."""
        with admin_client.session_transaction() as sess:
            admin_id = sess.get("user_id")

        prof_id = make_user("Prof Check", "prof.check@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB204", "Compiladores", prof_id)

        _login_as(client, "prof.check@teste.com")
        response = client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_id, "aluno_id": admin_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "aluno inválido" in body.lower() or "aluno invalido" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Disciplina de outro professor
    # -----------------------------------------------------------------------

    def test_professor_nao_pode_indicar_para_disciplina_alheia(self, client, make_user):
        """C3: Professor tenta indicar para disciplina de outro professor → 'Disciplina inválida.'"""
        prof_a = make_user("Prof A", "prof.a@teste.com", "PROFESSOR")
        prof_b = make_user("Prof B", "prof.b@teste.com", "PROFESSOR")
        disc_b = _create_disciplina("MAB205", "SO", prof_b)
        aluno_id = make_user("Aluno C3", "aluno.c3@teste.com", "ALUNO")

        _login_as(client, "prof.a@teste.com")
        response = client.post(
            "/monitorias/indicar",
            data={"disciplina_id": disc_b, "aluno_id": aluno_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "disciplina inválida" in body.lower() or "disciplina invalida" in body.lower()

    # -----------------------------------------------------------------------
    # Proteção de acesso
    # -----------------------------------------------------------------------

    def test_aluno_nao_pode_acessar_tela_de_indicacao(self, client, make_user):
        """Segurança: Papel ALUNO tenta acessar /monitorias/indicar → redirecionado."""
        make_user("Aluno Guard", "aluno.guard@teste.com", "ALUNO")
        _login_as(client, "aluno.guard@teste.com")

        response = client.get("/monitorias/indicar", follow_redirects=False)
        assert response.status_code == 302

    def test_nao_autenticado_redireciona_para_login(self, client):
        """Segurança: sem sessão → redirecionado para login."""
        response = client.post(
            "/monitorias/indicar",
            data={"disciplina_id": 1, "aluno_id": 1},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
