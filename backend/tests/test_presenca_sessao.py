"""
Presença em sessão de monitoria — Aluno confirma e cancela presença

Rotas:
  POST /disciplinas/<int:disciplina_id>/presenca   — atualiza status de presença
  POST /disciplinas/<int:disciplina_id>/cancelar   — cancela presença confirmada

Regras de negócio (presenca):
  - Apenas alunos matriculados na disciplina podem confirmar/atualizar
  - A sessão precisa ser futura (ainda não começou)
  - status deve ser CONFIRMADA ou AUSENTE

Regras de negócio (cancelar):
  - Precisa ter mais de 6 horas de antecedência
  - Apenas presenças com status CONFIRMADA podem ser canceladas

Cenários:
  C1  Aluno confirma presença em sessão futura → sucesso, status CONFIRMADA no banco
  C2  Aluno confirma ausência em sessão futura → sucesso, status AUSENTE no banco
  C3  Aluno não matriculado → permissão negada
  C4  Sessão já começou → "A sessão já começou"
  C5  Sessão de outra disciplina → "Sessão não encontrada"
  C6  Aluno cancela presença confirmada (> 6h) → "Ausência confirmada", status → AUSENTE
  C7  Cancelar presença com < 6h de antecedência → flash de erro, status permanece CONFIRMADA
  C8  Cancelar sem presença confirmada → "Somente presenças confirmadas"
"""

import datetime

from db.connection import get_connection
from utils.time import now_sp_naive


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


def _create_sessao(disc_id, monitor_id, horas_futuras=8):
    """Cria sessão relativa a now. horas_futuras < 0 → sessão já começou."""
    now = now_sp_naive()
    data_inicio = now + datetime.timedelta(hours=horas_futuras)
    data_fim = data_inicio + datetime.timedelta(hours=1)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status)
        VALUES (%s, %s, %s, %s, 'AGENDADA')
        """,
        (disc_id, monitor_id, data_inicio, data_fim),
    )
    conn.commit()
    sessao_id = cur.lastrowid
    cur.close()
    conn.close()
    return sessao_id


def _set_presenca(sessao_id, aluno_id, status="CONFIRMADA"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO presencas (sessao_id, aluno_id, status)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """,
        (sessao_id, aluno_id, status),
    )
    conn.commit()
    cur.close()
    conn.close()


