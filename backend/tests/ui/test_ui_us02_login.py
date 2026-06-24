"""
US02 — Login UI Tests (Desktop + Mobile)

Testa a interface real no Railway com Playwright.
Cobre o que os testes de backend não cobrem:
  - Visibilidade e usabilidade dos campos no viewport
  - Flash messages renderizadas na tela
  - Sidebar presente após autenticação
  - Fluxo completo com interação visual: criar usuário → login com senha temp
  - Desativação via dialog nativo → login negado com mensagem na tela

Cenários (criterios-de-aceitacao.md):
  C1  Login bem-sucedido → sidebar aparece, redirecionamento correto
  C2  Credenciais inválidas → mensagem de erro visível na tela
  C3  Primeiro acesso (PENDENTE) → fluxo completo via UI
  C4  Usuário inativo → mensagem de conta inativa visível na tela

Rodar:
    pytest tests/ui/test_ui_us02_login.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, unique_email


# ===========================================================================
# Desktop (1280×800)
# ===========================================================================


class TestUS02LoginDesktop:

    # -----------------------------------------------------------------------
    # C1 — Login bem-sucedido
    # -----------------------------------------------------------------------

    def test_formulario_login_tem_campos_corretos(self, desktop):
        """C1: Página de login exibe campos de email, senha e botão Entrar."""
        desktop.goto(f"{BASE_URL}/auth/login")

        assert desktop.locator("input#email").is_visible()
        assert desktop.locator("input#senha").is_visible()
        assert desktop.locator("button[type='submit']").is_visible()
        assert "Entrar" in desktop.locator("button[type='submit']").inner_text()

    def test_admin_login_exibe_sidebar_e_redireciona(self, desktop):
        """C1: Admin faz login → sidebar visível e URL correta."""
        desktop.goto(f"{BASE_URL}/auth/login")
        desktop.fill("input#email", ADMIN_EMAIL)
        desktop.fill("input#senha", ADMIN_PASSWORD)
        desktop.click("button[type='submit']")
        desktop.wait_for_url(f"{BASE_URL}/usuarios/")

        assert desktop.locator("aside.sidebar").is_visible()
        assert "/usuarios/" in desktop.url

    # -----------------------------------------------------------------------
    # C2 — Credenciais inválidas
    # -----------------------------------------------------------------------

    def test_senha_errada_exibe_alerta_na_tela(self, desktop):
        """C2: Senha errada → alerta de erro visível, sem revelar qual campo."""
        desktop.goto(f"{BASE_URL}/auth/login")
        desktop.fill("input#email", ADMIN_EMAIL)
        desktop.fill("input#senha", "senha-completamente-errada")
        desktop.click("button[type='submit']")

        alerta = desktop.locator(".alert.error")
        assert alerta.is_visible()
        assert "invalidas" in alerta.inner_text().lower()

    def test_email_inexistente_exibe_mesmo_alerta(self, desktop):
        """C2: Email que não existe → mesma mensagem genérica (não revela o campo)."""
        desktop.goto(f"{BASE_URL}/auth/login")
        desktop.fill("input#email", "nao-existe-nunca@teste.com")
        desktop.fill("input#senha", "qualquer")
        desktop.click("button[type='submit']")

        alerta = desktop.locator(".alert.error")
        assert alerta.is_visible()
        assert "invalidas" in alerta.inner_text().lower()

    def test_erro_nao_redireciona_permanece_no_login(self, desktop):
        """C2: Após erro, usuário permanece na tela de login."""
        desktop.goto(f"{BASE_URL}/auth/login")
        desktop.fill("input#email", ADMIN_EMAIL)
        desktop.fill("input#senha", "errada")
        desktop.click("button[type='submit']")

        assert "/auth/login" in desktop.url
        assert desktop.locator("input#email").is_visible()

    # -----------------------------------------------------------------------
    # C3 — Primeiro acesso: fluxo completo via UI
    # -----------------------------------------------------------------------

    def test_fluxo_completo_primeiro_acesso(self, admin_desktop):
        """
        C3: Admin cria usuário → extrai senha temporária da tela →
        faz logout → novo usuário loga → redirecionado para primeiro-acesso.
        """
        email = unique_email("pendente-ui")

        # Admin abre dialog e cria usuário
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Pendente UI")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        # Extrai senha temporária do toast de sucesso (o que contém <strong>)
        toast_strong = admin_desktop.locator(".alert.success:has(strong) strong")
        toast_strong.wait_for(state="visible")
        senha_temp = toast_strong.inner_text().strip()
        assert len(senha_temp) > 0

        # Admin faz logout
        admin_desktop.click("button:has-text('Sair')")
        admin_desktop.wait_for_url(f"{BASE_URL}/auth/login")

        # Novo usuário tenta logar com senha temporária
        admin_desktop.fill("input#email", email)
        admin_desktop.fill("input#senha", senha_temp)
        admin_desktop.click("button[type='submit']")

        # Deve redirecionar para primeiro-acesso
        admin_desktop.wait_for_url(f"{BASE_URL}/auth/primeiro-acesso")
        assert "primeiro-acesso" in admin_desktop.url

    # -----------------------------------------------------------------------
    # C4 — Usuário inativo: desativação via dialog + login negado
    # -----------------------------------------------------------------------

    def test_fluxo_completo_usuario_inativo(self, admin_desktop):
        """
        C4: Admin cria usuário → desativa via dialog nativo →
        logout → usuário tenta logar → alerta de conta inativa na tela.
        """
        email = unique_email("inativo-ui")

        # Admin cria usuário
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Inativo UI")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        # Aguarda a lista recarregar com o novo usuário
        admin_desktop.locator(f".user-email:has-text('{email}')").wait_for(state="visible")

        # Clica em Desativar no row do usuário recém-criado.
        # Usa .btn-danger para distinguir o trigger do botão confirm dentro do dialog,
        # que também tem o texto "Desativar" mas não tem a classe btn-danger.
        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.locator("button.btn-danger").click()

        # Dialog de confirmação abre — clica em Desativar para confirmar
        dialog_confirm = admin_desktop.locator("dialog[open]")
        dialog_confirm.wait_for(state="visible")
        dialog_confirm.locator(".dialog-actions form button[type='submit']").click()

        # Aguarda a página recarregar e o usuário aparecer como Inativo
        admin_desktop.locator(
            f".user-row:has(.user-email:has-text('{email}')) .status-pill.muted"
        ).wait_for(state="visible")

        # Admin faz logout
        admin_desktop.click("button:has-text('Sair')")
        admin_desktop.wait_for_url(f"{BASE_URL}/auth/login")

        # Usuário inativo tenta logar com qualquer senha (não importa qual)
        admin_desktop.fill("input#email", email)
        admin_desktop.fill("input#senha", "qualquer-senha")
        admin_desktop.click("button[type='submit']")

        # Alerta de conta inativa deve aparecer
        alerta = admin_desktop.locator(".alert.error")
        assert alerta.is_visible()
        assert "inativa" in alerta.inner_text().lower()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS02LoginMobile:

    # -----------------------------------------------------------------------
    # C1 — Formulário usável no mobile
    # -----------------------------------------------------------------------

    def test_formulario_login_visivel_e_usavel_no_mobile(self, mobile):
        """C1: Em mobile, campos de login e botão estão visíveis e acessíveis."""
        mobile.goto(f"{BASE_URL}/auth/login")

        assert mobile.locator("input#email").is_visible()
        assert mobile.locator("input#senha").is_visible()
        assert mobile.locator("button[type='submit']").is_visible()

    def test_login_bem_sucedido_no_mobile(self, mobile):
        """C1: Admin faz login em mobile → redirecionado corretamente."""
        mobile.goto(f"{BASE_URL}/auth/login")
        mobile.fill("input#email", ADMIN_EMAIL)
        mobile.fill("input#senha", ADMIN_PASSWORD)
        mobile.click("button[type='submit']")
        mobile.wait_for_url(f"{BASE_URL}/usuarios/")

        assert "/usuarios/" in mobile.url

    # -----------------------------------------------------------------------
    # C2 — Erro visível no mobile
    # -----------------------------------------------------------------------

    def test_alerta_erro_visivel_no_mobile(self, mobile):
        """C2: Em mobile, alerta de credenciais inválidas é visível na tela."""
        mobile.goto(f"{BASE_URL}/auth/login")
        mobile.fill("input#email", ADMIN_EMAIL)
        mobile.fill("input#senha", "errada")
        mobile.click("button[type='submit']")

        alerta = mobile.locator(".alert.error")
        assert alerta.is_visible()
        assert "invalidas" in alerta.inner_text().lower()
