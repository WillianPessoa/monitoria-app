# Revisão de Backlog e Priorização — Sprint 0

**Produto:** Monitoria App  
**Responsável por consolidar:** Willian (QM)  
**Consolidado em:** 06/05/2026

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
| TT01 | Definir e documentar a stack | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| TT02 | Modelar banco de dados | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| TT03 | Configurar ambiente de desenvolvimento local | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| TT04 | Criar estrutura base do projeto (skeleton) | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| TT05 | Configurar conexão com MySQL | Must | ✅ | ✅ | ✅ | ✅ | ✅ |

### EP01 — Perfis e Autenticação

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US01 | Admin cadastra usuários com perfis diferentes (aluno, monitor, professor, admin) | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US02 | Usuário faz login com email e senha | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US03 | Monitor edita seu perfil (contato, disponibilidade) | Should | ✅ | ✅ | ✅ | ✅ | ✅ |
| US04 | Admin desativa um usuário | Should | ✅ | ✅ | ✅ | ✅ | ✅ |
| US05 | Usuário recupera senha por email | Could | ✅ | ✅ | ✅ | Won't | ✅ |

> **US05 — nota de consolidação (Willian/QM):** A recuperação por email foi simplificada e transferida para o admin: o sistema agora gera senha temporária/reset direto na tela de usuarios, sem SMTP.

### EP02 — Cadastro de Disciplinas e Monitores

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US06 | Admin cadastra disciplinas com nome, código e professor | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US07 | Professor indica um aluno como monitor da sua disciplina | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US08 | Admin aprova ou rejeita indicações de monitor | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US09 | Admin lista monitorias ativas por disciplina | Should | ✅ | ✅ | ✅ | ✅ | ✅ |

### EP03 — Agenda e Agendamento

| ID   | História                                           | Atual  | João Pedro | Pedro | Gabriel | Gustavo | Willian |
| ---- | -------------------------------------------------- | :----: | :--------: | :---: | :-----: | :-----: | :-----: |
| US10 | Monitor cria horários de atendimento na agenda     |  Must  |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |
| US11 | Aluno vê horários disponíveis de um monitor        |  Must  |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |
| US12 | Aluno agenda um horário disponível                 |  Must  |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |
| US13 | Monitor vê sua agenda com agendamentos confirmados |  Must  |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |
| US14 | Aluno cancela um agendamento                       | Should |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |
| US15 | Monitor bloqueia um horário da agenda              | Should |     ✅      |   ✅   |    ✅    |    ✅    |    ✅    |

### EP04 — Registro de Atendimentos e Bolsas

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US16 | Monitor registra presença ou ausência do aluno | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US17 | Monitor registra o assunto tratado no atendimento | Should | ✅ | Must | ✅ | ✅ | ✅ |
| US18 | Admin vê total de horas de monitoria por monitor no mês | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US19 | Professor vê histórico de atendimentos dos monitores | Should | ✅ | ✅ | ✅ | ✅ | ✅ |

> **US17 — nota de consolidação (Willian/QM):** Pedro sugeriu elevar para Must, argumentando que sem o registro do assunto o histórico de atendimentos perde valor real para o professor. Time manteve Should — o registro de assunto agrega valor mas o sistema funciona sem ele. Pode ser promovido no Sprint Planning do Sprint 4.

### EP05 — Relatórios e Notificações

| ID | História | Atual | João Pedro | Pedro | Gabriel | Gustavo | Willian |
|----|----------|:-----:|:----------:|:-----:|:-------:|:-------:|:-------:|
| US20 | Admin gera relatório de participação por disciplina | Must | ✅ | ✅ | ✅ | ✅ | ✅ |
| US21 | Aluno recebe confirmação quando agendar | Should | ✅ | ✅ | ✅ | ✅ | ✅ |
| US22 | Aluno recebe lembrete antes do atendimento | Could | ✅ | ✅ | ✅ | ✅ | ✅ |
| US23 | Professor recebe relatório mensal por email | Could | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Parte 2 — Planning Poker

Estime o esforço de cada item (1 · 2 · 3 · 5 · 8 · 13).

### EP00 — Infraestrutura e Setup

| ID | Tarefa | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|--------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| TT01 | Definir e documentar a stack | 2 | 2 | 2 | 1 | 2 | **2** |
| TT02 | Modelar banco de dados | 5 | 8 | 5 | 8 | 8 | **8** |
| TT03 | Configurar ambiente de desenvolvimento local | 3 | 2 | 3 | 2 | 3 | **3** |
| TT04 | Criar estrutura base do projeto (skeleton) | 3 | 5 | 3 | 3 | 5 | **3** |
| TT05 | Configurar conexão com MySQL | 2 | 2 | 3 | 2 | 3 | **2** |

> **TT02 — nota:** Pedro e Gustavo estimaram 8; João Pedro e Gabriel estimaram 5. Após discussão, time convergiu para 8 — o modelo de dados é a fundação de todas as sprints e erros aqui têm custo alto.

