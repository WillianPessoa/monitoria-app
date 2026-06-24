"""
US05 — Admin muda a senha do usuário manualmente (UI Tests)

Cenários de UI:
  C1  Botão "Resetar senha" está visível na lista de usuários
  C2  Clicar em "Resetar senha" → flash de sucesso com senha temporária
  C3  Status do usuário permanece "Pendente" após reset

Nota: o botão "Resetar senha" só aparece para usuários com status != INATIVO.
Usuários criados via form têm status PENDENTE por padrão — perfeito para os testes.

Rodar:
    pytest tests/ui/test_ui_us05_resetar_senha.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL, unique_email

USUARIOS_URL = f"{BASE_URL}/usuarios/"


def _criar_usuario(page, nome, email, papel="ALUNO"):
    """Helper: cria um usuário via dialog e aguarda o toast de sucesso."""
    page.click("button:has-text('Novo usuário')")
    page.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
    page.fill("dialog#dlg-novo-usuario input#nome", nome)
    page.fill("dialog#dlg-novo-usuario input#email", email)
    page.select_option("dialog#dlg-novo-usuario select#papel", papel)
    page.click("dialog#dlg-novo-usuario button[type='submit']")
    page.locator(".alert.success:has(strong)").wait_for(state="visible")
    page.locator(f".user-email:has-text('{email}')").wait_for(state="visible")


# ===========================================================================
# Desktop (1280×800)
# ===========================================================================


class TestUS05ResetarSenhaDesktop:

    # -----------------------------------------------------------------------
    # C1 — Botão visível
    # -----------------------------------------------------------------------

    def test_botao_resetar_senha_visivel_para_usuario_pendente(self, admin_desktop):
        """C1: Botão 'Resetar senha' visível para usuário com status Pendente."""
        email = unique_email("reset-vis-desktop")
        _criar_usuario(admin_desktop, "Usuário Reset Vis", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        assert user_row.locator("button:has-text('Resetar senha')").is_visible()

    # -----------------------------------------------------------------------
    # C2 — Flash com senha temporária
    # -----------------------------------------------------------------------

    def test_resetar_senha_exibe_flash_de_sucesso(self, admin_desktop):
        """C2: Clicar em 'Resetar senha' → flash de sucesso aparece."""
        email = unique_email("reset-flash-desktop")
        _criar_usuario(admin_desktop, "Usuário Reset Flash", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button:has-text('Resetar senha')").click()

        # Flash de sucesso com texto da senha redefinida
        flash = admin_desktop.locator(".alert.success")
        flash.wait_for(state="visible")
        assert flash.is_visible()

    def test_resetar_senha_flash_contem_senha_temporaria(self, admin_desktop):
        """C2: Flash exibe texto 'Nova senha temporária' com a nova senha."""
        email = unique_email("reset-senha-desktop")
        _criar_usuario(admin_desktop, "Usuário Reset Senha", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button:has-text('Resetar senha')").click()

        flash = admin_desktop.locator(".alert.success")
        flash.wait_for(state="visible")
        flash_text = flash.inner_text().lower()
        assert "temporária" in flash_text or "temporaria" in flash_text

    # -----------------------------------------------------------------------
    # C3 — Status permanece Pendente
    # -----------------------------------------------------------------------

    def test_usuario_permanece_pendente_apos_reset(self, admin_desktop):
        """C3: Após reset de senha, badge do usuário mostra 'Pendente'."""
        email = unique_email("reset-status-desktop")
        _criar_usuario(admin_desktop, "Usuário Reset Status", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button:has-text('Resetar senha')").click()

        # Aguarda página recarregar
        admin_desktop.wait_for_url(USUARIOS_URL)

        badge = admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill"
        )
        badge.wait_for(state="visible")
        assert "Pendente" in badge.inner_text()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS05ResetarSenhaMobile:

    def test_botao_resetar_senha_visivel_no_mobile(self, admin_mobile):
        """C1: Em mobile, o botão 'Resetar senha' está visível para usuários não inativos."""
        email = unique_email("reset-mobile")
        _criar_usuario(admin_mobile, "Usuário Reset Mobile", email)

        user_row = admin_mobile.locator(".user-row").filter(
            has=admin_mobile.locator(f".user-email:has-text('{email}')")
        )
        assert user_row.locator("button:has-text('Resetar senha')").is_visible()

    def test_resetar_senha_no_mobile_exibe_flash(self, admin_mobile):
        """C2: Em mobile, clicar em 'Resetar senha' exibe flash de sucesso."""
        email = unique_email("reset-flash-mobile")
        _criar_usuario(admin_mobile, "Usuário Flash Mobile", email)

        user_row = admin_mobile.locator(".user-row").filter(
            has=admin_mobile.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button:has-text('Resetar senha')").click()

        flash = admin_mobile.locator(".alert.success")
        flash.wait_for(state="visible")
        assert flash.is_visible()
