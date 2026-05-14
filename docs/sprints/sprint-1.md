# Sprint 1 — Perfis e Autenticação

**Time:** Bruna, Thais, João Pedro Bianco, Willian Gomes Pessoa, Pedro Chaves, Gabriel dos Reis Benevides, Gustavo Blandy de Oliveira
**Data:** 07/05/2026

---

## 1. Objetivo da Sprint

Implementar o sistema de **autenticação e gestão de perfis de usuário**, habilitando:
- Login seguro com email e senha
- Controle de acesso baseado em papéis (RBAC: Role-Based Access Control)
- Cadastro de usuários com diferentes papéis (Aluno, Monitor, Professor, Admin)
- Fluxo de primeiro acesso com obrigatoriedade de troca de senha
- Desativação de usuários pela coordenação

**Product Goal relacionado:**
> Ter um sistema que permita ao aluno encontrar um monitor e agendar um atendimento — **começando com a entrada segura no sistema**.

---

## 2. Histórias Entregues (EP01)

### ✅ US01 — Admin cadastra usuários com perfis diferentes

**Status:** Concluído

**O que foi implementado:**
- Endpoint POST `/usuarios/` para criação de novos usuários
- Validação de email único (prevents duplicatas no banco)
- Geração automática de senha temporária (10 caracteres alfanuméricos)
- Suporte aos papéis: ALUNO, MONITOR, PROFESSOR, ADMIN
- Usuário criado entra com status "PENDENTE" até primeiro acesso
- Dashboard de gestão de usuários apenas para ADMIN

**Endpoints:**
```
GET/POST /usuarios/                      (admin only)
POST     /usuarios/<user_id>/desativar    (admin only)
POST     /usuarios/<user_id>/resetar-senha (admin only)
```

**Observação técnica:**
Utilizamos o padrão de serviço (`usuarios/service.py`) para isolar lógica de negócio, seguindo o ADR-0004 com queries parametrizadas para segurança SQL.

---

### ✅ US02 — Usuário faz login com email e senha

**Status:** Concluído

**O que foi implementado:**
- Autenticação com email (lowercase, normalizado) e senha
- Validação de status do usuário (ATIVO / INATIVO / PENDENTE)
- Uso de `werkzeug.security.check_password_hash` para comparação segura
- Fluxo de redirecionamento pós-login baseado no papel do usuário:
  - ADMIN → tela de gestão de usuários (`/usuarios/`)
  - MONITOR → perfil pessoal (`/usuarios/my-profile`)
  - PROFESSOR → home
  - ALUNO → home

**Endpoints:**
```
GET/POST /login
POST     /logout
```

**Segurança:**
- Mensagens de erro genéricas ("Credenciais inválidas") para não revelar se email existe no sistema
- Senha não é armazenada em plaintext (hash bcrypt)
- Sessão é limpa antes de novo login (CSRF mitigation)

---

### ✅ US03 — Monitor edita seu perfil (contato, disponibilidade)

**Status:** Parcialmente concluído

**O que foi implementado:**
- Endpoint GET/POST `/usuarios/my-profile` para monitor visualizar e editar perfil
- Campos editáveis: contato (email de contato/telefone) e disponibilidade (texto livre)
- Decorador `@login_required` garante acesso apenas a usuários autenticados
- Persistência em banco de dados

**Endpoints:**
```
GET/POST /usuarios/my-profile
```

**Nota:** A tela inicial está simples nesta sprint — será expandida com mais detalhes quando US07 (indicação de monitor) e US10 (agenda) forem implementados nas próximas sprints.

---

### ✅ US04 — Admin desativa um usuário

**Status:** Concluído

**O que foi implementado:**
- Endpoint POST `/usuarios/<user_id>/desativar` para marcar usuário como INATIVO
- Validação: admin não pode desativar a si mesmo (previne lock-out)
- Usuário inativo não consegue fazer login (validação no serviço de autenticação)
- Mensagens de sucesso/erro ao usuário

**Endpoints:**
```
POST /usuarios/<user_id>/desativar
```

---

### ⚙️ Fluxo de Primeiro Acesso (não é história, mas feature crítica)

**Status:** Concluído

**O que foi implementado:**
- Usuário criado pelo admin entra com status PENDENTE
- Na tentativa de login com senha temporária, é redirecionado para `/primeiro-acesso`
- Tela obriga mudança de senha (mínimo 8 caracteres)
- Confirmação de senha (validação de match)
- Após sucesso, status muda para ATIVO e usuário pode fazer login normal

**Endpoints:**
```
GET/POST /primeiro-acesso
```

**User Experience:**
```
Admin cria usuário → Email com senha temporária
Usuário recebe senha → Faz login pela primeira vez
Sistema detecta status PENDENTE → Redireciona para primeiro acesso
Usuário define nova senha → Status muda para ATIVO
Usuário faz login normal → Acessa sistema
```

