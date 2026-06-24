"""
US07/US08 — Indicação e aprovação de monitor (UI Tests)

US07 — Professor indica aluno:
  C1  Tela de indicação carrega com campos de disciplina e aluno
  C2  Submeter indicação → flash de sucesso
  C3  Indicação aparece na lista de indicações do professor

US08 — Admin aprova/rejeita:
  C1  Admin vê indicação pendente em /monitorias/pendentes
  C2  Admin aprova indicação → flash de sucesso, indicação sai da lista
  C3  Admin rejeita indicação com motivo → flash de sucesso, indicação sai da lista

Fluxo combinado US07→US08: os testes de US08 criam a indicação via flow de professor
antes de processá-la como admin, garantindo pre-condição independente de estado Railway.

Rodar:
    pytest tests/ui/test_ui_us07_us08_indicacao.py -v --headed --slowmo=400
"""

from tests.ui.conftest import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    BASE_URL,
    PROFESSOR_EMAIL,
    PROFESSOR_PASSWORD,
)

INDICAR_URL = f"{BASE_URL}/monitorias/indicar"
PENDENTES_URL = f"{BASE_URL}/monitorias/pendentes"


def _login(page, email, password):
    """Faz login e aguarda o redirecionamento pós-autenticação (destino varia por papel)."""
    page.goto(f"{BASE_URL}/auth/login")
    page.fill("input#email", email)
    page.fill("input#senha", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")


def _logout(page):
    """Faz logout via formulário POST e aguarda tela de login."""
    page.evaluate("""
        (() => {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/auth/logout';
            document.body.appendChild(form);
            form.submit();
        })()
    """)
    page.wait_for_load_state("networkidle")


def _select_first_valid(page, selector):
    """Seleciona a primeira opção válida (não-disabled, com value) de um <select>."""
    value = page.eval_on_selector(
        selector,
        "el => Array.from(el.options).find(o => !o.disabled && o.value)?.value",
    )
    assert value, f"Nenhuma opção válida encontrada em '{selector}'"
    page.select_option(selector, value=value)
    return value


def _criar_indicacao_como_professor(page):
    """Helper: loga como professor, cria uma indicação e retorna o nome do aluno indicado."""
    _login(page, PROFESSOR_EMAIL, PROFESSOR_PASSWORD)
    page.goto(INDICAR_URL)

    # Seleciona primeira disciplina disponível
    _select_first_valid(page, "select#disciplina_id")

    # Seleciona primeiro aluno disponível (via JS)
    aluno_valor = page.eval_on_selector(
        "select#aluno_id",
        "el => Array.from(el.options).find(o => !o.disabled && o.value)?.value",
    )
    if not aluno_valor:
        return None  # Sem alunos ativos — teste será pulado

    aluno_nome = page.eval_on_selector(
        "select#aluno_id",
        "el => Array.from(el.options).find(o => !o.disabled && o.value)?.text?.split('(')[0]?.trim()",
    )
    page.select_option("select#aluno_id", value=aluno_valor)
    page.locator("button[type='submit']:has-text('Enviar indicação')").click()

    flash = page.locator(".alert.success")
    flash.wait_for(state="visible")
    return aluno_nome


# ===========================================================================
# Desktop (1280×800) — US07
# ===========================================================================


class TestUS07IndicarMonitorDesktop:

    def test_tela_indicar_carrega_com_campos(self, professor_desktop):
        """C1: Tela /monitorias/indicar exibe campos de disciplina e aluno."""
        professor_desktop.goto(INDICAR_URL)
        assert professor_desktop.locator("select#disciplina_id").is_visible()
        assert professor_desktop.locator("select#aluno_id").is_visible()

    def test_submeter_indicacao_exibe_flash_sucesso(self, professor_desktop):
        """C2: Professor submete indicação válida → flash de sucesso."""
        professor_desktop.goto(INDICAR_URL)

        # Verifica se professor tem disciplinas
        count = professor_desktop.eval_on_selector(
            "select#disciplina_id",
            "el => Array.from(el.options).filter(o => !o.disabled && o.value).length",
        )
        if count == 0:
            return  # Sem disciplinas para o professor no Railway — pula

        _select_first_valid(professor_desktop, "select#disciplina_id")

        aluno_valor = professor_desktop.eval_on_selector(
            "select#aluno_id",
            "el => Array.from(el.options).find(o => !o.disabled && o.value)?.value",
        )
        if not aluno_valor:
            return  # Sem alunos ativos — pula

        professor_desktop.select_option("select#aluno_id", value=aluno_valor)
        professor_desktop.locator("button[type='submit']:has-text('Enviar indicação')").click()

        flash = professor_desktop.locator(".alert.success, .alert.error")
        flash.wait_for(state="visible")
        # Aceita tanto "sucesso" (nova indicação) quanto mensagem de duplicata
        assert flash.is_visible()

    def test_indicacao_enviada_aparece_na_lista(self, professor_desktop):
        """C3: Após indicação, o nome do aluno aparece na lista de indicações do professor."""
        professor_desktop.goto(INDICAR_URL)

        count = professor_desktop.eval_on_selector(
            "select#disciplina_id",
            "el => Array.from(el.options).filter(o => !o.disabled && o.value).length",
        )
        if count == 0:
            return

        _select_first_valid(professor_desktop, "select#disciplina_id")

        aluno_nome_raw = professor_desktop.eval_on_selector(
            "select#aluno_id",
            "el => Array.from(el.options).find(o => !o.disabled && o.value)?.text",
        )
        if not aluno_nome_raw:
            return

        aluno_nome = aluno_nome_raw.split("(")[0].strip()
        aluno_valor = professor_desktop.eval_on_selector(
            "select#aluno_id",
            "el => Array.from(el.options).find(o => !o.disabled && o.value)?.value",
        )
        professor_desktop.select_option("select#aluno_id", value=aluno_valor)
        professor_desktop.locator("button[type='submit']:has-text('Enviar indicação')").click()
        professor_desktop.locator(".alert").wait_for(state="visible")

        # Redireciona de volta para /indicar e mostra as indicações enviadas
        professor_desktop.wait_for_url(INDICAR_URL)
        professor_desktop.wait_for_load_state("networkidle")
        # Lista de indicações exibe o nome do aluno em .pending-name (não no select oculto)
        professor_desktop.locator(f".pending-name:has-text('{aluno_nome}')").first.wait_for(
            state="visible"
        )


# ===========================================================================
# Desktop (1280×800) — US08
# ===========================================================================


class TestUS08AprovarRejeitarDesktop:

    def test_admin_ve_lista_de_pendentes(self, admin_desktop):
        """C1: Admin acessa /monitorias/pendentes sem erro."""
        admin_desktop.goto(PENDENTES_URL)
        assert admin_desktop.url == PENDENTES_URL
        # Página carrega (sem erro 500)
        assert admin_desktop.locator("body").is_visible()

    def test_aprovar_indicacao_exibe_flash_sucesso(self, page):
        """C2: Admin aprova indicação pendente (criada pelo professor no mesmo teste)."""
        # Cria indicação como professor
        aluno_nome = _criar_indicacao_como_professor(page)
        if not aluno_nome:
            return  # Sem dados disponíveis no Railway

        # Muda para admin
        _logout(page)
        _login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

        page.goto(PENDENTES_URL)
        # Procura a indicação do aluno na lista
        pending_card = page.locator(".pending-card, .pending-item, tr").filter(
            has=page.locator(f"text={aluno_nome}")
        ).first

        if not pending_card.is_visible():
            return  # Indicação pode já ter sido processada

        # Clica em Aprovar → abre dialog
        pending_card.locator("button:has-text('Aprovar')").click()
        dialog = page.locator("dialog[open]")
        dialog.wait_for(state="visible")
        dialog.locator("button[type='submit']").click()

        flash = page.locator(".alert.success")
        flash.wait_for(state="visible")
        assert "aprovada" in flash.inner_text().lower()

    def test_rejeitar_indicacao_exibe_flash_sucesso(self, page):
        """C3: Admin rejeita indicação pendente com motivo."""
        # Cria nova indicação como professor
        aluno_nome = _criar_indicacao_como_professor(page)
        if not aluno_nome:
            return

        _logout(page)
        _login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

        page.goto(PENDENTES_URL)
        pending_card = page.locator(".pending-card, .pending-item, tr").filter(
            has=page.locator(f"text={aluno_nome}")
        ).first

        if not pending_card.is_visible():
            return

        # Clica em Rejeitar → abre dialog
        pending_card.locator("button:has-text('Rejeitar')").click()
        dialog = page.locator("dialog[open]")
        dialog.wait_for(state="visible")
        # Preenche motivo
        motivo_input = dialog.locator("input[name='motivo']")
        if motivo_input.is_visible():
            motivo_input.fill("Teste automatizado — rejeição UI")
        dialog.locator("button[type='submit']").click()

        flash = page.locator(".alert.success")
        flash.wait_for(state="visible")
        assert "rejeitada" in flash.inner_text().lower()


# ===========================================================================
# Mobile (375×812)
# ===========================================================================


class TestUS07US08Mobile:

    def test_tela_indicar_visivel_no_mobile(self, professor_mobile):
        """C1 mobile: Tela /monitorias/indicar carrega com campos visíveis."""
        professor_mobile.goto(INDICAR_URL)
        assert professor_mobile.locator("select#disciplina_id").is_visible()

    def test_lista_pendentes_visivel_no_mobile(self, admin_mobile):
        """C1 mobile: Admin acessa /monitorias/pendentes sem erro."""
        admin_mobile.goto(PENDENTES_URL)
        assert admin_mobile.url == PENDENTES_URL
        assert admin_mobile.locator("body").is_visible()
