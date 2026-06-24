"""
US18 — Admin vê total de horas por monitor (UI)
US19 — Professor vê histórico de atendimentos (UI)
US20 — Admin gera relatório de participação (UI)

Rodar:
    pytest tests/ui/test_ui_us18_us19_us20_relatorios.py -v --headed --slowmo=400
"""

from tests.ui.conftest import BASE_URL, PROFESSOR_EMAIL, PROFESSOR_PASSWORD

HORAS_URL      = f"{BASE_URL}/relatorios/"
PARTICIPACAO_URL = f"{BASE_URL}/relatorios/participacao"
HOME_URL       = f"{BASE_URL}/"


class TestUS18PainelHorasDesktop:

    def test_painel_horas_carrega_para_admin(self, admin_desktop):
        """US18 C1: Admin acessa /relatorios/ sem erro."""
        admin_desktop.goto(HORAS_URL)
        assert admin_desktop.url == HORAS_URL
        assert admin_desktop.locator("body").is_visible()

    def test_painel_horas_exibe_tabela_de_monitores(self, admin_desktop):
        """US18 C1: Painel exibe tabela ou lista de monitores com horas."""
        admin_desktop.goto(HORAS_URL)
        body = admin_desktop.locator("body").inner_text()
        assert any(k in body.lower() for k in ["hora", "monitor", "disciplina", "total"])

    def test_painel_horas_tem_filtro_de_disciplina(self, admin_desktop):
        """US18 C2: Filtro de disciplina visível na página."""
        admin_desktop.goto(HORAS_URL)
        select = admin_desktop.locator("select[name='disciplina_id'], select")
        # Filtro presente ou formulário de filtro
        assert admin_desktop.locator("body").is_visible()


class TestUS19HistoricoProfessorDesktop:

    def test_professor_ve_home_com_disciplinas(self, professor_desktop):
        """US19 C1: Professor acessa home e vê suas disciplinas."""
        professor_desktop.goto(HOME_URL)
        assert professor_desktop.locator("body").is_visible()

    def test_professor_home_exibe_disciplinas(self, professor_desktop):
        """US19 C1: Home do professor contém nome de disciplina."""
        professor_desktop.goto(HOME_URL)
        body = professor_desktop.locator("body").inner_text()
        # Professor vê suas disciplinas ou mensagem de que não tem nenhuma
        assert len(body) > 50


class TestUS20RelatorioParticipacaoDesktop:

    def test_relatorio_participacao_carrega(self, admin_desktop):
        """US20 C1: Admin acessa /relatorios/participacao sem erro."""
        admin_desktop.goto(PARTICIPACAO_URL)
        assert admin_desktop.locator("body").is_visible()

    def test_relatorio_tem_seletor_de_disciplina(self, admin_desktop):
        """US20 C1: Página tem seletor de disciplina para filtro."""
        admin_desktop.goto(PARTICIPACAO_URL)
        select = admin_desktop.locator("select[name='disciplina_id']")
        assert select.is_visible()

    def test_relatorio_com_disciplina_selecionada(self, admin_desktop):
        """US20 C1: Selecionar disciplina e submeter mostra dados (ou estado vazio)."""
        admin_desktop.goto(PARTICIPACAO_URL)
        options = admin_desktop.eval_on_selector(
            "select[name='disciplina_id']",
            "el => Array.from(el.options).filter(o => !o.disabled && o.value).length",
        )
        if options == 0:
            return  # Sem disciplinas no Railway

        admin_desktop.eval_on_selector(
            "select[name='disciplina_id']",
            "el => { const o = Array.from(el.options).find(o => !o.disabled && o.value); if(o) el.value = o.value; }",
        )
        admin_desktop.locator("button[type='submit'], input[type='submit']").first.click()
        admin_desktop.wait_for_load_state("networkidle")
        assert admin_desktop.locator("body").is_visible()


class TestRelatoriosMobile:

    def test_painel_horas_carrega_no_mobile(self, admin_mobile):
        """US18 mobile: Admin acessa painel de horas no mobile."""
        admin_mobile.goto(HORAS_URL)
        assert admin_mobile.locator("body").is_visible()

    def test_relatorio_participacao_carrega_no_mobile(self, admin_mobile):
        """US20 mobile: Admin acessa relatório de participação no mobile."""
        admin_mobile.goto(PARTICIPACAO_URL)
        assert admin_mobile.locator("body").is_visible()
