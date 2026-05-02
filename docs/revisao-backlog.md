# Revisão de Backlog e Priorização — Sprint 0

**Produto:** Monitoria App  
**Responsável por consolidar:** Willian (QM)

---

## Como preencher

**Parte 1 — Revisão do MoSCoW**  
O backlog já tem uma classificação inicial. Para cada história, coloque na sua coluna:
- ✅ se concordar com a classificação atual
- A nova classificação se discordar (ex: `Should`) — pode adicionar um comentário ao lado

**Parte 2 — Planning Poker**  
Estime o esforço de cada história usando a escala abaixo. **Preencha sem ver a estimativa dos outros** — é importante que a sua opinião seja independente.

| Valor | Significa |
|:-----:|-----------|
| 1 | Trivial — menos de 1h |
| 2 | Simples — algumas horas |
| 3 | Pequeno — menos de 1 dia |
| 5 | Médio — 1 a 2 dias |
| 8 | Grande — vários dias, tem incerteza |
| 13 | Muito grande — precisa ser quebrado |

**Parte 3 — Sugestões**  
Se você acha que falta alguma história, adicione ao final.

Mande suas respostas para o Willian assim que puder.

---

## Parte 1 — Revisão do MoSCoW

### EP00 — Infraestrutura e Setup

> Tarefas técnicas — sem formato de User Story. Avaliem se concordam com a prioridade e se falta alguma tarefa técnica.

| ID | Tarefa | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|--------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| TT01 | Definir e documentar a stack | Must | | | | | |
| TT02 | Modelar banco de dados | Must | | | | | |
| TT03 | Configurar ambiente de desenvolvimento local | Must | | | | | |
| TT04 | Criar estrutura base do projeto (skeleton) | Must | | | | | |
| TT05 | Configurar conexão com MySQL | Must | | | | | |

### EP01 — Perfis e Autenticação

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US01 | Admin cadastra usuários com perfis diferentes (aluno, monitor, professor, admin) | Must | | | | | |
| US02 | Usuário faz login com email e senha | Must | | | | | |
| US03 | Monitor edita seu perfil (contato, disponibilidade) | Should | | | | | |
| US04 | Admin desativa um usuário | Should | | | | | |
| US05 | Usuário recupera senha por email | Could | | | | | |

### EP02 — Cadastro de Disciplinas e Monitores

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US06 | Admin cadastra disciplinas com nome, código e professor | Must | | | | | |
| US07 | Professor indica um aluno como monitor da sua disciplina | Must | | | | | |
| US08 | Admin aprova ou rejeita indicações de monitor | Must | | | | | |
| US09 | Admin lista monitorias ativas por disciplina | Should | | | | | |

### EP03 — Agenda e Agendamento

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US10 | Monitor cria horários de atendimento na agenda | Must | | | | | |
| US11 | Aluno vê horários disponíveis de um monitor | Must | | | | | |
| US12 | Aluno agenda um horário disponível | Must | | | | | |
| US13 | Monitor vê sua agenda com agendamentos confirmados | Must | | | | | |
| US14 | Aluno cancela um agendamento | Should | | | | | |
| US15 | Monitor bloqueia um horário da agenda | Should | | | | | |

### EP04 — Registro de Atendimentos e Bolsas

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US16 | Monitor registra presença ou ausência do aluno | Must | | | | | |
| US17 | Monitor registra o assunto tratado no atendimento | Should | | | | | |
| US18 | Admin vê total de horas de monitoria por monitor no mês | Must | | | | | |
| US19 | Professor vê histórico de atendimentos dos monitores | Should | | | | | |

### EP05 — Relatórios e Notificações

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US20 | Admin gera relatório de participação por disciplina | Must | | | | | |
| US21 | Aluno recebe confirmação ao agendar | Should | | | | | |
| US22 | Aluno recebe lembrete antes do atendimento | Could | | | | | |
| US23 | Professor recebe relatório mensal por email | Could | | | | | |

---

## Parte 2 — Planning Poker

Estime o esforço de cada item (1 · 2 · 3 · 5 · 8 · 13).

### EP00 — Infraestrutura e Setup

| ID | Tarefa | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|--------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| TT01 | Definir e documentar a stack | | | | | | |
| TT02 | Modelar banco de dados | | | | | | |
| TT03 | Configurar ambiente de desenvolvimento local | | | | | | |
| TT04 | Criar estrutura base do projeto (skeleton) | | | | | | |
| TT05 | Configurar conexão com MySQL | | | | | | |

### EP01 — Perfis e Autenticação

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US01 | Admin cadastra usuários com perfis diferentes | | | | | | |
| US02 | Usuário faz login com email e senha | | | | | | |
| US03 | Monitor edita seu perfil | | | | | | |
| US04 | Admin desativa um usuário | | | | | | |
| US05 | Usuário recupera senha por email | | | | | | |

### EP02 — Cadastro de Disciplinas e Monitores

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US06 | Admin cadastra disciplinas com nome, código e professor | | | | | | |
| US07 | Professor indica um aluno como monitor | | | | | | |
| US08 | Admin aprova ou rejeita indicações de monitor | | | | | | |
| US09 | Admin lista monitorias ativas por disciplina | | | | | | |

### EP03 — Agenda e Agendamento

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US10 | Monitor cria horários de atendimento | | | | | | |
| US11 | Aluno vê horários disponíveis de um monitor | | | | | | |
| US12 | Aluno agenda um horário disponível | | | | | | |
| US13 | Monitor vê sua agenda com agendamentos confirmados | | | | | | |
| US14 | Aluno cancela um agendamento | | | | | | |
| US15 | Monitor bloqueia um horário da agenda | | | | | | |

### EP04 — Registro de Atendimentos e Bolsas

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US16 | Monitor registra presença ou ausência do aluno | | | | | | |
| US17 | Monitor registra o assunto tratado no atendimento | | | | | | |
| US18 | Admin vê total de horas de monitoria por monitor no mês | | | | | | |
| US19 | Professor vê histórico de atendimentos dos monitores | | | | | | |

### EP05 — Relatórios e Notificações

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US20 | Admin gera relatório de participação por disciplina | | | | | | |
| US21 | Aluno recebe confirmação ao agendar | | | | | | |
| US22 | Aluno recebe lembrete antes do atendimento | | | | | | |
| US23 | Professor recebe relatório mensal por email | | | | | | |

---

## Parte 3 — Sugestões de novas histórias

Se você acha que falta alguma história no backlog, descreva abaixo:

| Como... | Quero... | Para que... | Épico sugerido | Prioridade sugerida |
|---------|----------|-------------|:--------------:|:-------------------:|
| | | | | |
| | | | | |
| | | | | |
