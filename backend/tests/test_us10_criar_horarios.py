"""
US10 — Monitor cria horários de atendimento

Rota: POST /agenda/slots/create
Campos do form: data_inicio (ISO datetime), duracao (minutos int), local (opcional)

Critérios de aceitação:

  C1  Criação bem-sucedida
      Given: monitor com monitoria ativa na sua agenda
      When:  informa data/hora futura, duração e local válidos
      Then:  bloco aparece na agenda como disponível (flash de sucesso)

  C2  Horários sobrepostos
      Given: monitor já tem slot das 14h às 16h
      When:  tenta criar outro das 15h às 17h na mesma data
      Then:  sistema rejeita com mensagem de sobreposição

  C3  Data no passado
      Given: monitor tenta criar com data anterior ao dia atual
      When:  submete o formulário
      Then:  sistema rejeita com mensagem de data inválida

Cenários extras:
  C4  Usuário sem monitoria ativa → rejeitado
  C5  Duração inválida (0) → rejeitado
  C6  Data/hora malformada → rejeitado
  C7  Não autenticado → redireciona para login
  C8  Slot com local omitido (campo opcional) → aceito
"""

import datetime

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future(hours=24):
    return datetime.datetime.now() + datetime.timedelta(hours=hours)


def _past(hours=1):
    return datetime.datetime.now() - datetime.timedelta(hours=hours)


def _create_slot_db(monitor_id, disc_id, data_inicio, duracao_min, local=None):
    """Cria disponibilidade diretamente no banco, sem passar pela rota."""
    data_fim = data_inicio + datetime.timedelta(minutes=duracao_min)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
        VALUES (%s, %s, %s, %s, %s, 'DISPONIVEL')
        """,
        (disc_id, monitor_id, data_inicio, data_fim, local),
    )
    conn.commit()
    slot_id = cur.lastrowid
    cur.close()
    conn.close()
    return slot_id


def _count_slots(monitor_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM disponibilidades WHERE monitor_id = %s AND status = 'DISPONIVEL'",
        (monitor_id,),
    )
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestUS10CriarHorarios:

    # -----------------------------------------------------------------------
    # C1 — Criação bem-sucedida
    # -----------------------------------------------------------------------

    def test_criar_slot_retorna_flash_sucesso(self, client, make_monitoria_ativa):
        """C1: Monitor com monitoria ativa cria slot futuro → flash de sucesso."""
        setup = make_monitoria_ativa("us10c1")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _future(24).isoformat(timespec="minutes"),
                "duracao": "60",
                "local": "Sala 101",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "criado com sucesso" in body.lower() or "disponível criado" in body.lower()

    def test_criar_slot_persiste_no_banco(self, client, make_monitoria_ativa):
        """C1: Slot criado via rota aparece em disponibilidades com status DISPONIVEL."""
        setup = make_monitoria_ativa("us10c1b")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _future(48).isoformat(timespec="minutes"),
                "duracao": "90",
                "local": "Lab 2",
            },
            follow_redirects=True,
        )
        assert _count_slots(setup["aluno_id"]) == 1

    def test_criar_slot_sem_local_aceito(self, client, make_monitoria_ativa):
        """C8: Campo local é opcional — slot sem local deve ser aceito."""
        setup = make_monitoria_ativa("us10c8")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _future(72).isoformat(timespec="minutes"),
                "duracao": "60",
                "local": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "criado com sucesso" in body.lower() or "disponível criado" in body.lower()

    # -----------------------------------------------------------------------
    # C2 — Sobreposição de horários
    # -----------------------------------------------------------------------

    def test_criar_slot_sobreposto_rejeitado(self, client, make_monitoria_ativa):
        """C2: Monitor tenta criar slot que sobrepõe com existente → flash de erro."""
        setup = make_monitoria_ativa("us10c2")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        base = (_future(24)).replace(hour=14, minute=0, second=0, microsecond=0)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], base, 120)  # 14h–16h

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": base.replace(hour=15).isoformat(timespec="minutes"),  # 15h–17h
                "duracao": "120",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "sobrepõe" in body.lower() or "sobreposição" in body.lower() or "sobrepos" in body.lower()

    def test_criar_slot_adjacente_aceito(self, client, make_monitoria_ativa):
        """C2 (negativo): Slot adjacente (começa exatamente quando o anterior termina) é aceito."""
        setup = make_monitoria_ativa("us10c2b")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        base = (_future(24)).replace(hour=14, minute=0, second=0, microsecond=0)
        _create_slot_db(setup["aluno_id"], setup["disc_id"], base, 60)  # 14h–15h

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": base.replace(hour=15).isoformat(timespec="minutes"),  # 15h–16h
                "duracao": "60",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "criado com sucesso" in body.lower() or "disponível criado" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Data no passado
    # -----------------------------------------------------------------------

    def test_criar_slot_data_passada_rejeitado(self, client, make_monitoria_ativa):
        """C3: Monitor tenta criar slot com data no passado → flash de data inválida."""
        setup = make_monitoria_ativa("us10c3")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _past(2).isoformat(timespec="minutes"),
                "duracao": "60",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "futuro" in body.lower() or "passado" in body.lower() or "data" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Sem monitoria ativa
    # -----------------------------------------------------------------------

    def test_criar_slot_sem_monitoria_ativa_rejeitado(self, aluno_client):
        """C4: Aluno sem monitoria ativa tenta criar slot → flash de erro."""
        response = aluno_client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _future(24).isoformat(timespec="minutes"),
                "duracao": "60",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "monitoria" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Duração inválida
    # -----------------------------------------------------------------------

    def test_criar_slot_duracao_zero_rejeitado(self, client, make_monitoria_ativa):
        """C5: Duração zero → flash de duração inválida."""
        setup = make_monitoria_ativa("us10c5")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": _future(24).isoformat(timespec="minutes"),
                "duracao": "0",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "duração" in body.lower() or "duracao" in body.lower() or "inválida" in body.lower()

    # -----------------------------------------------------------------------
    # C6 — Data malformada
    # -----------------------------------------------------------------------

    def test_criar_slot_data_invalida_rejeitado(self, client, make_monitoria_ativa):
        """C6: Data/hora malformada → flash de data inválida."""
        setup = make_monitoria_ativa("us10c6")
        client.post("/auth/login", data={"email": setup["monitor_email"], "senha": setup["monitor_senha"]})

        response = client.post(
            "/agenda/slots/create",
            data={
                "data_inicio": "nao-e-uma-data",
                "duracao": "60",
                "local": "",
            },
            follow_redirects=True,
        )
        body = response.get_data(as_text=True)
        assert "inválida" in body.lower() or "invalida" in body.lower() or "data" in body.lower()

    # -----------------------------------------------------------------------
    # C7 — Proteção de acesso
    # -----------------------------------------------------------------------

    def test_nao_autenticado_redireciona_para_login(self, client):
        """C7: Sem sessão ativa → redireciona para login (302)."""
        response = client.post("/agenda/slots/create", follow_redirects=False)
        assert response.status_code == 302
        assert "login" in response.location
