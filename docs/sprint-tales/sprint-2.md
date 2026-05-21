# Sprint Tales — Sprint 2

**Sprint:** 2 — Cadastro do Domínio Principal
**Período:** 14/05/2026 – 20/05/2026
**QM:** Willian Gomes Pessoa

---

| ID | Prioridade | Solução adotada | Quem resolveu | Alterado depois? | Tempo suficiente? | Arquivos alterados | Impacto em qual artefato |
|---|---|---|---|---|---|---|---|
| US06 | must-have | CRUD de disciplinas com nome, código e professor responsável. Validação de código único e de papel do professor. Operações de ativar/desativar e matrícula de alunos em lote (por email) ou individual. | Gustavo | Não | Sim | `backend/disciplinas/repository.py`, `backend/disciplinas/routes.py`, `backend/disciplinas/service.py`, `frontend/templates/disciplinas/index.html` | Gestão de disciplinas pelo admin — base do EP02 |
| US07 | must-have | Tela `GET/POST /monitorias/indicar` para professor selecionar uma das suas disciplinas e um aluno ativo. Validação de propriedade da disciplina (professor só vê as suas) e de papel do aluno. Indicação criada com status `PENDENTE_APROVACAO`. Professor acompanha suas indicações na mesma tela. | João Pedro | Não | Sim | `backend/monitorias/routes.py`, `backend/monitorias/service.py`, `backend/monitorias/repository.py`, `frontend/templates/monitorias/indicar.html` | Fluxo de indicação de monitores — depende de US06 e US01 |
| US08 | must-have | `GET /monitorias/pendentes` lista indicações aguardando aprovação. `POST /monitorias/<id>/aprovar` ativa o vínculo; `POST /monitorias/<id>/rejeitar` registra o motivo. Validação: aluno já com monitoria ativa em qualquer disciplina é bloqueado na aprovação. | Pedro | Não | Sim | `backend/monitorias/routes.py`, `backend/monitorias/service.py`, `backend/monitorias/repository.py`, `frontend/templates/monitorias/pending.html`, `docs/adr/0006-admin-aprovacao-indicacao-monitor.md` | Controle de aprovação de monitores pelo admin — completa o ciclo do EP02 |
