# Como rodar os testes automatizados

Este documento explica como qualquer dev do time pode rodar os testes localmente e o que cada suíte faz.

---

## Visão geral das duas suítes

| Suíte | Framework | Banco | Onde roda |
|---|---|---|---|
| **Backend** | pytest + Flask test client | `monitoria_test` local (Docker) | Na sua máquina |
| **UI** | pytest + Playwright + Chromium | Não usa banco | Contra o Railway (app real) |

Os testes de backend são completamente isolados: criam e destroem o banco `monitoria_test` a cada execução. Os testes de UI acessam o Railway em produção — criam dados reais que ficam acumulados.

---

## Pré-requisitos

### Para testes de backend

1. **Docker** rodando com o container MySQL:
   ```bash
   docker compose -f docker-sql.yaml up -d
   ```
   Aguarda o container ficar `healthy` (5–20 segundos).

2. **Ambiente virtual Python** com as dependências:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/pip install pytest pytest-cov
   ```

3. **Variáveis de ambiente** — os valores padrão já funcionam com o Docker local:
   | Variável | Padrão usado pelos testes | Descrição |
   |---|---|---|
   | `MYSQL_HOST` | `localhost` | Host do MySQL |
   | `MYSQL_PORT` | `3306` | Porta |
   | `MYSQL_USER` | `root` | Usuário |
   | `MYSQL_PASSWORD` | `monitoria_root` | Senha root |
   | `MYSQL_DATABASE` | `monitoria_test` | Sobrescrito automaticamente pelo conftest |

   Se o seu Docker usa valores diferentes, exporte as variáveis antes de rodar:
   ```bash
   export MYSQL_PASSWORD=outra_senha
   ```

### Para testes de UI

1. Tudo do backend, mais:
   ```bash
   .venv/bin/pip install pytest-playwright
   .venv/bin/playwright install chromium
   ```

2. **Conexão com a internet** — os testes acessam `https://web-production-1f724.up.railway.app`.

3. As credenciais de teste estão hardcoded no `tests/ui/conftest.py` (são as mesmas do README do projeto).

---

## Como rodar

Todos os comandos a partir da pasta `backend/`:

```bash
cd monitoria-app/backend
```

### Testes de backend (rápidos, ~50s)

```bash
# Todos os testes de backend
../.venv/bin/pytest tests/ --ignore=tests/ui/ -v

# Uma US específica
../.venv/bin/pytest tests/test_us01_cadastro_usuarios.py -v

# Só uma função
../.venv/bin/pytest tests/test_us02_login.py::TestUS02Login::test_login_bem_sucedido -v
```

### Testes de UI (lentos, ~4 min para tudo)

```bash
# Todos os testes de UI (headless)
../.venv/bin/pytest tests/ui/ -v

# Com browser visível para acompanhar
../.venv/bin/pytest tests/ui/ -v --headed --slowmo=400

# Uma US específica
../.venv/bin/pytest tests/ui/test_ui_us01_cadastro.py -v --headed

# Só desktop (pula mobile)
../.venv/bin/pytest tests/ui/ -v -k "Desktop"
```

### Tudo de uma vez

```bash
../.venv/bin/pytest tests/ -v
```

---

## O que cada arquivo de teste cobre

### Suíte de backend (`tests/`)

| Arquivo | US | Cenários testados |
|---|---|---|
| `test_us01_cadastro_usuarios.py` | US01 | Cadastro válido, email duplicado, papel inválido, campos obrigatórios, proteção de acesso |
| `test_us02_login.py` | US02 | Login válido, senha errada, usuário inexistente, status INATIVO/PENDENTE, senha temporária |
| `test_us03_editar_perfil_monitor.py` | US03 | Salvar contato email/celular, formato inválido, disponibilidade, proteção de acesso |
| `test_us04_desativar_usuario.py` | US04 | Desativar, auto-desativação bloqueada, reativar, ID inexistente |
| `test_us05_resetar_senha.py` | US05 | Reset bem-sucedido, senha temporária no banco, auto-reset bloqueado, ID inexistente |
| `test_us06_cadastrar_disciplinas.py` | US06 | Cadastro válido, código duplicado, professor inválido/inativo, campos obrigatórios |
| `test_us07_indicar_monitor.py` | US07 | Indicação bem-sucedida, não-aluno como aluno, disciplina alheia, reenvio reutiliza |
| `test_us08_aprovar_rejeitar_indicacao.py` | US08 | Aprovação, rejeição com motivo, sai da fila, aluno já monitor, ID inexistente |
| `test_us09_listar_monitorias_ativas.py` | US09 | Listagem com dados, múltiplas, pendentes excluídas, seção ausente sem ativas |

