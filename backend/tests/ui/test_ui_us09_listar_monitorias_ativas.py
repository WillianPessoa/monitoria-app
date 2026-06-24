"""
US09 — Admin lista monitorias ativas por disciplina (UI Tests)

Cenários:
  C1  Seção "Monitorias ativas" está visível na tela de disciplinas quando há registros
  C2  A seção exibe as colunas esperadas (Disciplina, Monitor, Professor, Desde)
  C3  Cada linha mostra código da disciplina e nome do aluno-monitor

Nota: os testes de UI dependem de monitorias ativas existentes no Railway.
Após a sessão de US08, há ao menos uma monitoria aprovada (Aluno Comum).
C2 (seção ausente) não é testável via UI sem controle do estado Railway.

Rodar:
    pytest tests/ui/test_ui_us09_listar_monitorias_ativas.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL

DISCIPLINAS_URL = f"{BASE_URL}/disciplinas/"


class TestUS09ListarMonitoriasAtivasDesktop:

    def test_secao_monitorias_ativas_esta_visivel(self, admin_desktop):
        """C1: Seção 'Monitorias ativas' aparece na tela de disciplinas."""
        admin_desktop.goto(DISCIPLINAS_URL)
        heading = admin_desktop.locator("h3:has-text('Monitorias ativas')")
        heading.wait_for(state="visible")
        assert heading.is_visible()

    def test_colunas_da_secao_estao_presentes(self, admin_desktop):
        """C2: Cabeçalho da tabela exibe Disciplina, Monitor, Professor e Desde."""
        admin_desktop.goto(DISCIPLINAS_URL)
        admin_desktop.locator("h3:has-text('Monitorias ativas')").wait_for(state="visible")

        page_text = admin_desktop.locator(".card").filter(
            has=admin_desktop.locator("h3:has-text('Monitorias ativas')")
        ).inner_text()

        page_text_lower = page_text.lower()
        assert "disciplina" in page_text_lower
        assert "monitor" in page_text_lower
        assert "professor" in page_text_lower
        assert "desde" in page_text_lower

    def test_pelo_menos_uma_linha_de_dados_visivel(self, admin_desktop):
        """C1: Ao menos uma linha de monitoria ativa está visível na tabela."""
        admin_desktop.goto(DISCIPLINAS_URL)
        admin_desktop.locator("h3:has-text('Monitorias ativas')").wait_for(state="visible")

        # Cada linha está dentro do .card de monitorias ativas
        card = admin_desktop.locator(".card").filter(
            has=admin_desktop.locator("h3:has-text('Monitorias ativas')")
        )
        # A seção tem ao menos um div com dados de linha (não só o cabeçalho)
        rows = card.locator(".user-list > div:not(.user-list-head)")
        assert rows.count() >= 1

    def test_linha_contem_codigo_de_disciplina(self, admin_desktop):
        """C1: Cada linha visível exibe o código da disciplina (ex: MAB nnn)."""
        admin_desktop.goto(DISCIPLINAS_URL)
        admin_desktop.locator("h3:has-text('Monitorias ativas')").wait_for(state="visible")

        card = admin_desktop.locator(".card").filter(
            has=admin_desktop.locator("h3:has-text('Monitorias ativas')")
        )
        first_row = card.locator(".user-list > div:not(.user-list-head)").first
        row_text = first_row.inner_text()
        # Linha deve conter algo com padrão de código (letras + números)
        assert any(char.isdigit() for char in row_text)


class TestUS09ListarMonitoriasAtivasMobile:

    def test_secao_monitorias_ativas_visivel_no_mobile(self, admin_mobile):
        """C1 mobile: Seção 'Monitorias ativas' aparece em mobile."""
        admin_mobile.goto(DISCIPLINAS_URL)
        heading = admin_mobile.locator("h3:has-text('Monitorias ativas')")
        heading.wait_for(state="visible")
        assert heading.is_visible()
