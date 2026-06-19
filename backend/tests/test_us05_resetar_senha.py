"""
US05 — Admin muda a senha do usuário manualmente

Rota:  POST /usuarios/<id>/resetar-senha

Critérios de aceitação (GitHub issue #10):

  C1  Reset bem-sucedido
      Given: admin autenticado
      When:  chama POST /usuarios/<id>/resetar-senha
      Then:  flash com a nova senha temporária é exibido
             usuário fica com senha_temporaria=True e status PENDENTE

  C2  Usuário inexistente
      Given: admin tenta resetar senha de ID que não existe
      When:  a requisição é processada
      Then:  flash "Usuário não encontrado."
             (o BDD do issue menciona HTTP 404, mas a rota implementa flash + redirect;
              testamos o comportamento real)

Cenários extras (derivados da rota):
  C3  Admin não pode resetar a própria senha via esta tela
"""

from db.connection import get_connection


def _get_password_state(user_id):
    """Helper: retorna senha_temporaria e status do usuário direto do banco."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT status, senha_temporaria FROM usuarios WHERE id = %s", (user_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


class TestUS05ResetarSenha:

    # -----------------------------------------------------------------------
    # C1 — Reset bem-sucedido
    # -----------------------------------------------------------------------

    def test_admin_reseta_senha_exibe_senha_temporaria(self, admin_client, make_user):
        """C1: Admin reseta senha → flash contém a nova senha temporária."""
        user_id = make_user("Aluno Reset", "reset@teste.com", "ALUNO")

        response = admin_client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "senha redefinida" in body.lower()
        assert "nova senha temporária" in body.lower()

    def test_reset_marca_usuario_com_senha_temporaria(self, admin_client, make_user):
        """C1: Após reset, senha_temporaria=True no banco."""
        user_id = make_user("Aluno Temp", "temp@teste.com", "ALUNO")

        admin_client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=True,
        )
        state = _get_password_state(user_id)
        assert state["senha_temporaria"] == 1

    def test_reset_muda_status_para_pendente(self, admin_client, make_user):
        """C1: Após reset, status do usuário vira PENDENTE."""
        user_id = make_user("Aluno Status", "status@teste.com", "ALUNO", status="ATIVO")

        admin_client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=True,
        )
        state = _get_password_state(user_id)
        assert state["status"] == "PENDENTE"

    def test_reset_senha_diferente_a_cada_chamada(self, admin_client, make_user):
        """C1: Cada reset gera uma senha diferente (probabilidade ínfima de colisão)."""
        user_id = make_user("Aluno Duplo", "duplo@teste.com", "ALUNO")

        resp1 = admin_client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=True,
        )
        body1 = resp1.get_data(as_text=True)

        resp2 = admin_client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=True,
        )
        body2 = resp2.get_data(as_text=True)

        # Extrai as senhas temporárias dos flashes (aparecem após "temporária: ")
        import re
        match1 = re.search(r"temporária:\s*(\S+)", body1)
        match2 = re.search(r"temporária:\s*(\S+)", body2)
        assert match1 and match2
        # As senhas devem ser diferentes
        assert match1.group(1) != match2.group(1)

    # -----------------------------------------------------------------------
    # C2 — Usuário inexistente
    # -----------------------------------------------------------------------

    def test_resetar_senha_id_inexistente_exibe_erro(self, admin_client):
        """C2: Resetar senha de ID que não existe → flash 'não encontrado'."""
        response = admin_client.post(
            "/usuarios/999999/resetar-senha",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não encontrado" in body.lower() or "nao encontrado" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Admin não pode resetar a própria senha
    # -----------------------------------------------------------------------

    def test_admin_nao_pode_resetar_propria_senha(self, admin_client):
        """C3: Admin tenta resetar a própria senha → rejeitado com flash de erro."""
        with admin_client.session_transaction() as sess:
            own_id = sess.get("user_id")

        response = admin_client.post(
            f"/usuarios/{own_id}/resetar-senha",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não pode resetar" in body.lower() or "nao pode resetar" in body.lower()

    # -----------------------------------------------------------------------
    # Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_nao_pode_resetar_senha(self, client, make_user):
        """Segurança: requisição sem sessão → redirecionado para login."""
        user_id = make_user("Alvo Sem Auth", "sem-auth-reset@teste.com", "ALUNO")

        response = client.post(
            f"/usuarios/{user_id}/resetar-senha",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