def _get_presenca(sessao_id, aluno_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT status FROM presencas WHERE sessao_id = %s AND aluno_id = %s",
        (sessao_id, aluno_id),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


class TestPresencaSessao:

    # -----------------------------------------------------------------------
    # C1 — Aluno confirma presença
    # -----------------------------------------------------------------------

    def test_aluno_confirma_presenca_com_sucesso(self, client, make_user, make_monitoria_ativa):
        """C1: Aluno matriculado confirma CONFIRMADA em sessão futura → sucesso e banco."""
        setup = make_monitoria_ativa("ps1")
        aluno_id = make_user("Aluno Presença", "aluno.ps1@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"])

        client.post("/auth/login", data={"email": "aluno.ps1@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "atualizado" in response.get_data(as_text=True).lower()
        assert _get_presenca(sessao_id, aluno_id)["status"] == "CONFIRMADA"

    # -----------------------------------------------------------------------
    # C2 — Aluno confirma ausência
    # -----------------------------------------------------------------------

    def test_aluno_confirma_ausencia_com_sucesso(self, client, make_user, make_monitoria_ativa):
        """C2: Aluno matriculado confirma AUSENTE em sessão futura → sucesso e banco."""
        setup = make_monitoria_ativa("ps2")
        aluno_id = make_user("Aluno Ausente", "aluno.ps2@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"])

        client.post("/auth/login", data={"email": "aluno.ps2@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "AUSENTE"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "atualizado" in response.get_data(as_text=True).lower()
        assert _get_presenca(sessao_id, aluno_id)["status"] == "AUSENTE"

    # -----------------------------------------------------------------------
    # C3 — Aluno não matriculado
    # -----------------------------------------------------------------------

    def test_aluno_nao_matriculado_nao_pode_confirmar(self, client, make_user, make_monitoria_ativa):
        """C3: Aluno sem disciplina_alunos → permissão negada."""
        setup = make_monitoria_ativa("ps3")
        aluno_id = make_user("Aluno Externo", "aluno.ps3@teste.com", "ALUNO")
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"])

        client.post("/auth/login", data={"email": "aluno.ps3@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "permissão" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Sessão já começou
    # -----------------------------------------------------------------------

    def test_sessao_ja_comecou_retorna_erro(self, client, make_user, make_monitoria_ativa):
        """C4: Sessão com data_inicio no passado → "A sessão já começou"."""
        setup = make_monitoria_ativa("ps4")
        aluno_id = make_user("Aluno Tarde", "aluno.ps4@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], horas_futuras=-1)

        client.post("/auth/login", data={"email": "aluno.ps4@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "já começou" in body.lower() or "ja comecou" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Sessão de outra disciplina
    # -----------------------------------------------------------------------

    def test_sessao_outra_disciplina_retorna_nao_encontrada(self, client, make_user, make_monitoria_ativa):
        """C5: sessao_id pertence à disciplina B, POST vai para disciplina A → não encontrada."""
        setup_a = make_monitoria_ativa("ps5a")
        setup_b = make_monitoria_ativa("ps5b")
        aluno_id = make_user("Aluno Cross", "aluno.ps5@teste.com", "ALUNO")
        _enroll_aluno(setup_a["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup_b["disc_id"], setup_b["aluno_id"])

        client.post("/auth/login", data={"email": "aluno.ps5@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup_a['disc_id']}/presenca",
            data={"sessao_id": sessao_id, "status": "CONFIRMADA"},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "não encontrada" in body.lower() or "nao encontrada" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Cancelar presença confirmada (> 6h)
    # -----------------------------------------------------------------------

    def test_cancelar_presenca_confirmada_com_sucesso(self, client, make_user, make_monitoria_ativa):
        """C6: Aluno com presença CONFIRMADA cancela > 6h antes → "Ausência confirmada"."""
        setup = make_monitoria_ativa("ps6")
        aluno_id = make_user("Aluno Cancela", "aluno.ps6@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], horas_futuras=8)
        _set_presenca(sessao_id, aluno_id, "CONFIRMADA")

        client.post("/auth/login", data={"email": "aluno.ps6@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/cancelar",
            data={"sessao_id": sessao_id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "ausência confirmada" in body.lower() or "ausencia confirmada" in body.lower()
        assert _get_presenca(sessao_id, aluno_id)["status"] == "AUSENTE"

    # -----------------------------------------------------------------------
    # C7 — Cancelar com < 6h
    # -----------------------------------------------------------------------

    def test_cancelar_presenca_menos_6h_retorna_erro(self, client, make_user, make_monitoria_ativa):
        """C7: Sessão em 3h → cancelamento não permitido, presença permanece CONFIRMADA."""
        setup = make_monitoria_ativa("ps7")
        aluno_id = make_user("Aluno Urgente", "aluno.ps7@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], horas_futuras=3)
        _set_presenca(sessao_id, aluno_id, "CONFIRMADA")

        client.post("/auth/login", data={"email": "aluno.ps7@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/cancelar",
            data={"sessao_id": sessao_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "6 horas" in body or "antecedência" in body.lower() or "não permitido" in body.lower()
        assert _get_presenca(sessao_id, aluno_id)["status"] == "CONFIRMADA"

    # -----------------------------------------------------------------------
    # C8 — Cancelar sem presença confirmada
    # -----------------------------------------------------------------------

    def test_cancelar_sem_presenca_confirmada_retorna_erro(self, client, make_user, make_monitoria_ativa):
        """C8: Aluno sem presença CONFIRMADA tenta cancelar → flash de erro."""
        setup = make_monitoria_ativa("ps8")
        aluno_id = make_user("Aluno Sem Pres", "aluno.ps8@teste.com", "ALUNO")
        _enroll_aluno(setup["disc_id"], aluno_id)
        sessao_id = _create_sessao(setup["disc_id"], setup["aluno_id"], horas_futuras=8)
        # Não cria nenhuma presença

        client.post("/auth/login", data={"email": "aluno.ps8@teste.com", "senha": "Senha@Teste1"})
        response = client.post(
            f"/disciplinas/{setup['disc_id']}/cancelar",
            data={"sessao_id": sessao_id},
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "confirmadas" in body.lower() or "somente" in body.lower()
