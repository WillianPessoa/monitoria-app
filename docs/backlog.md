# Backlog Inicial do Produto

**Produto:** Sistema de Monitoria Acadêmica  
**Sprint 0 — 30/04/2026**  
**Priorização:** MoSCoW

---

## Épicos

| ID | Épico | Sprint alvo |
|---|---|:---:|
| EP01 | Perfis e Autenticação | Sprint 1 |
| EP02 | Cadastro de Disciplinas e Monitores | Sprint 2 |
| EP03 | Agenda e Agendamento | Sprint 3 |
| EP04 | Registro de Atendimentos e Bolsas | Sprint 4 |
| EP05 | Relatórios e Notificações | Sprint 5 |

---

## Backlog Completo

### EP01 — Perfis e Autenticação

| ID | Como... | Quero... | Para que... | Prioridade |
|---|---|---|---|:---:|
| US01 | admin | cadastrar usuários com perfis diferentes (aluno, monitor, professor, admin) | cada um acesse apenas o que é permitido | **Must** |
| US02 | usuário | fazer login com email e senha | entrar no sistema | **Must** |
| US03 | monitor | editar meu perfil (contato, disponibilidade) | manter meus dados atualizados | Should |
| US04 | admin | desativar um usuário | remover o acesso de quem saiu do programa | Should |
| US05 | usuário | recuperar minha senha por email | não ficar bloqueado | Could |

### EP02 — Cadastro de Disciplinas e Monitores

| ID | Como... | Quero... | Para que... | Prioridade |
|---|---|---|---|:---:|
| US06 | admin | cadastrar disciplinas com nome, código e professor | organizar o programa | **Must** |
| US07 | professor | indicar um aluno como monitor da minha disciplina | iniciar o vínculo de monitoria | **Must** |
| US08 | admin | aprovar ou rejeitar indicações de monitor | controlar quem entra no programa | **Must** |
| US09 | admin | listar monitorias ativas por disciplina | ter visibilidade do programa | Should |

### EP03 — Agenda e Agendamento

| ID | Como... | Quero... | Para que... | Prioridade |
|---|---|---|---|:---:|
| US10 | monitor | criar horários de atendimento na minha agenda | os alunos saibam quando estou disponível | **Must** |
| US11 | aluno | ver os horários disponíveis de um monitor | escolher quando ser atendido | **Must** |
| US12 | aluno | agendar um horário disponível | garantir minha vaga | **Must** |
| US13 | monitor | ver minha agenda com agendamentos confirmados | me organizar | **Must** |
| US14 | aluno | cancelar um agendamento | liberar o horário se não puder ir | Should |
| US15 | monitor | bloquear um horário da agenda | marcar quando não estou disponível | Should |

### EP04 — Registro de Atendimentos e Bolsas

| ID | Como... | Quero... | Para que... | Prioridade |
|---|---|---|---|:---:|
| US16 | monitor | registrar presença ou ausência do aluno | manter o histórico de atendimentos | **Must** |
| US17 | monitor | registrar o assunto tratado no atendimento | documentar o que foi coberto | Should |
| US18 | admin | ver total de horas de monitoria por monitor no mês | controle de bolsas | **Must** |
| US19 | professor | ver histórico de atendimentos dos monitores da minha disciplina | acompanhar o programa | Should |

### EP05 — Relatórios e Notificações

| ID | Como... | Quero... | Para que... | Prioridade |
|---|---|---|---|:---:|
| US20 | admin | gerar relatório de participação por disciplina | avaliar o impacto do programa | **Must** |
| US21 | aluno | receber confirmação quando agendar | não esquecer o atendimento | Should |
| US22 | aluno | receber lembrete antes do atendimento | não perder o horário | Could |
| US23 | professor | receber relatório mensal por email | acompanhar sem precisar entrar no sistema | Could |

---

## Resumo MoSCoW

| Classificação | Histórias | Total |
|---|---|:---:|
| **Must have** | US01, US02, US06, US07, US08, US10, US11, US12, US13, US16, US18, US20 | 12 |
| **Should have** | US03, US04, US09, US14, US15, US17, US19, US21 | 8 |
| **Could have** | US05, US22, US23 | 3 |

---

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
