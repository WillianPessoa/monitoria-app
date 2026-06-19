"""
US06 — Admin cadastra disciplinas (UI Tests)

Cenários:
  C1  Dialog "Nova disciplina" abre ao clicar no botão
  C2  Cadastro bem-sucedido → flash de sucesso e disciplina na lista
  C3  Código duplicado → flash de erro exibido
  C4  Mobile: dialog abre e cadastro funciona

Nota: usa códigos únicos por execução para evitar conflito com dados existentes no Railway.

Rodar:
    pytest tests/ui/test_ui_us06_cadastrar_disciplinas.py -v --headed --slowmo=400
"""

import time

from tests.ui.conftest import BASE_URL

DISCIPLINAS_URL = f"{BASE_URL}/disciplinas/"


def unique_code(prefix="T"):
    """Gera código único (máx 8 chars) por execução."""
    return f"{prefix}{int(time.time() * 1000) % 100000}"


def _abrir_dialog(page):
    """Helper: abre o dialog de nova disciplina."""
    page.goto(DISCIPLINAS_URL)
    page.click("button:has-text('Nova disciplina')")
    page.locator("dialog#dlg-nova-disc").wait_for(state="visible")


def _preencher_e_submeter(page, codigo, nome):
    """Helper: preenche e submete o form de nova disciplina (usa o primeiro professor disponível)."""
    page.fill("dialog#dlg-nova-disc input#codigo", codigo)
    page.fill("dialog#dlg-nova-disc input#nome", nome)
    # Aguarda o select estar visível (options são "hidden" para Playwright — usa eval JS)
    page.locator("dialog#dlg-nova-disc select#professor_id").wait_for(state="visible")
    value = page.eval_on_selector(
        "dialog#dlg-nova-disc select#professor_id",
        "el => Array.from(el.options).find(o => !o.disabled && o.value)?.value",
    )
    assert value, "Nenhum professor ativo disponível no Railway"
    page.select_option("dialog#dlg-nova-disc select#professor_id", value=value)
    page.locator("dialog#dlg-nova-disc button[type='submit']").click()


# ===========================================================================
# Desktop (1280×800)
# ===========================================================================


class TestUS06CadastrarDisciplinasDesktop:

    # -----------------------------------------------------------------------
    # C1 — Dialog abre
    # -----------------------------------------------------------------------

    def test_dialog_nova_disciplina_abre(self, admin_desktop):
        """C1: Clicar em 'Nova disciplina' abre o dialog."""
        admin_desktop.goto(DISCIPLINAS_URL)
        admin_desktop.click("button:has-text('Nova disciplina')")

        dialog = admin_desktop.locator("dialog#dlg-nova-disc")
        dialog.wait_for(state="visible")
        assert dialog.is_visible()

    def test_dialog_contem_campos_codigo_nome_professor(self, admin_desktop):
        """C1: Dialog exibe campos de código, nome e professor."""
        _abrir_dialog(admin_desktop)

        assert admin_desktop.locator("dialog#dlg-nova-disc input#codigo").is_visible()
        assert admin_desktop.locator("dialog#dlg-nova-disc input#nome").is_visible()
        assert admin_desktop.locator("dialog#dlg-nova-disc select#professor_id").is_visible()

    # -----------------------------------------------------------------------
    # C2 — Cadastro bem-sucedido
    # -----------------------------------------------------------------------

    def test_cadastrar_disciplina_exibe_flash_sucesso(self, admin_desktop):
        """C2: Cadastro com dados válidos → flash de sucesso."""
        codigo = unique_code("DS")
        _abrir_dialog(admin_desktop)
        _preencher_e_submeter(admin_desktop, codigo, "Disciplina Sucesso Desktop")

        flash = admin_desktop.locator(".alert.success")
        flash.wait_for(state="visible")
        assert flash.is_visible()

    def test_disciplina_aparece_na_lista_apos_criacao(self, admin_desktop):
        """C2: Disciplina recém-criada aparece na listagem."""
        codigo = unique_code("DL")
        _abrir_dialog(admin_desktop)
        _preencher_e_submeter(admin_desktop, codigo, "Disciplina Lista Desktop")

        admin_desktop.wait_for_url(DISCIPLINAS_URL)
        # O código aparece nos cards de disciplina
        admin_desktop.locator(f"text={codigo[:4]}").first.wait_for(state="visible")
        assert admin_desktop.locator(f"text={codigo[:4]}").first.is_visible()

    # -----------------------------------------------------------------------
    # C3 — Código duplicado
    # -----------------------------------------------------------------------

    def test_codigo_duplicado_exibe_flash_de_erro(self, admin_desktop):
        """C3: Tentar cadastrar código já existente → flash de erro."""
        codigo = unique_code("DD")

        # Primeira criação
        _abrir_dialog(admin_desktop)
        _preencher_e_submeter(admin_desktop, codigo, "Disciplina Original")
        admin_desktop.locator(".alert.success").wait_for(state="visible")

        # Segunda criação com mesmo código
        _abrir_dialog(admin_desktop)
        _preencher_e_submeter(admin_desktop, codigo, "Disciplina Duplicada")

        flash_error = admin_desktop.locator(".alert.error")
        flash_error.wait_for(state="visible")
        assert flash_error.is_visible()
        assert "código" in flash_error.inner_text().lower() or "codigo" in flash_error.inner_text().lower()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS06CadastrarDisciplinasMobile:

    def test_botao_nova_disciplina_visivel_no_mobile(self, admin_mobile):
        """C1: Em mobile, botão 'Nova disciplina' está visível."""
        admin_mobile.goto(DISCIPLINAS_URL)
        assert admin_mobile.locator("button:has-text('Nova disciplina')").is_visible()

    def test_cadastro_completo_no_mobile(self, admin_mobile):
        """C2: Em mobile, o fluxo completo de cadastro funciona."""
        codigo = unique_code("DM")
        _abrir_dialog(admin_mobile)
        _preencher_e_submeter(admin_mobile, codigo, "Disciplina Mobile")

        flash = admin_mobile.locator(".alert.success")
        flash.wait_for(state="visible")
        assert flash.is_visible()
