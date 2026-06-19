"""
US02 — Usuário faz login com email e senha

Rota:   POST /auth/login
Campos: email, senha

Cenários (criterios-de-aceitacao.md):
  C1  Login bem-sucedido
      → autenticado e redirecionado para a tela do seu papel
  C2  Credenciais inválidas
      → mensagem de erro genérica (sem revelar qual campo está errado)
  C3  Primeiro acesso (status PENDENTE)
      → redirecionado para /auth/primeiro-acesso
  C4  Usuário inativo
      → login negado com mensagem de conta inativa

Mensagens do backend (auth/service.py):
  "Credenciais invalidas."   — email não encontrado ou senha errada
  "Sua conta esta inativa."  — status INATIVO

Redirects por papel (auth/routes.py):
  ADMIN     → /usuarios/
  ALUNO     → /
  PROFESSOR → /
  MONITOR   → /usuarios/meu-perfil
"""


class TestUS02Login:

    # -----------------------------------------------------------------------
    # C1 — Login bem-sucedido
    # -----------------------------------------------------------------------

    def test_admin_redireciona_para_usuarios(self, client):
        """C1: Admin com credenciais corretas → 302 para /usuarios/."""
        response = client.post(
            "/auth/login",
            data={"email": "willian.pessoa.cs@gmail.com", "senha": "monitoria-app"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/usuarios/" in response.location

    def test_aluno_redireciona_para_home(self, client, make_user):
        """C1: Aluno ativo com credenciais corretas → 302 para /."""
        make_user("Aluno Teste", "aluno@teste.com", "ALUNO", senha="Senha@Teste1")

        response = client.post(
            "/auth/login",
            data={"email": "aluno@teste.com", "senha": "Senha@Teste1"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.endswith("/")

    def test_professor_redireciona_para_home(self, client, make_user):
        """C1: Professor ativo com credenciais corretas → 302 para /."""
        make_user("Prof Teste", "prof@teste.com", "PROFESSOR", senha="Senha@Teste1")

        response = client.post(
            "/auth/login",
            data={"email": "prof@teste.com", "senha": "Senha@Teste1"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.endswith("/")

    def test_login_cria_sessao_com_dados_do_usuario(self, client, make_user):
        """C1: Após login bem-sucedido, sessão contém user_id e papel."""
        make_user("Aluno Sessao", "sessao@teste.com", "ALUNO", senha="Senha@Teste1")

        client.post(
            "/auth/login",
            data={"email": "sessao@teste.com", "senha": "Senha@Teste1"},
        )
        with client.session_transaction() as sess:
            assert sess.get("user_id") is not None
            assert sess.get("papel") == "ALUNO"

    # -----------------------------------------------------------------------
    # C2 — Credenciais inválidas
    # -----------------------------------------------------------------------

    def test_senha_errada_exibe_erro_generico(self, client):
        """C2: Senha errada → status 200, mensagem genérica sem revelar o campo."""
        response = client.post(
            "/auth/login",
            data={"email": "willian.pessoa.cs@gmail.com", "senha": "senha-errada"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "invalidas" in body.lower() or "inválidas" in body.lower()

    def test_email_inexistente_exibe_mesmo_erro_generico(self, client):
        """C2: Email inexistente → mesma mensagem que senha errada (não revela qual campo)."""
        response = client.post(
            "/auth/login",
            data={"email": "nao-existe@teste.com", "senha": "qualquer"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "invalidas" in body.lower() or "inválidas" in body.lower()

    def test_credenciais_invalidas_nao_criam_sessao(self, client):
        """C2: Login com credenciais erradas → nenhuma sessão criada."""
        client.post(
            "/auth/login",
            data={"email": "willian.pessoa.cs@gmail.com", "senha": "errada"},
        )
        with client.session_transaction() as sess:
            assert sess.get("user_id") is None

    # -----------------------------------------------------------------------
    # C3 — Primeiro acesso (status PENDENTE)
    # -----------------------------------------------------------------------

    def test_usuario_pendente_redireciona_primeiro_acesso(self, client, make_user):
        """C3: Usuário PENDENTE → 302 para /auth/primeiro-acesso."""
        make_user(
            "Pendente Teste", "pendente@teste.com", "ALUNO",
            status="PENDENTE", senha="Senha@Teste1"
        )

        response = client.post(
            "/auth/login",
            data={"email": "pendente@teste.com", "senha": "Senha@Teste1"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "primeiro-acesso" in response.location

    def test_usuario_pendente_armazena_id_na_sessao(self, client, make_user):
        """C3: Redirecionado para primeiro acesso → sessão contém first_access_user_id."""
        make_user(
            "Pendente Sessao", "pendente2@teste.com", "ALUNO",
            status="PENDENTE", senha="Senha@Teste1"
        )

        client.post(
            "/auth/login",
            data={"email": "pendente2@teste.com", "senha": "Senha@Teste1"},
        )
        with client.session_transaction() as sess:
            assert sess.get("first_access_user_id") is not None
            assert sess.get("user_id") is None  # Ainda não autenticado de fato

    # -----------------------------------------------------------------------
    # C4 — Usuário inativo
    # -----------------------------------------------------------------------

    def test_usuario_inativo_login_negado(self, client, make_user):
        """C4: Usuário INATIVO → status 200, mensagem de conta inativa."""
        make_user(
            "Inativo Teste", "inativo@teste.com", "ALUNO",
            status="INATIVO", senha="Senha@Teste1"
        )

        response = client.post(
            "/auth/login",
            data={"email": "inativo@teste.com", "senha": "Senha@Teste1"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "inativa" in body.lower()

    def test_usuario_inativo_nao_cria_sessao(self, client, make_user):
        """C4: Login negado por conta inativa → nenhuma sessão criada."""
        make_user(
            "Inativo Sessao", "inativo2@teste.com", "ALUNO",
            status="INATIVO", senha="Senha@Teste1"
        )

        client.post(
            "/auth/login",
            data={"email": "inativo2@teste.com", "senha": "Senha@Teste1"},
        )
        with client.session_transaction() as sess:
            assert sess.get("user_id") is None
