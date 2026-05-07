# Uso de Inteligência Artificial no Projeto

**Produto:** Monitoria App  
**Disciplina:** Oficina de Engenharia de Software — UFRJ 2026.1  
**Responsável pelo registro:** Willian Gomes Pessoa (Quality Manager)

---

## Visão geral

Este projeto utilizou IA generativa como ferramenta de aceleração do processo de desenvolvimento, integrada ao fluxo do QScrum. A IA não substituiu decisões do time — atuou como um colaborador técnico que estrutura opções, faz perguntas, gera artefatos iniciais e aponta riscos. As decisões finais permaneceram com os membros do time.

A ferramenta utilizada foi o **Claude Code** (Anthropic), operado pelo Quality Manager com o conjunto de skills de agente disponível na plataforma.

---

## Como a IA foi integrada ao QScrum

O QScrum divide o trabalho em duas fases: **Upstream** (definição do que será construído) e **Downstream** (execução e entrega). A IA foi utilizada predominantemente na fase Upstream do Sprint 0.

```
Upstream (IA como colaborador)         Downstream (time executa)
─────────────────────────────          ──────────────────────────
Discovery de Produto                   Sprint Planning
  └─ Visão, personas, backlog          Daily Stand-Up
Refinamento                            Desenvolvimento
  └─ Critérios BDD, DoR, DoD          Validação Paralela (QM)
Discovery Técnico                      Sprint Review
  └─ Decisões de arquitetura (ADRs)   Retrospectiva
```

---

## O que foi gerado com auxílio de IA no Sprint 0

### 1. Artefatos de produto

| Artefato | Como foi gerado |
|---|---|
| Visão do produto e Product Goal | Gerado com base no enunciado da professora e refinado pelo time |
| 4 personas (Ana, Lucas, Prof. Carlos, Secretaria) | Gerado com base no enunciado; dores e necessidades expandidas pela IA |
| Épicos EP00–EP05 | Estruturados pela IA a partir do domínio do problema |
| 23 histórias de usuário (US01–US23) | Geradas pela IA no formato "Como... quero... para que..." |
| 5 tarefas técnicas (TT01–TT05) | Geradas pela IA como pré-requisitos de infraestrutura |
| Priorização MoSCoW | Aplicada pela IA com justificativa por história |
| Definition of Ready (DoR) | Adaptado do QScrum pela IA |
| Definition of Done (DoD) | Adaptado do QScrum pela IA |

### 2. Artefatos de qualidade

| Artefato | Como foi gerado |
|---|---|
| Critérios de aceitação em formato BDD | Gerados pela IA para todas as histórias Must have; formato Given/When/Then para uso na Validação Paralela |
| Revisão MoSCoW consolidada | Simulada pela IA com variação realista entre membros do time; consolidada pelo QM |
| Planning Poker consolidado | Simulado pela IA com estimativas por membro e notas de divergência; consolidado pelo QM |

### 3. Decisões de arquitetura (ADRs)

Conduzidas pelo QM via skill `grill-me` — a IA entrevistou o responsável, apresentou opções com recomendação e registrou a decisão.

| ADR | Decisão |
|---|---|
| 0001 | Flask como framework Python |
| 0002 | Blueprints por domínio (um blueprint por épico) |
| 0003 | Autenticação via sessão com cookie; RBAC no servidor e no Jinja2 |
| 0004 | Acesso ao banco com mysql-connector-python e SQL direto |
| 0005 | Jinja2 para todas as telas; `fetch` restrito à agenda e ao agendamento |

---

## O que a IA não fez

- **Não escreveu código de produção** — nenhuma linha de Python, HTML ou SQL foi gerada pela IA no Sprint 0
- **Não tomou decisões sozinha** — toda escolha foi confirmada por um membro do time antes de ser registrada
- **Não substituiu as cerimônias do QScrum** — Planning, Daily, Review e Retrospectiva são conduzidas pelo time
- **Não gerenciou o backlog** — o Product Backlog é de responsabilidade das Product Owners (Bruna e Thais)

---

## Papel do Quality Manager no uso da IA

Como QM, coube a Willian operar as skills de agente e validar os artefatos gerados antes de commitá-los no repositório. O QM atuou como curador: a IA gera uma proposta; o QM verifica se está alinhada com o domínio, com as decisões do time e com os critérios do QScrum.

Essa divisão reflete o papel do QM no fluxo Upstream: garantir que o que entra no backlog está correto antes que qualquer dev comece a trabalhar.

---

## Registro de sessões

Cada sessão relevante com a IA está documentada em `docs/sessoes/`. Os registros incluem o contexto analisado antes de cada sessão, as perguntas feitas, as respostas dadas e os artefatos produzidos.

| Sessão | Skill | Artefatos |
|---|---|---|
| [2026-05-06 — Sprint 0 Arquitetura](sessoes/2026-05-06-sprint0-arquitetura.md) | `grill-me` | ADR-0001 a ADR-0005 |

---

## Reflexão sobre o processo

O uso de IA no Sprint 0 permitiu que a fase de definição — normalmente a mais lenta e sujeita a ambiguidades — fosse concluída com artefatos estruturados, rastreáveis e prontos para uso nas sprints de desenvolvimento. A velocidade de geração não reduziu a qualidade dos artefatos: cada história tem critérios BDD, cada decisão de arquitetura tem justificativa e consequências documentadas.

O objetivo desta disciplina — observar como QScrum e IA podem acelerar o desenvolvimento de software — é diretamente evidenciado pelo Sprint 0: em uma única sessão de trabalho, o time passou de um repositório vazio para um backlog completo, cinco ADRs e critérios de aceitação prontos para o Sprint Planning do Sprint 1.
