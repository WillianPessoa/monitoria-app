# Sessão: Sprint 0 — Decisões de Arquitetura com IA

**Data:** 2026-05-06  
**Responsável:** Willian Gomes Pessoa (Quality Manager)  
**Ferramenta:** Claude Code — skill `grill-me`  
**Artefatos produzidos:** ADR-0001 a ADR-0005

---

## Contexto inicial

O repositório do grupo tinha os artefatos de produto do Sprint 0 definidos (visão, backlog, personas), mas nenhuma decisão de arquitetura registrada. As seguintes questões estavam em aberto antes da sessão:

- Qual framework Python usar
- Como autenticar usuários (JWT vs sessão)
- Como organizar o código do backend
- Como o frontend HTML+CSS vai consumir o backend
- Como acessar o banco de dados (ORM vs SQL direto)

A sessão foi conduzida pelo QM usando a skill `grill-me`, que faz perguntas uma por vez com recomendação prévia em cada uma. As decisões do projeto solo (monitoria-plus, stack C++/QML) foram usadas como referência de domínio — as regras de negócio são as mesmas; apenas a tecnologia muda.

---

## Perguntas e decisões

### Pergunta 1 — Framework Python

**Opções apresentadas:** Flask / FastAPI / Django  
**Recomendação da skill:** Flask — minimal, sem opinião forte, adequado ao tempo disponível e ao objetivo pedagógico da disciplina  
**Resposta:** Flask  
**Decisão:** Flask como framework Python. (ADR-0001)

---

### Pergunta 2 — Autenticação

**Opções apresentadas:** JWT / sessão com cookie  
**Recomendação da skill:** Sessão com cookie — funciona nativamente com formulários HTML sem JavaScript adicional; JWT faz sentido apenas com SPA  
**Resposta:** Recomendação aceita  
**Decisão:** `flask.session` com cookie assinado. RBAC implementado via decorator no servidor e verificação de `session['papel']` no Jinja2. (ADR-0003)

---

### Pergunta 3 — Organização do backend

**Opções apresentadas:** MVC clássico (models/, views/, controllers/) / Blueprint por domínio  
**Recomendação da skill:** Blueprint por domínio — mapeia diretamente aos épicos do backlog, facilita divisão de trabalho entre devs sem conflito  
**Resposta:** Recomendação aceita  
**Decisão:** Um blueprint Flask por épico: `auth/`, `usuarios/`, `disciplinas/`, `agenda/`, `registros/`, `relatorios/`. (ADR-0002)

---

### Pergunta 4 — Como o frontend consome o backend

**Opções apresentadas:** Jinja2 puro / Jinja2 + fetch seletivo  
**Recomendação da skill:** Jinja2 como base + `fetch` apenas nas telas de agenda e agendamento, onde reload de página inteira prejudica a experiência  
**Resposta:** Recomendação aceita  
**Decisão:** Jinja2 para todas as telas; `fetch` restrito a `agenda.js` e `agendamento.js`. Backend expõe endpoints JSON apenas para essas rotas. (ADR-0005)

---

### Pergunta 5 — Acesso ao banco de dados

**Opções apresentadas:** SQLAlchemy (ORM) / mysql-connector-python com SQL direto  
**Recomendação da skill:** SQL direto — o time já modela o banco em TT02; faz sentido que o código reflita esse modelo sem abstração adicional  
**Resposta:** Recomendação aceita  
**Decisão:** mysql-connector-python com queries parametrizadas via `%s`. Cada blueprint tem `repository.py`. SQL injection é item de verificação obrigatória na Validação Paralela do QM. (ADR-0004)

---

## Artefatos produzidos

| Artefato | Decisão |
|---|---|
| `docs/adr/0001-framework-flask.md` | Flask como framework Python |
| `docs/adr/0002-organizacao-blueprints.md` | Blueprints por domínio (um por épico) |
| `docs/adr/0003-autenticacao-sessao-cookie.md` | Sessão com cookie, RBAC via `session['papel']` |
| `docs/adr/0004-banco-queries-diretas.md` | mysql-connector-python, SQL direto, sem ORM |
| `docs/adr/0005-frontend-jinja2-fetch.md` | Jinja2 base + fetch só em agenda e agendamento |

---

## Nota do QM

O ADR-0004 estabelece uma responsabilidade explícita para o Quality Manager: toda história que envolva acesso ao banco deve ser verificada quanto ao uso de placeholders `%s` — nunca interpolação de string. Isso será item fixo de checklist na Validação Paralela a partir do Sprint 1.
