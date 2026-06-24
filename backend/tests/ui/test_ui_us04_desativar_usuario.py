"""
US04 — Desativar e Reativar Usuário UI Tests (Desktop + Mobile)

Cenários:
  C1  Botão "Desativar" abre dialog de confirmação
  C2  Confirmar desativação → badge "Inativo" aparece na lista
  C3  Botão "Reativar" aparece para usuários inativos e funciona
  C4  Admin não vê opção de desativar a si mesmo (ou é bloqueado)

Nota: cada teste cria um usuário único para evitar dependência de estado.

Rodar:
    pytest tests/ui/test_ui_us04_desativar_usuario.py -v --headed --slowmo=400
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


class TestUS04DesativarUsuarioDesktop:

    # -----------------------------------------------------------------------
    # C1 — Dialog de confirmação abre
    # -----------------------------------------------------------------------

    def test_botao_desativar_abre_dialog(self, admin_desktop):
        """C1: Clicar em 'Desativar' abre o dialog de confirmação."""
        email = unique_email("dlg-desktop")
        _criar_usuario(admin_desktop, "Usuário Dialog", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_desktop.locator("dialog[open]")
        dialog.wait_for(state="visible")
        assert dialog.is_visible()

    def test_dialog_exibe_nome_do_usuario(self, admin_desktop):
        """C1: Dialog de confirmação exibe o nome do usuário a ser desativado."""
        email = unique_email("dlg-nome-desktop")
        _criar_usuario(admin_desktop, "Usuário Com Nome", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_desktop.locator("dialog[open]")
        dialog.wait_for(state="visible")
        assert "Usuário Com Nome" in dialog.inner_text()

    def test_cancelar_fecha_dialog_sem_desativar(self, admin_desktop):
        """C1: Clicar em 'Cancelar' fecha o dialog sem alterar o status."""
        email = unique_email("cancel-desktop")
        _criar_usuario(admin_desktop, "Usuário Cancelar", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_desktop.locator("dialog[open]")
        dialog.wait_for(state="visible")
        dialog.locator("button:has-text('Cancelar')").click()

        # Dialog fechado, usuário ainda aparece como Pendente (não Inativo)
        user_row_after = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        assert user_row_after.locator(".status-pill.warning").is_visible()

    # -----------------------------------------------------------------------
    # C2 — Desativação efetiva
    # -----------------------------------------------------------------------

    def test_confirmar_desativacao_muda_badge_para_inativo(self, admin_desktop):
        """C2: Confirmar desativação → badge 'Inativo' aparece na lista."""
        email = unique_email("desativ-desktop")
        _criar_usuario(admin_desktop, "Usuário Desativar", email)

        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_desktop.locator("dialog[open]")
        dialog.wait_for(state="visible")
        dialog.locator(".dialog-actions form button[type='submit']").click()

        # Página recarrega — verifica badge Inativo
        badge_inativo = admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill.muted"
        )
        badge_inativo.wait_for(state="visible")
        assert "Inativo" in badge_inativo.inner_text()

    # -----------------------------------------------------------------------
    # C3 — Reativação
    # -----------------------------------------------------------------------

    def test_reativar_usuario_inativo_muda_badge_para_ativo(self, admin_desktop):
        """C3: Após desativação, botão 'Reativar' aparece e funciona."""
        email = unique_email("reativ-desktop")
        _criar_usuario(admin_desktop, "Usuário Reativar", email)

        # Desativa
        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()
        dialog = admin_desktop.locator("dialog[open]")
        dialog.wait_for(state="visible")
        dialog.locator(".dialog-actions form button[type='submit']").click()

        admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill.muted"
        ).wait_for(state="visible")

        # Reativa
        user_row_inativo = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row_inativo.locator("button:has-text('Reativar')").click()

        # Badge volta a mostrar algum status ativo (Pendente ou Ativo)
        admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill"
        ).wait_for(state="visible")
        badge = admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill"
        )
        assert "Inativo" not in badge.inner_text()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS04DesativarUsuarioMobile:

    def test_botao_desativar_visivel_no_mobile(self, admin_mobile):
        """C1: Em mobile, o botão 'Desativar' está visível para usuários ativos."""
        email = unique_email("desativ-mobile")
        _criar_usuario(admin_mobile, "Usuário Mobile Desativ", email)

        user_row = admin_mobile.locator(".user-row").filter(
            has=admin_mobile.locator(f".user-email:has-text('{email}')")
        )
        assert user_row.locator("button.btn-danger").is_visible()

    def test_dialog_abre_no_mobile(self, admin_mobile):
        """C1: Em mobile, o dialog de confirmação abre ao clicar em Desativar."""
        email = unique_email("dlg-mobile")
        _criar_usuario(admin_mobile, "Usuário Dialog Mobile", email)

        user_row = admin_mobile.locator(".user-row").filter(
            has=admin_mobile.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_mobile.locator("dialog[open]")
        dialog.wait_for(state="visible")
        assert dialog.is_visible()

    def test_desativacao_completa_no_mobile(self, admin_mobile):
        """C2: Em mobile, o fluxo completo de desativação funciona."""
        email = unique_email("full-desativ-mobile")
        _criar_usuario(admin_mobile, "Usuário Full Mobile", email)

        user_row = admin_mobile.locator(".user-row").filter(
            has=admin_mobile.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        dialog = admin_mobile.locator("dialog[open]")
        dialog.wait_for(state="visible")
        dialog.locator(".dialog-actions form button[type='submit']").click()

        badge_inativo = admin_mobile.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill.muted"
        )
        badge_inativo.wait_for(state="visible")
        assert "Inativo" in badge_inativo.inner_text()
