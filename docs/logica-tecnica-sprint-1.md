# Explicação da Lógica Técnica — Sprint 1

**Elaborado por:** Desenvolvedores da Sprint 1  
**Destinado a:** Willian Gomes Pessoa (Quality Manager)  
**Sprint:** 1 — Perfis e Autenticação (07/05 a 13/05/2026)

---

## Visão geral da arquitetura

O backend é uma aplicação Flask organizada em **blueprints** — módulos independentes, um por domínio do sistema. A comunicação entre o browser e o servidor usa **sessão por cookie** (sem JWT). O banco de dados é MySQL, acessado por **queries SQL diretas** (sem ORM).

```
browser
  └── Flask (app.py)
        ├── auth/        ← login, logout, primeiro acesso
        ├── usuarios/    ← CRUD de usuários, perfis
        ├── disciplinas/ ← (placeholder Sprint 1)
        ├── agenda/      ← (placeholder Sprint 1)
        ├── registros/   ← (placeholder Sprint 1)
        └── relatorios/  ← (placeholder Sprint 1)
              └── db/connection.py ← pool de conexões MySQL
```

---

## TT01 — Stack

- **Linguagem:** Python 3.12 — familiaridade do time
- **Framework:** Flask 3.0.3 — simples, sem "magia", cada rota é explícita
- **Banco:** MySQL 8.0 — modelo relacional, SQL auditável
- **Conector:** mysql-connector-python 9.0.0 — oficial da Oracle, sem dependências extras
- **Queries:** SQL direto, sem ORM — transparência para revisão técnica e auditoria

---

## TT02 — Modelagem do banco

O schema define 4 tabelas para suportar Sprint 1 e preparar Sprint 2:

**`usuarios`** — tabela central. Cada usuário tem um `papel` (ALUNO, MONITOR, PROFESSOR, ADMIN) e um `status` (PENDENTE, ATIVO, INATIVO). O campo `senha_temporaria` indica se o usuário ainda não trocou a senha inicial.

**`password_reset_tokens`** — tokens de reset de senha com expiração. Pertence a um usuário via FK com `ON DELETE CASCADE`.

**`disciplinas`** — tabela preparada para Sprint 2 (EP02). Já criada para evitar migration futura.

**`monitorias`** — vínculo entre aluno e disciplina. Constraint `UNIQUE(disciplina_id, aluno_id)` impede duplicidade.

---

## TT03 — Setup local

O ambiente local usa **Docker Compose** para subir o MySQL sem instalar nada na máquina. O schema é aplicado automaticamente no primeiro start. O backend roda em **venv Python** com dependências fixadas em `requirements.txt`.

Fluxo de setup em 7 passos documentados em `docs/setup.md`:
1. Criar venv e instalar dependências
2. Subir MySQL via Docker
3. Configurar variáveis de ambiente (`.env.example` como base)
4. Criar o primeiro usuário ADMIN via script
5. Rodar a aplicação

---

## TT04 — Skeleton do projeto

A aplicação usa o padrão **app factory** (`create_app()`): a instância Flask é criada dentro de uma função, o que facilita testes e configuração. Cada domínio é um **blueprint** registrado no factory.

A rota `GET /health` retorna `{"status": "ok"}` com HTTP 200 — usada para verificar se a aplicação está no ar.

Templates e arquivos estáticos (CSS, JS) estão em `frontend/`, separados do backend.

---

## TT05 — Conexão com MySQL

A conexão usa **connection pool** com 5 conexões reutilizáveis — evita abrir e fechar conexão a cada request. Todas as configurações (host, porta, usuário, senha, banco) são lidas de **variáveis de ambiente** via a classe `Config`. Nenhuma credencial está hardcoded no código.

Se o banco não estiver disponível na inicialização, o erro é **logado no console** com `logging.exception` — a aplicação não sobe silenciosamente com banco ausente.

---

## US01 — Cadastro de usuários com perfis

**Fluxo principal (admin cria usuário):**
1. Admin preenche nome, email e papel no formulário
2. Backend valida: papel deve ser ALUNO/MONITOR/PROFESSOR/ADMIN; nome e email obrigatórios; email não pode ser duplicado
3. Senha temporária é gerada com `secrets.choice` (10 caracteres alfanuméricos — criptograficamente seguro)
4. Hash da senha é armazenado no banco (werkzeug `generate_password_hash`)
5. Usuário criado com status `PENDENTE` e `senha_temporaria=True`
6. A senha temporária é exibida ao admin na tela — não é enviada por email

**Outras operações disponíveis:**
- **Desativar usuário**: atualiza status para INATIVO
- **Reset de senha**: gera nova senha temporária, exibe ao admin
- **Monitor edita perfil**: atualiza `contato` e `disponibilidade` no próprio perfil

---

## US02 — Login com email e senha

**Fluxo de login:**
1. Usuário informa email e senha
2. Backend busca usuário por email e verifica com `check_password_hash`
3. Se status for `INATIVO`: rejeita com mensagem de conta inativa
4. Se status for `PENDENTE`: redireciona para tela de **primeiro acesso** (troca de senha obrigatória)
5. Se status for `ATIVO`: cria sessão com `user_id`, `nome`, `papel` e redireciona por papel:
   - ADMIN → gestão de usuários
   - MONITOR → perfil próprio
   - PROFESSOR/ALUNO → home

**Primeiro acesso:**
1. Usuário informa nova senha (mínimo 8 caracteres) e confirmação
2. Backend atualiza hash no banco e muda status para `ATIVO`
3. Usuário é redirecionado ao dashboard

**Segurança da sessão:**
- Cookie com flag `HTTPOnly` (não acessível por JavaScript)
- Em produção, flag `Secure` ativado via variável de ambiente
- Sessão expira em 8 horas

---

## Pontos de atenção para o QM

- **Senha temporária:** exibida uma única vez ao admin — não há recuperação posterior sem novo reset
- **Email:** normalizado para lowercase antes de salvar e comparar
- **Status PENDENTE:** usuário com este status não acessa o sistema — é forçado a trocar a senha primeiro
- **Blueprints futuros:** `disciplinas`, `agenda`, `registros` e `relatorios` existem como placeholders — sem rotas implementadas ainda
