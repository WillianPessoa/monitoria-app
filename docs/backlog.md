	# Backlog do Produto — Monitoria App

**Priorização:** MoSCoW  
**Sprint 0 — 30/04/2026**

---

## Épicos

| ID | Épico | Sprint alvo |
|---|---|:---:|
| EP00 | Infraestrutura e Setup | Sprint 0 |
| EP01 | Perfis e Autenticação | Sprint 1 |
| EP02 | Cadastro de Disciplinas e Monitores | Sprint 2 |
| EP03 | Agenda e Agendamento | Sprint 3 |
| EP04 | Registro de Atendimentos e Bolsas | Sprint 4 |
| EP05 | Relatórios e Notificações | Sprint 5 |

---

## Backlog Completo

### EP00 — Infraestrutura e Setup

> Tarefas técnicas que habilitam o desenvolvimento. Não seguem o formato de User Story — são pré-requisitos para que as demais histórias funcionem.

| ID | Tarefa | Depende de | Prioridade |
|---|---|---|:---:|
| TT01 | Definir e documentar a stack (versão do Python, framework, MySQL) | — | **Must** |
| TT02 | Modelar banco de dados (usuários, disciplinas, monitores, agendas, atendimentos) | TT01 | **Must** |
| TT03 | Configurar ambiente de desenvolvimento local (guia para o time) | TT01 | **Must** |
| TT04 | Criar estrutura base do projeto (skeleton do backend) | TT01 | **Must** |
| TT05 | Configurar conexão da aplicação com o MySQL | TT02, TT04 | **Must** |

### EP01 — Perfis e Autenticação

| ID | Como... | Quero... | Para que... | Depende de | Prioridade |
|---|---|---|---|---|:---:|
| US01 | admin | cadastrar usuários com perfis diferentes (aluno, monitor, professor, admin) | cada um acesse apenas o que é permitido | TT02, TT04 | **Must** |
| US02 | usuário | fazer login com email e senha | entrar no sistema | TT02, TT04 | **Must** |
| US03 | monitor | editar meu perfil (contato, disponibilidade) | manter meus dados atualizados | US01 | Should |
| US04 | admin | desativar um usuário | remover o acesso de quem saiu do programa | US01 | Should |
| US05 | usuário | recuperar minha senha por email | não ficar bloqueado | US02 | Could |

### EP02 — Cadastro de Disciplinas e Monitores

| ID | Como... | Quero... | Para que... | Depende de | Prioridade |
|---|---|---|---|---|:---:|
| US06 | admin | cadastrar disciplinas com nome, código e professor | organizar o programa | TT02, TT04 | **Must** |
| US07 | professor | indicar um aluno como monitor da minha disciplina | iniciar o vínculo de monitoria | US01, US06 | **Must** |
| US08 | admin | aprovar ou rejeitar indicações de monitor | controlar quem entra no programa | US07 | **Must** |
| US09 | admin | listar monitorias ativas por disciplina | ter visibilidade do programa | US08 | Should |

### EP03 — Agenda e Agendamento

| ID   | Como... | Quero...                                      | Para que...                              | Depende de | Prioridade |
| ---- | ------- | --------------------------------------------- | ---------------------------------------- | ---------- | :--------: |
| US10 | monitor | criar horários de atendimento na minha agenda | os alunos saibam quando estou disponível | US01, TT02 |  **Must**  |
| US11 | aluno   | ver os horários disponíveis de um monitor     | escolher quando ser atendido             | US10       |  **Must**  |
| US12 | aluno   | agendar um horário disponível                 | garantir minha vaga                      | US10, US11 |  **Must**  |
| US13 | monitor | ver minha agenda com agendamentos confirmados | me organizar                             | US10       |  **Must**  |
| US14 | aluno   | cancelar um agendamento                       | liberar o horário se não puder ir        | US12       |   Should   |
| US15 | monitor | bloquear um horário da agenda                 | marcar quando não estou disponível       | US10       |   Should   |
| US16-novo | monitor | cancelar uma sessão de monitoria confirmada | reagendar quando houver imprevistos | US25 | **Must** |
| US24 | aluno | votar em horário preferido para a sessão semanal de monitoria | o monitor possa confirmar o horário mais conveniente | US07/US08, US06 | **Must** |
| US25 | monitor | configurar a carga horária semanal e confirmar o horário mais votado | os alunos saibam quando a sessão ocorrerá | US24, US10 | **Must** |
| US26 | aluno | confirmar ou cancelar minha presença em sessão coletiva de monitoria | o monitor saiba quantos alunos comparecerão | US24/US25, US06 | Should |

### EP04 — Registro de Atendimentos e Bolsas

| ID | Como... | Quero... | Para que... | Depende de | Prioridade |
|---|---|---|---|---|:---:|
| US16 | monitor | registrar presença ou ausência do aluno | manter o histórico de atendimentos | US12 | **Must** |
| US17 | monitor | registrar o assunto tratado no atendimento | documentar o que foi coberto | US16 | Should |
| US18 | admin | ver total de horas de monitoria por monitor no mês | controle de bolsas | US16 | **Must** |
| US19 | professor | ver histórico de atendimentos dos monitores da minha disciplina | acompanhar o programa | US16 | Should |

### EP05 — Relatórios e Notificações

| ID   | Como...   | Quero...                                       | Para que...                               | Depende de | Prioridade |
| ---- | --------- | ---------------------------------------------- | ----------------------------------------- | ---------- | :--------: |
| US20 | admin     | gerar relatório de participação por disciplina | avaliar o impacto do programa             | US16, US18 |  **Must**  |
| US21 | aluno     | receber confirmação quando agendar             | não esquecer o atendimento                | US12       |   Should   |
| US22 | aluno     | receber lembrete antes do atendimento          | não perder o horário                      | US21       |   Could    |
| US23 | professor | receber relatório mensal por email             | acompanhar sem precisar entrar no sistema | US20       |   Could    |

---

## Resumo MoSCoW

| Classificação | IDs | Total |
|---|---|:---:|
| **Must have** | TT01, TT02, TT03, TT04, TT05, US01, US02, US06, US07, US08, US10, US11, US12, US13, US16, US16-novo, US18, US20, US24, US25 | 20 |
| **Should have** | US03, US04, US09, US14, US15, US17, US19, US21, US26 | 9 |
| **Could have** | US05, US22 | 2 |
| **Won't do** | US23 | 1 |

---

> Os critérios de aceitação de cada história estão em [`docs/criterios-de-aceitacao.md`](criterios-de-aceitacao.md).

## Definition of Ready (DoR)

Uma história está pronta para entrar em Sprint quando:
- [ ] Está escrita no formato "Como... quero... para que..."
- [ ] Tem critérios de aceitação definidos
- [ ] Não tem ambiguidades identificadas pelo QM
- [ ] Dependências com sprints anteriores estão claras
- [ ] O time consegue estimar o esforço

## Definition of Done (DoD)

Uma história está pronta quando:
- [ ] O código foi escrito e atende aos critérios de aceitação
- [ ] Não há Flags pendentes do Quality Manager
- [ ] O dev explicou a lógica técnica ao QM
- [ ] O QM atualizou o Sprint Tales