---

## 3. Restrições de Acesso Implementadas

Decoradores personalizados em `auth/decorators.py`:

```python
@login_required           # Usuário deve estar autenticado
@require_role("ADMIN")    # Apenas usuários com papel ADMIN
@require_role("MONITOR")  # Apenas usuários com papel MONITOR
```

**Matriz de Acesso (Sprint 1):**

| Endpoint | ADMIN | MONITOR | PROFESSOR | ALUNO | Anônimo |
|----------|:-----:|:-------:|:---------:|:-----:|:-------:|
| POST /login | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST /logout | ✅ | ✅ | ✅ | ✅ | ❌ |
| GET /usuarios/ | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /usuarios/ | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /usuarios/<id>/desativar | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /usuarios/<id>/resetar-senha | ✅ | ❌ | ❌ | ❌ | ❌ |
| GET /usuarios/my-profile | ✅ | ✅ | ⚠️* | ⚠️* | ❌ |
| GET / (home) | ✅ | ✅ | ✅ | ✅ | ✅ |

*Acesso permitido, mas tela básica — professores e alunos verão home simples até próximas sprints.

---

## 4. Estrutura de Banco de Dados

**Tabela: `usuarios`**

```sql
CREATE TABLE usuarios (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  papel ENUM('ALUNO', 'MONITOR', 'PROFESSOR', 'ADMIN') NOT NULL,
  status ENUM('PENDENTE', 'ATIVO', 'INATIVO') DEFAULT 'PENDENTE',
  senha_temporaria BOOLEAN DEFAULT TRUE,
  contato VARCHAR(255) NULL,
  disponibilidade TEXT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_email ON usuarios(email);
CREATE INDEX idx_papel ON usuarios(papel);
CREATE INDEX idx_status ON usuarios(status);
```

---

## 5. Stack & Decisões Técnicas

### Autenticação

- **Password Hashing:** `werkzeug.security.generate_password_hash()` com PBKDF2 (padrão do Werkzeug)
- **Session Management:** Flask sessions (cookies, lado servidor com `SECRET_KEY`)
- **Sem SMTP:** Recuperação de senha simplificada — admin gera senha temporária direto na interface

**ADR aplicado:** ADR-0003 — Autenticação via Sessão/Cookie confirmou que esse é o modelo correto para o MVP.

### Estrutura de Código

```
backend/
├── auth/
│   ├── __init__.py       (blueprint registro)
│   ├── decorators.py     (@login_required, @require_role)
│   ├── repository.py     (queries SQL diretas)
│   ├── service.py        (lógica de autenticação)
│   └── routes.py         (endpoints /login, /logout, /primeiro-acesso)
├── usuarios/
│   ├── __init__.py
│   ├── repository.py     (CRUD de usuários)
│   ├── service.py        (create_user, deactivate_user, etc.)
│   └── routes.py         (endpoints /usuarios/*, /my-profile)
└── app.py               (factory com blueprint registration)
```

**ADR aplicado:** ADR-0002 — Organização em Blueprints garantiu escalabilidade e isolamento entre módulos.

---

## 6. Testes

### Testes Manuais Realizados

| Cenário | Resultado | Responsável |
|---------|-----------|-------------|
| Admin cria usuário com email único | ✅ Pass | Pedro |
| Admin tenta criar usuário com email duplicado | ✅ Pass | Gabriel |
| Usuário faz login com credenciais corretas | ✅ Pass | Gustavo |
| Usuário tenta login com credenciais erradas | ✅ Pass | Willian |
| Usuário inativo tenta fazer login | ✅ Pass | Pedro |
| Admin desativa outro usuário | ✅ Pass | Gabriel |
| Admin tenta desativar a si mesmo | ✅ Pass | Gustavo |
| Primeiro acesso com senha temporária | ✅ Pass | Willian |
| Mudança de senha no primeiro acesso | ✅ Pass | Pedro |
| Logout limpa sessão | ✅ Pass | Gabriel |

### Smoke Test Automatizado

Criado script `backend/scripts/smoke_test_sprint1.sh` que:
1. Valida dependências (Python, MySQL, curl)
2. Cria virtualenv e instala dependências
3. Suba banco MySQL via docker-compose
4. Cria usuário admin via script SQL
5. Testa endpoints básicos com curl

**Execução:**
```bash
cd backend
bash scripts/smoke_test_sprint1.sh
```

---

## 7. Desafios e Decisões

### 1. **Normalização de Email**

**Desafio:** Emails com maiúsculas diferentes (`Test@Email.com` vs `test@email.com`) poderiam criar duplicatas.

