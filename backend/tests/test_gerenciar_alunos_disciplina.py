"""
Gerenciamento de alunos em disciplina — Admin matricula e remove alunos

Rotas:
  GET  /disciplinas/                       — index (link para detalhe de cada disciplina)
  GET  /disciplinas/<id>/alunos            — lista alunos matriculados
  POST /disciplinas/<id>/alunos/adicionar  — adiciona alunos por e-mail (bulk)
  POST /disciplinas/<id>/alunos/remover    — remove alunos selecionados (bulk)

Bug registrado: BUG-05
  Em /disciplinas/, o disc-card não tinha link para o detalhe da disciplina.
  Sem esse link, o admin não conseguia navegar até "Ver alunos" para matricular
  alunos. A correção foi transformar o disc-card-name em um <a> para o detalhe.

Cenários:
  C1  GET /disciplinas/ contém link para detalhe de cada disciplina (regressão BUG-05)
  C2  Admin adiciona aluno por e-mail válido → sucesso, registro em disciplina_alunos
  C3  E-mail não cadastrado no sistema → flash de erro listando e-mail faltante
  C4  Textarea vazia → flash "Nenhum e-mail válido informado"
  C5  Aluno que já é monitor desta disciplina → flash de erro
  C6  Admin remove aluno selecionado → sucesso, removido de disciplina_alunos
  C7  Remover sem selecionar nenhum aluno → flash de erro
  C8  Não-admin tenta POST /alunos/adicionar → redirecionado (sem permissão)
"""

from db.connection import get_connection


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


def _is_enrolled(disc_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM disciplina_alunos WHERE disciplina_id=%s AND aluno_id=%s",
        (disc_id, aluno_id),
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0


class TestGerenciarAlunosDisciplina:

    # -----------------------------------------------------------------------
    # C1 — Regressão BUG-05: index contém link para detalhe
    # -----------------------------------------------------------------------

    def test_index_contem_link_para_detalhe(self, admin_client, make_monitoria_ativa):
        """C1 (BUG-05): GET /disciplinas/ deve conter href para /disciplinas/<id>."""
        setup = make_monitoria_ativa("ga01")

        response = admin_client.get("/disciplinas/")
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert f"/disciplinas/{setup['disc_id']}" in body

    # -----------------------------------------------------------------------
    # C2 — Adicionar aluno por e-mail válido
    # -----------------------------------------------------------------------

    def test_adicionar_aluno_por_email_valido(self, admin_client, make_user, make_monitoria_ativa):
        """C2: Admin envia e-mail de aluno ativo → aluno matriculado na disciplina."""
        setup = make_monitoria_ativa("ga02")
        aluno_id = make_user("Aluno Add", "aluno.ga02@teste.com", "ALUNO")

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/adicionar",
            data={"alunos_emails": "aluno.ga02@teste.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "adicionado" in body.lower()
        assert _is_enrolled(setup["disc_id"], aluno_id)

    # -----------------------------------------------------------------------
    # C3 — E-mail não cadastrado
    # -----------------------------------------------------------------------

    def test_email_nao_cadastrado_retorna_erro(self, admin_client, make_monitoria_ativa):
        """C3: E-mail inexistente no sistema → flash de erro listando o e-mail."""
        setup = make_monitoria_ativa("ga03")

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/adicionar",
            data={"alunos_emails": "naoexiste.ga03@teste.com"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "não encontrado" in body.lower() or "nao encontrado" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Textarea vazia
    # -----------------------------------------------------------------------

    def test_textarea_vazia_retorna_erro(self, admin_client, make_monitoria_ativa):
        """C4: Nenhum e-mail informado → flash "Nenhum e-mail válido informado"."""
        setup = make_monitoria_ativa("ga04")

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/adicionar",
            data={"alunos_emails": "   "},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "válido" in body.lower() or "valido" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Aluno que já é monitor desta disciplina
    # -----------------------------------------------------------------------

    def test_monitor_da_disciplina_nao_pode_ser_matriculado(
        self, admin_client, make_monitoria_ativa
    ):
        """C5: Tentar matricular o monitor-aluno desta disciplina → flash de erro."""
        setup = make_monitoria_ativa("ga05")

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT email FROM usuarios WHERE id = %s", (setup["aluno_id"],))
        email = cur.fetchone()["email"]
        cur.close()
        conn.close()

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/adicionar",
            data={"alunos_emails": email},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "monitor" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Remover aluno selecionado
    # -----------------------------------------------------------------------

    def test_remover_aluno_selecionado_com_sucesso(
        self, admin_client, make_user, make_monitoria_ativa
    ):
        """C6: Admin remove aluno matriculado → removido de disciplina_alunos."""
        setup = make_monitoria_ativa("ga06")
        aluno_id = make_user("Aluno Rem", "aluno.ga06@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/remover",
            data={"alunos_ids": [str(aluno_id)]},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "removido" in body.lower()
        assert not _is_enrolled(setup["disc_id"], aluno_id)

    # -----------------------------------------------------------------------
    # C7 — Remover sem selecionar nenhum aluno
    # -----------------------------------------------------------------------

    def test_remover_sem_selecionar_retorna_erro(self, admin_client, make_monitoria_ativa):
        """C7: POST remover sem alunos_ids → flash pedindo seleção."""
        setup = make_monitoria_ativa("ga07")

        response = admin_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/remover",
            data={},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "selecione" in body.lower() or "ao menos" in body.lower()

    # -----------------------------------------------------------------------
    # C8 — Segurança: não-admin não pode adicionar
    # -----------------------------------------------------------------------

    def test_nao_admin_nao_pode_adicionar_aluno(
        self, aluno_client, make_monitoria_ativa
    ):
        """C8: Aluno comum tenta POST /alunos/adicionar → redirecionado sem permissão."""
        setup = make_monitoria_ativa("ga08")

        response = aluno_client.post(
            f"/disciplinas/{setup['disc_id']}/alunos/adicionar",
            data={"alunos_emails": "qualquer@teste.com"},
            follow_redirects=False,
        )
        assert response.status_code == 302
