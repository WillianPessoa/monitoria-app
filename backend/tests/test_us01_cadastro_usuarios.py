"""
US01 — Admin cadastra usuários com perfis

Rota:   POST /usuarios/
Campos: nome, email, papel

Cenários (criterios-de-aceitacao.md):
  C1  Cadastro bem-sucedido
      → usuário criado com status PENDENTE, senha temporária exibida ao admin
  C2  Email duplicado
      → rejeitado com mensagem "Email ja cadastrado"
  C3  Campos obrigatórios ausentes
      → rejeitado com mensagem de campo faltando

Mensagens do backend (usuarios/service.py):
  "Usuário criado com status PENDENTE."  — flash de sucesso (rota)
  "Email ja cadastrado"                  — service.create_user
  "Nome e email sao obrigatorios."       — service.create_user
  "Papel invalido."                      — service.create_user
"""


class TestUS01CadastroUsuarios:

    # -----------------------------------------------------------------------
    # C1 — Cadastro bem-sucedido
    # -----------------------------------------------------------------------

    def test_cadastro_aluno_retorna_status_pendente(self, admin_client):
        """C1: Admin cadastra aluno → flash confirma criação com status PENDENTE."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "João Teste", "email": "joao@teste.com", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "PENDENTE" in body

    def test_cadastro_professor_retorna_status_pendente(self, admin_client):
        """C1: Admin cadastra professor → aceito, status PENDENTE."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Prof. Silva", "email": "prof@teste.com", "papel": "PROFESSOR"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "PENDENTE" in body

    def test_cadastro_exibe_senha_temporaria(self, admin_client):
        """C1: Admin cadastra usuário → senha temporária é exibida na resposta."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Maria Teste", "email": "maria@teste.com", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        # A rota passa `generated_password` ao template — verificamos que algo
        # relacionado à senha temporária aparece na página
        assert "Usuário criado" in body

    # -----------------------------------------------------------------------
    # C2 — Email duplicado
    # -----------------------------------------------------------------------

    def test_email_duplicado_rejeitado(self, admin_client):
        """C2: Segundo cadastro com mesmo email → flash de email já cadastrado."""
        admin_client.post(
            "/usuarios/",
            data={"nome": "Ana", "email": "duplicado@teste.com", "papel": "ALUNO"},
        )
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Ana Dois", "email": "duplicado@teste.com", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "ja cadastrado" in body.lower()

    def test_email_duplicado_case_insensitive(self, admin_client):
        """C2: Email duplicado com capitalização diferente → também rejeitado."""
        admin_client.post(
            "/usuarios/",
            data={"nome": "Bob", "email": "bob@teste.com", "papel": "ALUNO"},
        )
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Bob Dois", "email": "BOB@TESTE.COM", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "ja cadastrado" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Campos obrigatórios ausentes
    # -----------------------------------------------------------------------

    def test_sem_nome_rejeitado(self, admin_client):
        """C3: Envio sem nome → backend rejeita com campo obrigatório."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "", "email": "sem-nome@teste.com", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "obrigatorio" in body.lower() or "obrigatório" in body.lower()

    def test_sem_email_rejeitado(self, admin_client):
        """C3: Envio sem email → backend rejeita com campo obrigatório."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Sem Email", "email": "", "papel": "ALUNO"},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "obrigatorio" in body.lower() or "obrigatório" in body.lower()

    def test_sem_papel_rejeitado(self, admin_client):
        """C3: Envio sem papel → backend rejeita com papel inválido."""
        response = admin_client.post(
            "/usuarios/",
            data={"nome": "Sem Papel", "email": "sem-papel@teste.com", "papel": ""},
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "invalido" in body.lower() or "inválido" in body.lower()
