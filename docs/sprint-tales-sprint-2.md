# Sprint Tales — Sprint 2

**Sprint:** 2 — Cadastro do Domínio Principal
**Período:** 14/05/2026 – 20/05/2026
**QM:** Willian Gomes Pessoa

---

## US06 — Admin cadastra disciplinas

**Prioridade:** Must
**Responsável:** Gustavo
**Alterado depois:** Não
**Tempo suficiente:** Sim

**Solução adotada:** CRUD de disciplinas com nome, código e professor responsável. Validação de código único e de papel do professor. Operações de ativar/desativar e matrícula de alunos em lote (por email) ou individual.

**Arquivos alterados:** `backend/disciplinas/repository.py`, `backend/disciplinas/routes.py`, `backend/disciplinas/service.py`, `frontend/templates/disciplinas/index.html`

**Impacto:** Gestão de disciplinas pelo admin — base do EP02.

---

## US07 — Professor indica aluno como monitor

**Prioridade:** Must
**Responsável:** João Pedro
**Alterado depois:** Não
**Tempo suficiente:** Sim

**Solução adotada:** Tela `GET/POST /monitorias/indicar` para professor selecionar uma das suas disciplinas e um aluno ativo. Validação de propriedade da disciplina (professor só vê as suas) e de papel do aluno. Indicação criada com status `PENDENTE_APROVACAO`. Professor acompanha suas indicações na mesma tela.

**Arquivos alterados:** `backend/monitorias/routes.py`, `backend/monitorias/service.py`, `backend/monitorias/repository.py`, `frontend/templates/monitorias/indicar.html`

**Impacto:** Fluxo de indicação de monitores — depende de US06 e US01.

---

## US08 — Admin aprova ou rejeita indicação de monitor

**Prioridade:** Must
**Responsável:** Pedro
**Alterado depois:** Não
**Tempo suficiente:** Sim

**Solução adotada:** `GET /monitorias/pendentes` lista indicações aguardando aprovação. `POST /monitorias/<id>/aprovar` ativa o vínculo; `POST /monitorias/<id>/rejeitar` registra o motivo. Validação: aluno já com monitoria ativa em qualquer disciplina é bloqueado na aprovação.

**Arquivos alterados:** `backend/monitorias/routes.py`, `backend/monitorias/service.py`, `backend/monitorias/repository.py`, `frontend/templates/monitorias/pending.html`, `docs/adr/0006-admin-aprovacao-indicacao-monitor.md`

**Impacto:** Controle de aprovação de monitores pelo admin — completa o ciclo do EP02.

---

## US09 — Admin lista monitorias ativas por disciplina

**Prioridade:** Should
**Responsável:** João Pedro
**Alterado depois:** Não
**Tempo suficiente:** Sim

**Solução adotada:** Função `list_active_monitorias()` retorna todos os vínculos com `status = 'ATIVO'`. Exibida como tabela "Monitorias ativas" na tela de admin de disciplinas. Mensagem de vazio quando não há registros. Implementada dentro do PR #32 junto com US07/US08.

**Arquivos alterados:** `backend/monitorias/repository.py`, `backend/monitorias/service.py`, `backend/disciplinas/routes.py`, `frontend/templates/disciplinas/index.html`

**Impacto:** Visibilidade das monitorias ativas para o admin — completa EP02.

---

## TT06 — Publicar aplicação em servidor na nuvem

**Prioridade:** Must
**Responsável:** Willian
**Alterado depois:** Não
**Tempo suficiente:** Sim

**Solução adotada:** Publicação da aplicação no Railway. Configuração do `Procfile` (gunicorn), `railpack.json` e `requirements.txt` na raiz. `config.py` adaptado para aceitar as variáveis de ambiente do plugin MySQL do Railway (`MYSQLHOST`, `MYSQLPORT`, etc.). Schema e seed de admins aplicados automaticamente na inicialização.

**Arquivos alterados:** `Procfile`, `railpack.json`, `requirements.txt`, `backend/config.py`, `backend/db/connection.py`

**Impacto:** Aplicação acessível para as POs sem depender de ambiente local.
