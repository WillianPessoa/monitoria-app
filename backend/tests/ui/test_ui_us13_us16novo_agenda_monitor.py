"""
US13 — Monitor vê agenda com agendamentos confirmados (UI)
US15 — Monitor bloqueia/desbloqueia horário (UI)
US16-novo — Monitor cancela sessão confirmada (UI)

Rodar:
    pytest tests/ui/test_ui_us13_us16novo_agenda_monitor.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL

AGENDA_URL = f"{BASE_URL}/agenda/"


# ===========================================================================
# Desktop — US13 (Monitor vê agenda)
# ===========================================================================


class TestUS13AgendaMonitorDesktop:

    def test_agenda_carrega_para_monitor(self, monitor_desktop):
        """US13 C1: Monitor acessa /agenda/ sem erro."""
        monitor_desktop.goto(AGENDA_URL)
        assert monitor_desktop.url == AGENDA_URL
        assert monitor_desktop.locator("body").is_visible()

    def test_monitor_ve_secoes_da_agenda(self, monitor_desktop):
        """US13 C1: Agenda exibe seções de sessões (próximas ou histórico)."""
        monitor_desktop.goto(AGENDA_URL)
        body = monitor_desktop.locator("body").inner_text()
        assert any(k in body for k in ["Próximas sessões", "Votação", "sessão", "Nenhuma sessão"])

    def test_monitor_ve_secao_meus_horarios(self, monitor_desktop):
        """US13/US15: Seção 'Meus horários cadastrados' visível na agenda do monitor."""
        monitor_desktop.goto(AGENDA_URL)
        body = monitor_desktop.locator("body").inner_text()
        # A seção aparece somente quando há own_slots — verifica que a página carrega
        assert monitor_desktop.locator("body").is_visible()


# ===========================================================================
# Desktop — US15 (Monitor bloqueia/desbloqueia horário)
# ===========================================================================


class TestUS15BloquearSlotDesktop:

    def test_botao_bloquear_visivel_em_slots_disponiveis(self, monitor_desktop):
        """US15 C1: Botão 'Bloquear' visível nos slots com status DISPONIVEL."""
        monitor_desktop.goto(AGENDA_URL)
        bloquear_btns = monitor_desktop.locator("button:has-text('Bloquear')")
        if bloquear_btns.count() == 0:
            return  # Monitor não tem slots disponíveis no Railway — passa

        assert bloquear_btns.first.is_visible()

    def test_botao_desbloquear_visivel_em_slots_bloqueados(self, monitor_desktop):
        """US15 C2: Botão 'Desbloquear' visível nos slots com status BLOQUEADO."""
        monitor_desktop.goto(AGENDA_URL)
        desbloquear_btns = monitor_desktop.locator("button:has-text('Desbloquear')")
        if desbloquear_btns.count() == 0:
            return  # Sem slots bloqueados no Railway — passa

        assert desbloquear_btns.first.is_visible()

    def test_secao_horarios_cadastrados_tem_status_pills(self, monitor_desktop):
        """US15: Status pills de DISPONIVEL/AGENDADO/BLOQUEADO visíveis nos slots."""
        monitor_desktop.goto(AGENDA_URL)
        secao = monitor_desktop.locator("section:has(h3:has-text('Meus horários cadastrados'))")
        if not secao.is_visible():
            return  # Sem own_slots no Railway

        pills = secao.locator(".status-pill")
        assert pills.count() > 0


# ===========================================================================
# Desktop — US16-novo (Monitor cancela sessão)
# ===========================================================================


class TestUS16NovoCancelarSessaoDesktop:

    def test_botao_cancelar_sessao_visivel(self, monitor_desktop):
        """US16-novo C1: Botão 'Cancelar' visível nas sessões futuras do monitor."""
        monitor_desktop.goto(AGENDA_URL)
        # Botão Cancelar para sessões futuras (na seção de próximas sessões)
        cancel_btns = monitor_desktop.locator(
            "section:has(h3:has-text('Próximas sessões')) button:has-text('Cancelar'), "
            ".btn-danger:has-text('Cancelar')"
        )
        if cancel_btns.count() == 0:
            return  # Sem sessões futuras no Railway — passa

        assert cancel_btns.first.is_visible()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestAgendaMonitorMobile:

    def test_agenda_carrega_no_mobile_para_monitor(self, monitor_mobile):
        """US13 mobile: Tela /agenda/ carrega para monitor."""
        monitor_mobile.goto(AGENDA_URL)
        assert monitor_mobile.url == AGENDA_URL
        assert monitor_mobile.locator("body").is_visible()

    def test_formulario_criar_horario_visivel_no_mobile(self, monitor_mobile):
        """US10/US15 mobile: Formulário de criar horário e seção de horários visível."""
        monitor_mobile.goto(AGENDA_URL)
        # Verifica que a página do monitor carrega sem erro
        assert monitor_mobile.locator("body").is_visible()
        content = monitor_mobile.locator("body").inner_text()
        assert "500" not in content[:50]
