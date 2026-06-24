"""
US03 — Monitor edita perfil (contato e disponibilidade)

Rota:   GET/POST /usuarios/meu-perfil
Acesso: papel=MONITOR ou aluno com monitoria ativa

ATENÇÃO: US03 não tem critérios BDD definidos em criterios-de-aceitacao.md.
Os cenários abaixo foram derivados do comportamento da rota e do service.

Cenários derivados do código:
  C1  Monitor acessa a página de perfil com sucesso
  C2  Monitor atualiza contato com email válido → sucesso
  C3  Monitor atualiza contato com celular BR válido → sucesso
  C4  Monitor atualiza contato com valor inválido → rejeitado
  C5  Usuário sem papel de monitor não pode acessar a página

Validações do service (usuarios/service.py):
  email válido:   regex ^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$
  celular válido: regex ^\\(\\d{2}\\) \\d{5}-\\d{4}$
  contato vazio:  aceito (limpa o contato)
"""


class TestUS03EditarPerfil:

    # -----------------------------------------------------------------------
    # C1 — Acesso à página
    # -----------------------------------------------------------------------

    def test_monitor_acessa_pagina_de_perfil(self, monitor_client):
        """C1: Monitor autenticado consegue acessar GET /usuarios/meu-perfil."""
        response = monitor_client.get("/usuarios/meu-perfil")
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "perfil" in body.lower()

    def test_pagina_tem_campos_de_contato(self, monitor_client):
        """C1: Página de perfil contém os campos de contato e carga horária."""
        response = monitor_client.get("/usuarios/meu-perfil")
        body = response.get_data(as_text=True)
        assert 'name="contato_tipo"' in body
        assert 'name="contato_valor"' in body
        assert 'name="carga_horaria"' in body

    # -----------------------------------------------------------------------
    # C2 — Atualização com email válido
    # -----------------------------------------------------------------------

    def test_atualiza_contato_email_valido(self, monitor_client):
        """C2: Monitor envia email válido como contato → perfil atualizado."""
        response = monitor_client.post(
            "/usuarios/meu-perfil",
            data={
                "contato_tipo": "email",
                "contato_valor": "monitor.contato@email.com",
                "carga_horaria": "1",
                "modo_2h": "CONSECUTIVAS",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "atualizado com sucesso" in body.lower()

    # -----------------------------------------------------------------------
    # C3 — Atualização com celular BR válido
    # -----------------------------------------------------------------------

    def test_atualiza_contato_celular_valido(self, monitor_client):
        """C3: Monitor envia celular no formato BR → perfil atualizado."""
        response = monitor_client.post(
            "/usuarios/meu-perfil",
            data={
                "contato_tipo": "celular",
                "contato_valor": "(21) 99999-8888",
                "carga_horaria": "1",
                "modo_2h": "CONSECUTIVAS",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "atualizado com sucesso" in body.lower()

    def test_atualiza_contato_vazio_aceito(self, monitor_client):
        """C3: Contato vazio é aceito — limpa o contato anterior."""
        response = monitor_client.post(
            "/usuarios/meu-perfil",
            data={
                "contato_tipo": "",
                "contato_valor": "",
                "carga_horaria": "1",
                "modo_2h": "CONSECUTIVAS",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "atualizado com sucesso" in body.lower()

    # -----------------------------------------------------------------------
    # C4 — Contato inválido rejeitado
    # -----------------------------------------------------------------------

    def test_email_invalido_rejeitado(self, monitor_client):
        """C4: Email sem @ → rejeitado com mensagem de contato inválido."""
        response = monitor_client.post(
            "/usuarios/meu-perfil",
            data={
                "contato_tipo": "email",
                "contato_valor": "nao-e-um-email",
                "carga_horaria": "1",
                "modo_2h": "CONSECUTIVAS",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "inv" in body.lower()  # "inválido" ou "invalido"

    def test_celular_fora_do_formato_rejeitado(self, monitor_client):
        """C4: Celular sem DDD entre parênteses → rejeitado."""
        response = monitor_client.post(
            "/usuarios/meu-perfil",
            data={
                "contato_tipo": "celular",
                "contato_valor": "21999998888",
                "carga_horaria": "1",
                "modo_2h": "CONSECUTIVAS",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "inv" in body.lower()

    # -----------------------------------------------------------------------
    # C5 — Acesso negado para não-monitor
    # -----------------------------------------------------------------------

    def test_aluno_sem_monitoria_nao_acessa_perfil(self, aluno_client):
        """C5: Aluno comum (sem monitoria ativa) é redirecionado ao tentar acessar."""
        response = aluno_client.get(
            "/usuarios/meu-perfil",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/" in response.location

    def test_nao_autenticado_redirecionado_para_login(self, client):
        """C5: Requisição sem sessão ativa → redirecionado para login."""
        response = client.get(
            "/usuarios/meu-perfil",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "login" in response.location
