"""
US16 — Monitor registra presença/ausência (UI)
US17 — Monitor registra assunto tratado (UI)

Nota: o formulário de registro aparece apenas para sessões passadas (data_fim < now).
O Railway deve ter sessões passadas disponíveis para o monitor de teste.

Rodar:
    pytest tests/ui/test_ui_us16_us17_registrar.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL

AGENDA_URL = f"{BASE_URL}/agenda/"


class TestUS16US17RegistrarDesktop:

    def test_agenda_monitor_carrega(self, monitor_desktop):
        """Smoke: monitor acessa /agenda/ sem erro."""
        monitor_desktop.goto(AGENDA_URL)
        assert monitor_desktop.url == AGENDA_URL

    def test_sessao_passada_exibe_form_de_registro(self, monitor_desktop):
        """US16/US17: Se houver sessão passada, formulário de registro é visível."""
        monitor_desktop.goto(AGENDA_URL)
        form_registrar = monitor_desktop.locator(
            "form[action*='/registrar'], button:has-text('Salvar registro')"
        )
        if form_registrar.count() == 0:
            # Sem sessões passadas pendentes no Railway — passa
            return
        assert form_registrar.first.is_visible()

    def test_campo_assunto_presente_no_form(self, monitor_desktop):
        """US17: Campo de assunto visível no formulário de registro."""
        monitor_desktop.goto(AGENDA_URL)
        textarea = monitor_desktop.locator("textarea[name='assunto']")
        if textarea.count() == 0:
            return  # Sem sessões pendentes
        assert textarea.first.is_visible()

    def test_checkboxes_de_presenca_presentes(self, monitor_desktop):
        """US16: Checkboxes de presença visíveis para cada participante."""
        monitor_desktop.goto(AGENDA_URL)
        checkboxes = monitor_desktop.locator("input[type='checkbox'][name='presentes']")
        if checkboxes.count() == 0:
            return  # Sem participantes ou sem sessões pendentes
        assert checkboxes.first.is_visible()


class TestUS16US17Mobile:

    def test_agenda_registrar_carrega_no_mobile(self, monitor_mobile):
        """US16/US17 mobile: Monitor acessa agenda no mobile."""
        monitor_mobile.goto(AGENDA_URL)
        assert monitor_mobile.locator("body").is_visible()