### EP01 — Perfis e Autenticação

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US01 | Admin cadastra usuários com perfis diferentes | 5 | 8 | 5 | 8 | 8 | **8** |
| US02 | Usuário faz login com email e senha | 5 | 5 | 8 | 5 | 8 | **5** |
| US03 | Monitor edita seu perfil | 3 | 2 | 2 | 3 | 3 | **3** |
| US04 | Admin desativa um usuário | 2 | 2 | 2 | 2 | 3 | **2** |
| US05 | Usuário recupera senha por email | 8 | 13 | 8 | 13 | 8 | **13** |

> **US01 — nota:** divergência entre 5 e 8. Convergiu para 8 — RBAC com 4 papéis e fluxo de senha temporária é mais complexo do que parece.  
> **US02 — nota:** Gabriel estimou 8 prevendo o fluxo de primeiro acesso (senha temporária). Time convergiu para 5 após esclarecer que o fluxo de primeiro acesso está em US01.  
> **US05 — nota:** A estimativa original considerava SMTP externo; com o fluxo simplificado, a responsabilidade ficou com o admin e a dependência externa foi removida.

### EP02 — Cadastro de Disciplinas e Monitores

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US06 | Admin cadastra disciplinas com nome, código e professor | 3 | 3 | 5 | 3 | 5 | **3** |
| US07 | Professor indica um aluno como monitor | 5 | 5 | 5 | 5 | 8 | **5** |
| US08 | Admin aprova ou rejeita indicações de monitor | 3 | 3 | 5 | 3 | 5 | **3** |
| US09 | Admin lista monitorias ativas por disciplina | 2 | 2 | 2 | 3 | 3 | **2** |

> **US07 — nota:** Willian estimou 8 considerando o controle de papéis e o fluxo de vínculo. Time convergiu para 5 — o fluxo é linear e sem borda complexa.

### EP03 — Agenda e Agendamento

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US10 | Monitor cria horários de atendimento | 8 | 8 | 8 | 5 | 8 | **8** |
| US11 | Aluno vê horários disponíveis de um monitor | 3 | 5 | 3 | 3 | 5 | **3** |
| US12 | Aluno agenda um horário disponível | 5 | 8 | 8 | 5 | 8 | **8** |
| US13 | Monitor vê sua agenda com agendamentos confirmados | 3 | 3 | 3 | 2 | 3 | **3** |
| US14 | Aluno cancela um agendamento | 3 | 2 | 3 | 3 | 3 | **3** |
| US15 | Monitor bloqueia um horário da agenda | 2 | 2 | 2 | 2 | 3 | **2** |

> **US10 — nota:** Gustavo estimou 5; restante estimou 8. Convergiu para 8 — validação de sobreposição de horários tem edge cases que aumentam o esforço.  
> **US12 — nota:** João Pedro e Gustavo estimaram 5; Pedro, Gabriel e Willian estimaram 8. Convergiu para 8 — detecção de conflito de horário do aluno é a parte complexa.

### EP04 — Registro de Atendimentos e Bolsas

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US16 | Monitor registra presença ou ausência do aluno | 3 | 3 | 5 | 3 | 5 | **3** |
| US17 | Monitor registra o assunto tratado no atendimento | 2 | 2 | 2 | 2 | 2 | **2** |
| US18 | Admin vê total de horas de monitoria por monitor no mês | 5 | 8 | 5 | 8 | 8 | **8** |
| US19 | Professor vê histórico de atendimentos dos monitores | 3 | 5 | 3 | 5 | 5 | **5** |

> **US18 — nota:** divergência entre 5 e 8. Convergiu para 8 — agregação mensal com filtros e sinalização de monitores irregulares envolve queries mais complexas do que um CRUD simples.

### EP05 — Relatórios e Notificações

| ID | História | João Pedro | Pedro | Gabriel | Gustavo | Willian | Consenso |
|----|----------|:----------:|:-----:|:-------:|:-------:|:-------:|:--------:|
| US20 | Admin gera relatório de participação por disciplina | 8 | 13 | 13 | 8 | 13 | **13** |
| US21 | Aluno recebe confirmação quando agendar | 5 | 5 | 5 | 5 | 5 | **5** |
| US22 | Aluno recebe lembrete antes do atendimento | 8 | 8 | 8 | 8 | 8 | **8** |
| US23 | Professor recebe relatório mensal por email | 8 | 8 | 8 | 8 | 8 | **8** |

> **US20 — nota:** Pedro, Gabriel e Willian estimaram 13 pela exportação PDF/CSV. João Pedro e Gustavo estimaram 8. Convergiu para 13 — geração de arquivo exportável é uma dependência externa que adiciona complexidade e risco.

---

## Parte 3 — Sugestões de novas histórias

| Como... | Quero... | Para que... | Épico sugerido | Prioridade sugerida |
|---------|----------|-------------|:--------------:|:-------------------:|
| monitor | anexar um arquivo ou link a um registro de atendimento | o material produzido na sessão fique acessível aos alunos da disciplina | EP04 | Should |
| admin | exportar a lista de monitores ativos com suas horas em CSV | facilitar a prestação de contas mensal sem precisar entrar no sistema | EP05 | Could |