### Suíte de UI (`tests/ui/`)

| Arquivo | US | O que valida na tela real |
|---|---|---|
| `test_ui_us01_cadastro.py` | US01 | Dialog de novo usuário, cadastro e listagem, duplicata, mobile |
| `test_ui_us02_login.py` | US02 | Formulário de login, flash de erro, redirecionamento pós-login, mobile |
| `test_ui_us03_editar_perfil.py` | US03 | Formulário de perfil, salvar contato, feedback visual, mobile |
| `test_ui_us04_desativar_usuario.py` | US04 | Dialog de confirmação, badge Inativo, reativação, mobile |
| `test_ui_us05_resetar_senha.py` | US05 | Botão visível, flash com senha temporária, status Pendente pós-reset, mobile |
| `test_ui_us06_cadastrar_disciplinas.py` | US06 | Dialog nova disciplina, flash de sucesso, código duplicado, mobile |
| `test_ui_us07_us08_indicacao.py` | US07+US08 | Formulário de indicação, fluxo professor→admin, aprovar/rejeitar dialogs |
| `test_ui_us09_listar_monitorias_ativas.py` | US09 | Seção visível, colunas, ao menos uma linha, mobile |

---

## Detalhes de isolamento dos testes de backend

O `conftest.py` garante que cada teste começa com estado limpo:

- **Uma vez por execução (`scope="session"`):** cria o banco `monitoria_test` do zero, aplica o `schema.sql`, insere os admins seed (willian.pessoa.cs@gmail.com / monitoria-app).
- **Após cada teste (`autouse=True`):** trunca todas as tabelas na ordem correta (respeitando FKs) e restaura os admins seed.

Isso significa que cada teste pode criar qualquer dado sem se preocupar com limpeza — o próximo teste começa limpo.

---

## Detalhes dos testes de UI

Os testes de UI **não limpam dados** do Railway. Cada execução cria novos usuários, disciplinas e indicações. Para evitar conflitos:

- Usuários são criados com emails únicos: `unique_email("prefixo")` → `prefixo-{timestamp}@teste.com`
- Disciplinas são criadas com códigos únicos: `unique_code("T")` → `T{timestamp}`
- Credenciais estáticas (professor@email.com.br, aluno-monitor@email.com.br) são usadas apenas para operações que dependem de estado pré-existente

**Consequência:** com muitas execuções, o Railway acumula dados de teste. Isso não afeta os testes, mas pode poluir a listagem de usuários/disciplinas na tela de admin.

---

## Rodando no CI (Railway como alvo)

Os testes de UI já apontam para o Railway por padrão (`BASE_URL` em `tests/ui/conftest.py`). Não é necessário subir nada localmente para rodá-los — só precisa de Python, Playwright e internet.

Os testes de backend precisam do Docker local (ou de um MySQL acessível com as credenciais configuradas via variáveis de ambiente).

---

## Troubleshooting

**`OperationalError: Access denied`** — senha do MySQL local diferente. Exporte `MYSQL_PASSWORD`.

**`TimeoutError` nos testes de UI** — Railway pode estar em cold start. Aguarde 30s e tente novamente.

**`Duplicate column name` ao criar o banco** — o `conftest.py` já contorna isso pré-marcando as migrations. Se aparecer, limpe o banco manualmente:
```bash
docker exec -it monitoria-mysql mysql -uroot -pmonitoria_root -e "DROP DATABASE IF EXISTS monitoria_test;"
```

**Testes de UI flaky** — algumas asserções dependem de dados existentes no Railway (ex: monitorias ativas para US09). Se o Railway for redeploy com banco limpo, precisará de um seed antes de rodar os testes de UI.
