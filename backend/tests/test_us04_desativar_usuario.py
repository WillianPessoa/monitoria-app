"""
US04 — Admin desativa (e reativa) um usuário

Rotas:  POST /usuarios/<id>/desativar
        POST /usuarios/<id>/reativar

ATENÇÃO: US04 não tem critérios BDD definidos em criterios-de-aceitacao.md.
Os cenários abaixo foram derivados do comportamento da rota e do repositório.

Cenários derivados do código:
  C1  Admin desativa usuário ativo → status vira INATIVO, flash de sucesso
  C2  Admin não pode desativar a si mesmo → flash de erro, status permanece ATIVO
  C3  Admin reativa usuário inativo → status vira ATIVO, flash de sucesso
  C4  Tentativa de desativar ID inexistente → flash de não encontrado

Mensagens da rota (usuarios/routes.py):
  "Usuário desativado com sucesso."
  "Você não pode desativar o próprio usuário."
  "Usuário reativado com sucesso."
  "Usuário não encontrado."
"""

from db.connection import get_connection


def _get_user_status(user_id):
    """Helper: retorna o status atual do usuário direto do banco."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status FROM usuarios WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["status"] if row else None


class TestUS04DesativarUsuario:

    # -----------------------------------------------------------------------
    # C1 — Desativação bem-sucedida
    # -----------------------------------------------------------------------

    def test_admin_desativa_usuario_ativo(self, admin_client, make_user):
        """C1: Admin desativa outro usuário → status vira INATIVO."""
        user_id = make_user("Aluno Alvo", "alvo@teste.com", "ALUNO")

        response = admin_client.post(
            f"/usuarios/{user_id}/desativar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "desativado com sucesso" in body.lower()
        assert _get_user_status(user_id) == "INATIVO"

    # -----------------------------------------------------------------------
    # C2 — Admin não pode se auto-desativar
    # -----------------------------------------------------------------------

    def test_admin_nao_pode_desativar_a_si_mesmo(self, admin_client):
        """C2: Admin tenta desativar o próprio usuário → rejeitado."""
        # Busca o user_id do admin logado pela sessão
        with admin_client.session_transaction() as sess:
            own_id = sess.get("user_id")

        response = admin_client.post(
            f"/usuarios/{own_id}/desativar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não pode desativar" in body.lower() or "nao pode desativar" in body.lower()
        # Status do próprio admin deve permanecer ATIVO
        assert _get_user_status(own_id) == "ATIVO"

    # -----------------------------------------------------------------------
    # C3 — Reativação bem-sucedida
    # -----------------------------------------------------------------------

    def test_admin_reativa_usuario_inativo(self, admin_client, make_user):
        """C3: Admin reativa usuário previamente desativado → status vira ATIVO."""
        user_id = make_user("Aluno Reativar", "reativar@teste.com", "ALUNO", status="INATIVO")

        response = admin_client.post(
            f"/usuarios/{user_id}/reativar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "reativado com sucesso" in body.lower()
        assert _get_user_status(user_id) == "ATIVO"

    # -----------------------------------------------------------------------
    # C4 — ID inexistente
    # -----------------------------------------------------------------------

    def test_desativar_id_inexistente_retorna_erro(self, admin_client):
        """C4: Tentativa de desativar ID que não existe → flash de não encontrado."""
        response = admin_client.post(
            "/usuarios/999999/desativar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não encontrado" in body.lower() or "nao encontrado" in body.lower()

    # -----------------------------------------------------------------------
    # Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_nao_pode_desativar(self, client, make_user):
        """Segurança: requisição sem sessão → redirecionado para login."""
        user_id = make_user("Alvo Sem Auth", "sem-auth@teste.com", "ALUNO")

        response = client.post(
            f"/usuarios/{user_id}/desativar",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