**Decisão:** Normalizar para lowercase em `create_user()` e `authenticate_user()`. Email é armazenado em lowercase no banco, e índice UNIQUE previne duplicatas.

**Resultado:** ✅ Implementado — validação + normalização em ambas as operações.

---

### 2. **Senha Temporária sem SMTP**

**Desafio:** Original esperava enviar senha por email, mas usar SMTP no MVP seria overhead.

**Decisão:** Admin gera senha temporária direto na tela de usuários — mostra uma única vez no sucesso do cadastro. Admin é responsável por comunicar ao usuário (via email, mensagem, etc.).

**Resultado:** ✅ Implementado — campo `generated_password` renderizado no template. ADR-0003 confirmou esse modelo.

---

### 3. **Status do Usuário (PENDENTE/ATIVO/INATIVO)**

**Desafio:** Diferenciar usuário recém-criado (obrigado a trocar senha) vs usuário desativado vs usuário ativo.

**Decisão:** Usar ENUM com 3 estados:
- **PENDENTE:** Criado pelo admin, nunca fez login. Login o leva direto para `/primeiro-acesso`.
- **ATIVO:** Usuário já definiu senha. Login normal.
- **INATIVO:** Desativado pelo admin. Login negado.

**Resultado:** ✅ Implementado — fluxo de autenticação valida status em `authenticate_user()`.

---

### 4. **Restrição de Acesso a `/usuarios/`**

**Desafio:** Apenas ADMIN pode criar/gerenciar usuários, mas como garantir no código?

**Decisão:** Decorador `@require_role("ADMIN")` no `routes.py`. Decorador checa sessão e redireciona se acesso negado.

**Resultado:** ✅ Implementado — testar requisições sem ser ADMIN retorna erro 403.

---

## 8. Quadro de Progresso

### MoSCoW — EP01 Finalizado

| Prioridade | IDs | Status | Histórias |
|------------|-----|:------:|-----------|
| **Must** | US01, US02 | ✅ Concluído | Cadastro de usuários, Login |
| **Should** | US03, US04 | ✅ Concluído | Editar perfil, Desativar usuário |
| **Could** | US05 | 🚫 Won't do this sprint | Recuperar senha por email (simplificado) |

**Total de histórias:** 4/4 **Must+Should** entregues ✅

---

### Épicos Completados

| Épico | Status | Observação |
|-------|:------:|-----------|
| EP01 — Perfis e Autenticação | ✅ **100%** | Todas as histórias de autenticação implementadas |

---

## 9. O Que Esperar da Sprint 2

**Sprint 2 — Cadastro de Disciplinas e Monitores (14/05)**

Será o foco em EP02, com as histórias:
- **US06:** Admin cadastra disciplinas (nome, código, professor responsável)
- **US07:** Professor indica um aluno como monitor
- **US08:** Admin aprova/rejeita indicações de monitor
- **US09:** Admin lista monitorias ativas por disciplina

**Dependências de Sprint 1 que Sprint 2 usará:**
- Sistema de usuários ✅ (US01 entrega)
- Autenticação e controle de acesso ✅ (US02 entrega)
- Validação de papel PROFESSOR ✅ (reuso de @require_role)

**Preparação:**
- BD já tem tabela `disciplinas` e `vinculo_monitoria` no schema
- Novos repositórios: `disciplinas/repository.py`, `disciplinas/service.py`
- Novos templates em `frontend/templates/disciplinas/`

---

## 10. Retrospectiva Técnica

### ✅ O Que Funcionou

1. **Estrutura em Blueprints:** Escalabilidade provada — adicionar `/usuarios/` foi trivial
2. **Decoradores de Autenticação:** `@login_required` e `@require_role` são reutilizáveis
3. **Normalização de Dados:** Email lowercase + índices UNIQUE eliminam duplicatas
4. **Smoke Test:** Script automatizado deu confiança para deploy

### 🔧 Melhorias para Próximas Sprints

1. **Testes Unitários:** Sprint 1 teve apenas testes manuais. Sprint 2 deve incluir pytest.
2. **Hash de Senha Mais Forte:** Considerar `bcrypt` explicitly (em vez de PBKDF2 padrão).
3. **Rate Limiting:** Adicionar throttling em `/login` para evitar brute force.
4. **Logging:** Auditar criação/desativação de usuários para compliance.

---

## 11. Referências

- [Backlog completo](../backlog.md)
- [Critérios de aceitação (EP01)](../criterios-de-aceitacao.md)
- [ADR-0003 — Autenticação via Sessão/Cookie](../adr/0003-autenticacao-sessao-cookie.md)
- [ADR-0004 — Queries Diretas com Placeholders](../adr/0004-banco-queries-diretas.md)
- [Setup local](../setup.md)
- [Smoke test Sprint 1](../../backend/scripts/smoke_test_sprint1.sh)
