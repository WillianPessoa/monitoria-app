"""
US08 — Admin aprova ou rejeita indicação de monitor

Rotas:  POST /monitorias/<id>/aprovar
        POST /monitorias/<id>/rejeitar

Critérios de aceitação (GitHub issue #13):

  C1  Aprovação
      Given: indicação com status PENDENTE_APROVACAO
      When:  admin aprova
      Then:  status vira ATIVO, flash "Indicação aprovada."

  C2  Rejeição com motivo
      Given: indicação com status PENDENTE_APROVACAO
      When:  admin rejeita informando motivo
      Then:  status vira REJEITADO, motivo_rejeicao registrado no banco

  C3  Indicação processada sai da fila
      Given: admin aprova ou rejeita uma indicação
      When:  GET /monitorias/pendentes
      Then:  a indicação não aparece mais na listagem

Cenários extras:
  C4  Aluno já é monitor ativo em outra disciplina → flash "Aluno já possui monitoria ativa."
  C5  Tentar aprovar/rejeitar ID inexistente → flash de erro
"""

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers diretos ao banco
# ---------------------------------------------------------------------------


def _create_disciplina(codigo, nome, professor_id):
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


def _create_indicacao_pendente(disciplina_id, professor_id, aluno_id):
    """Cria indicação com status PENDENTE_APROVACAO diretamente no banco."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
        VALUES (%s, %s, %s, 'PENDENTE_APROVACAO')
        """,
        (disciplina_id, professor_id, aluno_id),
    )
    conn.commit()
    monitoria_id = cur.lastrowid
    cur.close()
    conn.close()
    return monitoria_id


