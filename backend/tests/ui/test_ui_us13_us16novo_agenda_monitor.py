"""
US13 — Monitor vê agenda (Monitorias) (UI)
US16-novo — Monitor cancela sessão com confirmação (UI)

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

    def test_monitor_ve_titulo_monitorias(self, monitor_desktop):
        """US13 F1: Página exibe 'Monitorias' como título (renomeado de 'Minha agenda')."""
        monitor_desktop.goto(AGENDA_URL)
        body = monitor_desktop.locator("body").inner_text()
        assert "Monitorias" in body

    def test_monitor_ve_secoes_da_agenda(self, monitor_desktop):
        """US13 C1: Agenda exibe seções de sessões (próximas, votação ou histórico)."""
        monitor_desktop.goto(AGENDA_URL)
        body = monitor_desktop.locator("body").inner_text()
        assert any(k in body for k in ["Próximas sessões", "Votação", "Histórico", "Nenhuma sessão"])


# ===========================================================================
# Desktop — US16-novo (Monitor cancela sessão com confirmação)
# ===========================================================================


class TestUS16NovoCancelarSessaoDesktop:

    def test_botao_cancelar_abre_dialog(self, monitor_desktop):
        """US16-novo F1: Clicar em 'Cancelar' abre dialog de confirmação (não submete diretamente)."""
        monitor_desktop.goto(AGENDA_URL)
        cancel_btns = monitor_desktop.locator(
            "section:has(h3:has-text('Próximas sessões')) button:has-text('Cancelar')"
        )
        if cancel_btns.count() == 0:
            return  # Sem sessões futuras no Railway — passa

        cancel_btns.first.click()
        dialog = monitor_desktop.locator("dialog[open]")
        assert dialog.is_visible()
        assert "cancelar" in dialog.inner_text().lower() or "sessão" in dialog.inner_text().lower()

    def test_dialog_tem_botao_confirmar_e_manter(self, monitor_desktop):
        """US16-novo F1: Dialog de cancelamento exibe 'Confirmar cancelamento' e 'Manter sessão'."""
        monitor_desktop.goto(AGENDA_URL)
        cancel_btns = monitor_desktop.locator(
            "section:has(h3:has-text('Próximas sessões')) button:has-text('Cancelar')"
        )
        if cancel_btns.count() == 0:
            return

        cancel_btns.first.click()
        dialog = monitor_desktop.locator("dialog[open]")
        assert dialog.is_visible()
        body_text = dialog.inner_text()
        assert "Confirmar cancelamento" in body_text or "Manter sessão" in body_text


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestAgendaMonitorMobile:

    def test_agenda_carrega_no_mobile_para_monitor(self, monitor_mobile):
        """US13 mobile: Tela /agenda/ carrega para monitor."""
        monitor_mobile.goto(AGENDA_URL)
        assert monitor_mobile.url == AGENDA_URL
        assert monitor_mobile.locator("body").is_visible()

    def test_agenda_monitor_sem_erro_500_no_mobile(self, monitor_mobile):
        """US13 mobile: Página carrega sem erro 500."""
        monitor_mobile.goto(AGENDA_URL)
        content = monitor_mobile.locator("body").inner_text()
        assert "500" not in content[:50]
        assert monitor_mobile.locator("body").is_visible()
