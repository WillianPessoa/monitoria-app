"""
US01 — Cadastro de Usuários UI Tests (Desktop + Mobile)

Testa a interface real no Railway com Playwright.
Cobre o que os testes de backend não cobrem:
  - Botão "Novo usuário" visível e clicável
  - Dialog nativo (<dialog>) abre corretamente
  - Formulário dentro do dialog tem os campos corretos
  - Toast de senha temporária visível após cadastro
  - Usuário aparece na lista com status "Pendente"
  - Mensagem de email duplicado visível na tela
  - Campos required impedem submissão pelo browser (validação nativa HTML)

Cenários (criterios-de-aceitacao.md):
  C1  Cadastro bem-sucedido → senha temporária visível, usuário na lista como Pendente
  C2  Email duplicado → flash de erro visível na tela
  C3  Campos obrigatórios ausentes → browser impede submissão (required nativo)

Rodar:
    pytest tests/ui/test_ui_us01_cadastro.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL, unique_email


# ===========================================================================
# Desktop (1280×800)
# ===========================================================================


class TestUS01CadastroDesktop:

    # -----------------------------------------------------------------------
    # Pré-condição: acesso ao formulário via dialog
    # -----------------------------------------------------------------------

    def test_botao_novo_usuario_visivel(self, admin_desktop):
        """Setup: Botão 'Novo usuário' está visível na página."""
        assert admin_desktop.locator("button:has-text('Novo usuário')").is_visible()

    def test_dialog_abre_ao_clicar_novo_usuario(self, admin_desktop):
        """Setup: Clicar em 'Novo usuário' abre o dialog nativo."""
        admin_desktop.click("button:has-text('Novo usuário')")
        dialog = admin_desktop.locator("dialog#dlg-novo-usuario")
        dialog.wait_for(state="visible")
        assert dialog.is_visible()

    def test_dialog_tem_campos_nome_email_e_papel(self, admin_desktop):
        """Setup: Dialog contém os campos nome, email e papel (select)."""
        admin_desktop.click("button:has-text('Novo usuário')")
        dialog = admin_desktop.locator("dialog#dlg-novo-usuario")
        dialog.wait_for(state="visible")

        assert dialog.locator("input#nome").is_visible()
        assert dialog.locator("input#email").is_visible()
        assert dialog.locator("select#papel").is_visible()

    # -----------------------------------------------------------------------
    # C1 — Cadastro bem-sucedido
    # -----------------------------------------------------------------------

    def test_cadastro_exibe_senha_temporaria_no_toast(self, admin_desktop):
        """C1: Após cadastro, toast exibe a senha temporária gerada."""
        email = unique_email("cad-desktop")

        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Teste UI")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        # A página exibe dois .alert.success: o flash da rota e o toast com a senha.
        # Usamos :has(strong) para selecionar especificamente o toast da senha temporária.
        toast = admin_desktop.locator(".alert.success:has(strong)")
        toast.wait_for(state="visible")
        assert "Usuário criado" in toast.inner_text()

        senha_temp = toast.locator("strong").inner_text().strip()
        assert len(senha_temp) > 0

    def test_usuario_aparece_na_lista_com_status_pendente(self, admin_desktop):
        """C1: Usuário recém-cadastrado aparece na lista com badge 'Pendente'."""
        email = unique_email("lista-desktop")

        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Lista UI")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        # Localiza o row do usuário recém-criado e verifica o badge Pendente
        user_row = admin_desktop.locator(".user-row").filter(
            has=admin_desktop.locator(f".user-email:has-text('{email}')")
        )
        user_row.wait_for(state="visible")

        badge = user_row.locator(".status-pill.warning")
        assert badge.is_visible()
        assert "Pendente" in badge.inner_text()

    # -----------------------------------------------------------------------
    # C2 — Email duplicado
    # -----------------------------------------------------------------------

    def test_email_duplicado_exibe_flash_de_erro(self, admin_desktop):
        """C2: Cadastrar o mesmo email duas vezes → alerta de erro visível."""
        email = unique_email("dup-desktop")

        # Primeiro cadastro
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Dup 1")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")
        admin_desktop.locator(".alert.success:has(strong)").wait_for(state="visible")

        # Segundo cadastro com mesmo email
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Usuário Dup 2")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", email)
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        alerta = admin_desktop.locator(".alert.error")
        alerta.wait_for(state="visible")
        assert "ja cadastrado" in alerta.inner_text().lower()

    # -----------------------------------------------------------------------
    # C3 — Campos obrigatórios (validação nativa do browser)
    # -----------------------------------------------------------------------

    def test_campo_nome_required_impede_submissao(self, admin_desktop):
        """C3: Campo nome é required — browser não submete o form sem ele."""
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")

        # Deixa nome vazio, preenche o resto
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", "sem-nome@teste.com")
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        # Dialog deve permanecer aberto (form não foi submetido)
        assert admin_desktop.locator("dialog#dlg-novo-usuario").is_visible()

    def test_campo_email_required_impede_submissao(self, admin_desktop):
        """C3: Campo email é required — browser não submete o form sem ele."""
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")

        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Sem Email")
        admin_desktop.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        assert admin_desktop.locator("dialog#dlg-novo-usuario").is_visible()

    def test_campo_papel_required_impede_submissao(self, admin_desktop):
        """C3: Select papel é required — browser não submete sem seleção."""
        admin_desktop.click("button:has-text('Novo usuário')")
        admin_desktop.locator("dialog#dlg-novo-usuario").wait_for(state="visible")

        admin_desktop.fill("dialog#dlg-novo-usuario input#nome", "Sem Papel")
        admin_desktop.fill("dialog#dlg-novo-usuario input#email", "sem-papel@teste.com")
        # Não seleciona papel — mantém "Selecione" (value="")
        admin_desktop.click("dialog#dlg-novo-usuario button[type='submit']")

        assert admin_desktop.locator("dialog#dlg-novo-usuario").is_visible()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS01CadastroMobile:

    def test_botao_novo_usuario_visivel_no_mobile(self, admin_mobile):
        """C1: Em mobile, o botão 'Novo usuário' está visível."""
        assert admin_mobile.locator("button:has-text('Novo usuário')").is_visible()

    def test_dialog_abre_no_mobile(self, admin_mobile):
        """C1: Em mobile, o dialog de cadastro abre ao clicar no botão."""
        admin_mobile.click("button:has-text('Novo usuário')")
        dialog = admin_mobile.locator("dialog#dlg-novo-usuario")
        dialog.wait_for(state="visible")
        assert dialog.is_visible()

    def test_cadastro_completo_funciona_no_mobile(self, admin_mobile):
        """C1: Em mobile, é possível preencher o form e criar um usuário."""
        email = unique_email("cad-mobile")

        admin_mobile.click("button:has-text('Novo usuário')")
        admin_mobile.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_mobile.fill("dialog#dlg-novo-usuario input#nome", "Usuário Mobile UI")
        admin_mobile.fill("dialog#dlg-novo-usuario input#email", email)
        admin_mobile.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_mobile.click("dialog#dlg-novo-usuario button[type='submit']")

        toast = admin_mobile.locator(".alert.success:has(strong)")
        toast.wait_for(state="visible")
        assert "Usuário criado" in toast.inner_text()

    def test_email_duplicado_exibe_erro_no_mobile(self, admin_mobile):
        """C2: Em mobile, erro de email duplicado é visível na tela."""
        email = unique_email("dup-mobile")

        # Primeiro cadastro
        admin_mobile.click("button:has-text('Novo usuário')")
        admin_mobile.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_mobile.fill("dialog#dlg-novo-usuario input#nome", "Dup Mobile 1")
        admin_mobile.fill("dialog#dlg-novo-usuario input#email", email)
        admin_mobile.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_mobile.click("dialog#dlg-novo-usuario button[type='submit']")
        admin_mobile.locator(".alert.success:has(strong)").wait_for(state="visible")

        # Segundo cadastro com mesmo email
        admin_mobile.click("button:has-text('Novo usuário')")
        admin_mobile.locator("dialog#dlg-novo-usuario").wait_for(state="visible")
        admin_mobile.fill("dialog#dlg-novo-usuario input#nome", "Dup Mobile 2")
        admin_mobile.fill("dialog#dlg-novo-usuario input#email", email)
        admin_mobile.select_option("dialog#dlg-novo-usuario select#papel", "ALUNO")
        admin_mobile.click("dialog#dlg-novo-usuario button[type='submit']")

        alerta = admin_mobile.locator(".alert.error")
        alerta.wait_for(state="visible")
        assert "ja cadastrado" in alerta.inner_text().lower()
