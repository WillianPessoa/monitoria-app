"""
US06 — Admin cadastra disciplinas

Rota principal:  POST /disciplinas/

Critérios de aceitação (GitHub issue #11):

  C1  Cadastro bem-sucedido
      Given: admin autenticado, professor ativo existente
      When:  preenche código, nome e seleciona professor e confirma
      Then:  disciplina criada com flash de sucesso

  C2  Código duplicado
      Given: disciplina com código X já existe
      When:  admin tenta cadastrar outra com o mesmo código
      Then:  flash "Código já cadastrado."

  C3  Professor inválido
      Given: admin informa ID de usuário sem papel PROFESSOR
      When:  confirma o cadastro
      Then:  flash "Professor inválido."

Cenários extras (derivados do service):
  C4  Campos obrigatórios ausentes
  C5  Professor inexistente (ID não existe no banco)
  C6  Professor com status PENDENTE ou INATIVO → rejeitado
"""

from db.connection import get_connection


def _get_disciplina_by_codigo(codigo):
    """Helper: busca disciplina pelo código direto do banco."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM disciplinas WHERE codigo = %s", (codigo,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


class TestUS06CadastrarDisciplinas:

    # -----------------------------------------------------------------------
    # C1 — Cadastro bem-sucedido
    # -----------------------------------------------------------------------

    def test_admin_cadastra_disciplina_com_sucesso(self, admin_client, make_user):
        """C1: Admin cadastra disciplina válida → flash de sucesso."""
        prof_id = make_user("Prof Caldeira", "prof.caldeira@teste.com", "PROFESSOR")

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB001", "nome": "Cálculo I", "professor_id": prof_id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "disciplina criada com sucesso" in body.lower()

    def test_disciplina_aparece_no_banco_apos_criacao(self, admin_client, make_user):
        """C1: Disciplina criada fica persistida no banco."""
        prof_id = make_user("Prof Azevedo", "prof.azevedo@teste.com", "PROFESSOR")

        admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB002", "nome": "Álgebra Linear", "professor_id": prof_id},
            follow_redirects=True,
        )
        disc = _get_disciplina_by_codigo("MAB002")
        assert disc is not None
        assert disc["nome"] == "Álgebra Linear"
        assert disc["professor_id"] == prof_id

    def test_codigo_e_normalizado_para_maiusculas(self, admin_client, make_user):
        """C1: Código informado em minúsculas é normalizado para maiúsculas."""
        prof_id = make_user("Prof Ferreira", "prof.ferreira@teste.com", "PROFESSOR")

        admin_client.post(
            "/disciplinas/",
            data={"codigo": "mab003", "nome": "Física I", "professor_id": prof_id},
            follow_redirects=True,
        )
        disc = _get_disciplina_by_codigo("MAB003")
        assert disc is not None
        assert disc["codigo"] == "MAB003"

    # -----------------------------------------------------------------------
    # C2 — Código duplicado
    # -----------------------------------------------------------------------

    def test_codigo_duplicado_retorna_erro(self, admin_client, make_user):
        """C2: Tentar cadastrar disciplina com código já existente → flash de erro."""
        prof_id = make_user("Prof Duplo", "prof.duplo@teste.com", "PROFESSOR")

        # Primeira criação — deve passar
        admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB099", "nome": "Disciplina A", "professor_id": prof_id},
            follow_redirects=True,
        )

        # Segunda criação com o mesmo código — deve rejeitar
        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB099", "nome": "Disciplina B", "professor_id": prof_id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "código já cadastrado" in body.lower() or "codigo ja cadastrado" in body.lower()

    def test_codigo_duplicado_case_insensitive(self, admin_client, make_user):
        """C2: Código duplicado em caixa diferente também é rejeitado (normalização para maiúsculas)."""
        prof_id = make_user("Prof Case", "prof.case@teste.com", "PROFESSOR")

        admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB088", "nome": "Disciplina Orig", "professor_id": prof_id},
            follow_redirects=True,
        )

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "mab088", "nome": "Disciplina Dup", "professor_id": prof_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "código já cadastrado" in body.lower() or "codigo ja cadastrado" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Professor inválido
    # -----------------------------------------------------------------------

    def test_aluno_como_professor_retorna_erro(self, admin_client, make_user):
        """C3: ID de usuário com papel ALUNO → flash 'Professor inválido.'"""
        aluno_id = make_user("Aluno Fake", "aluno.fake@teste.com", "ALUNO")

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB010", "nome": "Disciplina Inválida", "professor_id": aluno_id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "professor inválido" in body.lower() or "professor invalido" in body.lower()

    def test_professor_inexistente_retorna_erro(self, admin_client):
        """C5: professor_id que não existe no banco → flash 'Professor inválido.'"""
        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB011", "nome": "Disciplina Inválida", "professor_id": 999999},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "professor inválido" in body.lower() or "professor invalido" in body.lower()

    def test_professor_pendente_retorna_erro(self, admin_client, make_user):
        """C6: Professor com status PENDENTE → rejeitado (service exige status ATIVO)."""
        prof_id = make_user(
            "Prof Pendente", "prof.pendente@teste.com", "PROFESSOR", status="PENDENTE"
        )

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB012", "nome": "Disciplina Pendente", "professor_id": prof_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "professor inválido" in body.lower() or "professor invalido" in body.lower()

    def test_professor_inativo_retorna_erro(self, admin_client, make_user):
        """C6: Professor com status INATIVO → rejeitado."""
        prof_id = make_user(
            "Prof Inativo", "prof.inativo@teste.com", "PROFESSOR", status="INATIVO"
        )

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB013", "nome": "Disciplina Inativa", "professor_id": prof_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "professor inválido" in body.lower() or "professor invalido" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Campos obrigatórios
    # -----------------------------------------------------------------------

    def test_codigo_vazio_retorna_erro(self, admin_client, make_user):
        """C4: Código ausente → flash 'Código e nome são obrigatórios.'"""
        prof_id = make_user("Prof Vazio", "prof.vazio@teste.com", "PROFESSOR")

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "", "nome": "Disciplina Sem Código", "professor_id": prof_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "obrigatórios" in body.lower() or "obrigatorios" in body.lower()

    def test_nome_vazio_retorna_erro(self, admin_client, make_user):
        """C4: Nome ausente → flash 'Código e nome são obrigatórios.'"""
        prof_id = make_user("Prof Sem Nome", "prof.semnome@teste.com", "PROFESSOR")

        response = admin_client.post(
            "/disciplinas/",
            data={"codigo": "MAB014", "nome": "", "professor_id": prof_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "obrigatórios" in body.lower() or "obrigatorios" in body.lower()

    # -----------------------------------------------------------------------
    # Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_nao_pode_criar_disciplina(self, client, make_user):
        """Segurança: requisição sem sessão → redirecionado para login."""
        prof_id = make_user("Prof Sem Auth", "prof.semauth@teste.com", "PROFESSOR")

        response = client.post(
            "/disciplinas/",
            data={"codigo": "MAB015", "nome": "Disciplina Sem Auth", "professor_id": prof_id},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