def _get_monitoria_status(monitoria_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status, motivo_rejeicao FROM monitorias WHERE id = %s", (monitoria_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS08AprovarRejeitarIndicacao:

    # -----------------------------------------------------------------------
    # C1 — Aprovação bem-sucedida
    # -----------------------------------------------------------------------

    def test_admin_aprova_indicacao_pendente(self, admin_client, make_user):
        """C1: Admin aprova indicação → flash de sucesso."""
        prof_id = make_user("Prof Aprova", "prof.aprova@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB300", "Teoria da Comp.", prof_id)
        aluno_id = make_user("Aluno Aprova", "aluno.aprova@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        response = admin_client.post(
            f"/monitorias/{monitoria_id}/aprovar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "indicação aprovada" in body.lower() or "indicacao aprovada" in body.lower()

    def test_aprovacao_muda_status_para_ativo(self, admin_client, make_user):
        """C1: Após aprovação, status da monitoria vira ATIVO no banco."""
        prof_id = make_user("Prof Ativo", "prof.ativo@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB301", "Lógica", prof_id)
        aluno_id = make_user("Aluno Ativo", "aluno.ativo@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        admin_client.post(f"/monitorias/{monitoria_id}/aprovar", follow_redirects=True)
        state = _get_monitoria_status(monitoria_id)
        assert state["status"] == "ATIVO"

    # -----------------------------------------------------------------------
    # C2 — Rejeição com motivo
    # -----------------------------------------------------------------------

    def test_admin_rejeita_indicacao_com_motivo(self, admin_client, make_user):
        """C2: Admin rejeita indicação → flash de sucesso."""
        prof_id = make_user("Prof Rejeita", "prof.rejeita@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB302", "Redes", prof_id)
        aluno_id = make_user("Aluno Rejeita", "aluno.rejeita@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        response = admin_client.post(
            f"/monitorias/{monitoria_id}/rejeitar",
            data={"motivo": "Aluno com histórico insatisfatório"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "indicação rejeitada" in body.lower() or "indicacao rejeitada" in body.lower()

    def test_rejeicao_muda_status_para_rejeitado(self, admin_client, make_user):
        """C2: Após rejeição, status vira REJEITADO no banco."""
        prof_id = make_user("Prof Rej", "prof.rej@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB303", "BD", prof_id)
        aluno_id = make_user("Aluno Rej", "aluno.rej@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        admin_client.post(
            f"/monitorias/{monitoria_id}/rejeitar",
            data={"motivo": "Nota insuficiente"},
            follow_redirects=True,
        )
        state = _get_monitoria_status(monitoria_id)
        assert state["status"] == "REJEITADO"

    def test_motivo_rejeicao_registrado_no_banco(self, admin_client, make_user):
        """C2: Motivo da rejeição fica salvo em motivo_rejeicao no banco."""
        prof_id = make_user("Prof Motivo", "prof.motivo@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB304", "IHC", prof_id)
        aluno_id = make_user("Aluno Motivo", "aluno.motivo@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        motivo_esperado = "Aluno já reprovado duas vezes na disciplina"
        admin_client.post(
            f"/monitorias/{monitoria_id}/rejeitar",
            data={"motivo": motivo_esperado},
            follow_redirects=True,
        )
        state = _get_monitoria_status(monitoria_id)
        assert state["motivo_rejeicao"] == motivo_esperado

    # -----------------------------------------------------------------------
    # C3 — Indicação processada sai da fila de pendentes
    # -----------------------------------------------------------------------

    def test_aprovada_nao_aparece_em_pendentes(self, admin_client, make_user):
        """C3: Indicação aprovada não aparece mais em GET /monitorias/pendentes."""
        prof_id = make_user("Prof Fila", "prof.fila@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB305", "IA", prof_id)
        aluno_id = make_user("Aluno Fila", "aluno.fila@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        admin_client.post(f"/monitorias/{monitoria_id}/aprovar", follow_redirects=True)

        response = admin_client.get("/monitorias/pendentes")
        body = response.get_data(as_text=True)
        assert "aluno.fila@teste.com" not in body and "Aluno Fila" not in body

    def test_rejeitada_nao_aparece_em_pendentes(self, admin_client, make_user):
        """C3: Indicação rejeitada não aparece mais em GET /monitorias/pendentes."""
        prof_id = make_user("Prof Fila2", "prof.fila2@teste.com", "PROFESSOR")
        disc_id = _create_disciplina("MAB306", "Grafos", prof_id)
        aluno_id = make_user("Aluno Fila2", "aluno.fila2@teste.com", "ALUNO")
        monitoria_id = _create_indicacao_pendente(disc_id, prof_id, aluno_id)

        admin_client.post(
            f"/monitorias/{monitoria_id}/rejeitar",
            data={"motivo": "Teste"},
            follow_redirects=True,
        )

        response = admin_client.get("/monitorias/pendentes")
        body = response.get_data(as_text=True)
        assert "Aluno Fila2" not in body

    # -----------------------------------------------------------------------
    # C4 — Aluno já é monitor ativo
    # -----------------------------------------------------------------------

    def test_aprovar_aluno_ja_monitor_retorna_erro(self, admin_client, make_user):
        """C4: Aluno já com monitoria ATIVO em outra disciplina → flash de erro."""
        prof_id = make_user("Prof Dup", "prof.dup@teste.com", "PROFESSOR")
        disc1 = _create_disciplina("MAB307", "Comp Grafica", prof_id)
        disc2 = _create_disciplina("MAB308", "Visão Comp.", prof_id)
        aluno_id = make_user("Aluno Dup", "aluno.dup@teste.com", "ALUNO")

        # Cria e aprova a primeira indicação
        m1 = _create_indicacao_pendente(disc1, prof_id, aluno_id)
        admin_client.post(f"/monitorias/{m1}/aprovar", follow_redirects=True)

        # Segunda indicação para outra disciplina com o mesmo aluno
        m2 = _create_indicacao_pendente(disc2, prof_id, aluno_id)
        response = admin_client.post(
            f"/monitorias/{m2}/aprovar",
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "já possui monitoria ativa" in body.lower() or "ja possui monitoria ativa" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — ID inexistente
    # -----------------------------------------------------------------------

    def test_aprovar_id_inexistente_retorna_erro(self, admin_client):
        """C5: Tentar aprovar monitoria com ID que não existe → flash de erro."""
        response = admin_client.post(
            "/monitorias/999999/aprovar",
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não encontrada" in body.lower() or "nao encontrada" in body.lower()

    def test_rejeitar_id_inexistente_retorna_erro(self, admin_client):
        """C5: Tentar rejeitar monitoria com ID que não existe → flash de erro."""
        response = admin_client.post(
            "/monitorias/999999/rejeitar",
            data={"motivo": "Teste"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "não encontrada" in body.lower() or "nao encontrada" in body.lower()

    # -----------------------------------------------------------------------
    # Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_nao_pode_aprovar(self, client):
        """Segurança: sem sessão → redirecionado para login."""
        response = client.post("/monitorias/1/aprovar", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
