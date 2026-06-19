"""
Fixtures compartilhadas para testes de UI com Playwright.

Todos os testes de UI rodam contra o Railway (ambiente real).
Não há limpeza automática — os dados criados acumulam no Railway.
Por isso, todos os testes que criam usuários usam emails únicos por execução.

Rodar os testes:
    pytest tests/ui/ -v                  # headless (padrão)
    pytest tests/ui/ -v --headed         # com browser visível
    pytest tests/ui/ -v --slowmo=400     # com browser visível e delay para acompanhar
"""

import time

import pytest

BASE_URL = "https://web-production-1f724.up.railway.app"
ADMIN_EMAIL = "willian.pessoa.cs@gmail.com"
ADMIN_PASSWORD = "monitoria-app"

VIEWPORT_DESKTOP = {"width": 1280, "height": 800}
VIEWPORT_MOBILE = {"width": 375, "height": 812}

# Credenciais de teste estáticas no Railway
MONITOR_EMAIL = "aluno-monitor@email.com.br"
MONITOR_PASSWORD = "monitoria-app"

PROFESSOR_EMAIL = "professor@email.com.br"
PROFESSOR_PASSWORD = "monitoria-app"

ALUNO_EMAIL = "aluno-comum@email.com.br"
ALUNO_PASSWORD = "monitoria-app"


def unique_email(prefix="ui"):
    """Gera email único por execução para evitar conflito no Railway."""
    return f"{prefix}-{int(time.time() * 1000)}@teste.com"


# ---------------------------------------------------------------------------
# Fixtures de viewport
# ---------------------------------------------------------------------------


@pytest.fixture
def desktop(page):
    """Página em resolução desktop (1280×800)."""
    page.set_viewport_size(VIEWPORT_DESKTOP)
    return page


@pytest.fixture
def mobile(page):
    """Página em resolução mobile (375×812 — iPhone 14)."""
    page.set_viewport_size(VIEWPORT_MOBILE)
    return page


# ---------------------------------------------------------------------------
# Fixtures de autenticação
# ---------------------------------------------------------------------------


@pytest.fixture
def admin_desktop(desktop):
    """Desktop já autenticado como admin, na página /usuarios/."""
    desktop.goto(f"{BASE_URL}/auth/login")
    desktop.fill("input#email", ADMIN_EMAIL)
    desktop.fill("input#senha", ADMIN_PASSWORD)
    desktop.click("button[type='submit']")
    desktop.wait_for_url(f"{BASE_URL}/usuarios/")
    return desktop


@pytest.fixture
def admin_mobile(mobile):
    """Mobile já autenticado como admin, na página /usuarios/."""
    mobile.goto(f"{BASE_URL}/auth/login")
    mobile.fill("input#email", ADMIN_EMAIL)
    mobile.fill("input#senha", ADMIN_PASSWORD)
    mobile.click("button[type='submit']")
    mobile.wait_for_url(f"{BASE_URL}/usuarios/")
    return mobile


@pytest.fixture
def monitor_desktop(desktop):
    """Desktop já autenticado como monitor (credencial estática do Railway)."""
    desktop.goto(f"{BASE_URL}/auth/login")
    desktop.fill("input#email", MONITOR_EMAIL)
    desktop.fill("input#senha", MONITOR_PASSWORD)
    desktop.click("button[type='submit']")
    desktop.wait_for_url(f"{BASE_URL}/")
    return desktop


@pytest.fixture
def monitor_mobile(mobile):
    """Mobile já autenticado como monitor (credencial estática do Railway)."""
    mobile.goto(f"{BASE_URL}/auth/login")
    mobile.fill("input#email", MONITOR_EMAIL)
    mobile.fill("input#senha", MONITOR_PASSWORD)
    mobile.click("button[type='submit']")
    mobile.wait_for_url(f"{BASE_URL}/")
    return mobile


@pytest.fixture
def professor_desktop(desktop):
    """Desktop já autenticado como professor (credencial estática do Railway)."""
    desktop.goto(f"{BASE_URL}/auth/login")
    desktop.fill("input#email", PROFESSOR_EMAIL)
    desktop.fill("input#senha", PROFESSOR_PASSWORD)
    desktop.click("button[type='submit']")
    desktop.wait_for_url(f"{BASE_URL}/")
    return desktop


@pytest.fixture
def professor_mobile(mobile):
    """Mobile já autenticado como professor (credencial estática do Railway)."""
    mobile.goto(f"{BASE_URL}/auth/login")
    mobile.fill("input#email", PROFESSOR_EMAIL)
    mobile.fill("input#senha", PROFESSOR_PASSWORD)
    mobile.click("button[type='submit']")
    mobile.wait_for_url(f"{BASE_URL}/")
    return mobile
