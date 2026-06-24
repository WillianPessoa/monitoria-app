# Critérios de Aceitação — Monitoria App

Formato: **BDD (Given / When / Then)** para histórias de usuário — base da Validação Paralela do QM.  
Tarefas técnicas (TT) usam checklist — não são comportamentos de usuário.

---

## EP00 — Infraestrutura e Setup

### TT01 — Definir e documentar a stack
- [ ] Framework Python escolhido e documentado (Flask, FastAPI ou Django)
- [ ] Versão do Python definida e registrada
- [ ] Versão do MySQL definida e registrada
- [ ] Documento disponível no repositório em `docs/`

### TT02 — Modelar banco de dados
- [ ] Diagrama ER criado com as entidades principais: Usuário, Disciplina, Vínculo de Monitoria, Disponibilidade, Agendamento, Registro de Atendimento
- [ ] Script SQL de criação do schema (`schema.sql`) disponível no repositório
- [ ] Relacionamentos e chaves estrangeiras definidos e revisados pelo QM
- [ ] Tipos de dados e constraints (NOT NULL, UNIQUE) explicitados

### TT03 — Configurar ambiente de desenvolvimento local
- [ ] Guia de setup documentado (README ou `docs/setup.md`)
- [ ] Cobre: instalação do Python, MySQL, dependências e variáveis de ambiente
- [ ] Qualquer membro do time consegue rodar o projeto do zero seguindo o guia, sem ajuda verbal
- [ ] Testado em ao menos dois ambientes diferentes

### TT04 — Criar estrutura base do projeto (skeleton)
- [ ] Estrutura de pastas definida e criada
- [ ] Servidor sobe sem erros e responde a uma rota de saúde (`GET /health` → 200)
- [ ] Dependências listadas em `requirements.txt` com versões fixadas
- [ ] `.gitignore` configurado para Python e variáveis de ambiente

### TT05 — Configurar conexão da aplicação com MySQL
- [ ] Aplicação conecta ao banco na inicialização
- [ ] Configuração de banco via variável de ambiente (não hardcoded)
- [ ] Erro de conexão é logado de forma clara no console
- [ ] Conexão funciona no ambiente de todos os membros do time

---

## EP01 — Perfis e Autenticação

### US01 — Admin cadastra usuários com perfis

**Cenário 1: Cadastro bem-sucedido**
```
Given: admin autenticado na tela de gestão de usuários
When:  preenche nome, email e papel (aluno/monitor/professor/admin) e confirma
Then:  usuário é criado com status "Pendente" e senha temporária é exibida ao admin
```

**Cenário 2: Email duplicado**
```
Given: admin tenta cadastrar um email que já existe no sistema
When:  confirma o cadastro
Then:  sistema rejeita com mensagem "Email já cadastrado"
```

**Cenário 3: Campos obrigatórios ausentes**
```
Given: admin está na tela de cadastro de usuário
When:  tenta confirmar sem preencher nome, email ou papel
Then:  sistema impede o envio e aponta o campo faltando
```

---

### US02 — Usuário faz login com email e senha

**Cenário 1: Login bem-sucedido**
```
Given: usuário com status "Ativo" na tela de login
When:  informa email e senha corretos
Then:  é autenticado e redirecionado para a tela correspondente ao seu papel
```

**Cenário 2: Credenciais inválidas**
```
Given: usuário na tela de login
When:  informa email ou senha incorretos
Then:  sistema exibe mensagem de erro genérica sem revelar qual campo está errado
```

**Cenário 3: Primeiro acesso (status Pendente)**
```
Given: usuário com status "Pendente" na tela de login
When:  informa email e senha temporária corretos
Then:  é redirecionado para a tela de troca de senha obrigatória
```

**Cenário 4: Usuário inativo**
```
Given: usuário com status "Inativo" na tela de login
When:  informa credenciais corretas
Then:  login é negado com mensagem de que a conta está inativa
```

---

## EP02 — Cadastro de Disciplinas e Monitores

### US06 — Admin cadastra disciplinas

**Cenário 1: Cadastro bem-sucedido**
```
Given: admin autenticado na tela de gestão de disciplinas
When:  preenche nome, código e seleciona professor responsável e confirma
Then:  disciplina é criada e aparece imediatamente na listagem
```

**Cenário 2: Código duplicado**
```
Given: admin tenta cadastrar uma disciplina com código já existente
When:  confirma o cadastro
Then:  sistema rejeita com mensagem de código duplicado
```

**Cenário 3: Professor inválido**
```
Given: admin tenta associar usuário sem papel "professor" como responsável
When:  confirma o cadastro
Then:  sistema rejeita com mensagem de papel inválido
```

---

### US07 — Professor indica aluno como monitor

**Cenário 1: Indicação bem-sucedida**
```
Given: professor autenticado na tela de uma das suas disciplinas
When:  seleciona um aluno e confirma a indicação como monitor
Then:  vínculo é criado com status "Pendente de aprovação"
```

**Cenário 2: Indicação de usuário sem papel aluno**
```
Given: professor tenta indicar usuário que não tem papel "aluno"
When:  confirma a indicação
Then:  sistema rejeita com mensagem de papel inválido
```

**Cenário 3: Disciplina de outro professor**
```
Given: professor autenticado
When:  tenta criar indicação para disciplina que não é de sua responsabilidade
Then:  a disciplina não aparece nas opções disponíveis para ele
```

---

### US08 — Admin aprova ou rejeita indicação de monitor

**Cenário 1: Aprovação**
```
Given: admin visualiza indicação com status "Pendente de aprovação"
When:  aprova a indicação
Then:  vínculo muda para "Ativo" e o aluno passa a ter acesso como monitor da disciplina
```

**Cenário 2: Rejeição com motivo**
```
Given: admin visualiza indicação com status "Pendente de aprovação"
When:  rejeita informando o motivo
Then:  vínculo muda para "Rejeitado" e o motivo é registrado
```

**Cenário 3: Indicação processada sai da fila**
```
Given: admin aprova ou rejeita uma indicação
When:  retorna à lista de pendentes
Then:  a indicação processada não aparece mais na lista
```

---

## EP03 — Agenda e Agendamento

### US10 — Monitor cria horários de atendimento

**Cenário 1: Criação bem-sucedida**
```
Given: monitor autenticado na sua agenda
When:  informa data, horário de início, horário de fim e local e confirma
Then:  bloco aparece na agenda como disponível para agendamento
```

**Cenário 2: Horários sobrepostos**
```
Given: monitor já tem um horário das 14h às 16h em uma data
When:  tenta criar outro horário das 15h às 17h na mesma data
Then:  sistema rejeita com mensagem de sobreposição de horário
```

**Cenário 3: Data no passado**
```
Given: monitor na tela de criação de horários
When:  tenta criar horário com data anterior ao dia atual
Then:  sistema rejeita com mensagem de data inválida
```

---

### US11 — Aluno vê horários disponíveis de um monitor

**Cenário 1: Busca por disciplina**
```
Given: aluno autenticado na tela de busca de monitoria
When:  seleciona uma disciplina
Then:  sistema exibe lista de horários disponíveis com nome do monitor, data, horário e local
```

**Cenário 2: Horário lotado não aparece**
```
Given: horário de um monitor já tem agendamento confirmado
When:  aluno busca horários disponíveis desse monitor
Then:  o horário com agendamento não aparece na listagem
```

**Cenário 3: Horário passado não aparece**
```
Given: horário de atendimento cuja data já passou
When:  aluno busca horários disponíveis
Then:  o horário passado não aparece na listagem
```

---

### US12 — Aluno agenda um horário disponível

**Cenário 1: Agendamento bem-sucedido**
```
Given: aluno visualiza horário disponível na listagem
When:  confirma o agendamento
Then:  agendamento é criado, horário sai da listagem de disponíveis e aparece na agenda do monitor
```

**Cenário 2: Conflito de horário do aluno**
```
Given: aluno já tem agendamento confirmado em um determinado horário
When:  tenta agendar outro atendimento no mesmo período
Then:  sistema rejeita com mensagem de conflito de horário
```

---

### US13 — Monitor vê agenda com agendamentos confirmados

**Cenário 1: Visualização da agenda**
```
Given: monitor autenticado
When:  acessa sua agenda
Then:  visualiza todos os horários criados, diferenciando visualmente os que têm agendamento dos que estão livres
```

**Cenário 2: Dados do agendamento**
```
Given: monitor visualiza horário com agendamento na agenda
When:  acessa o detalhe do agendamento
Then:  sistema exibe nome do aluno, data e horário do atendimento
```

---

## EP04 — Registro de Atendimentos e Bolsas

### US16 — Monitor registra presença ou ausência do aluno

**Cenário 1: Registro de presença**
```
Given: horário de um agendamento já passou
When:  monitor registra o aluno como "presente"
Then:  registro é salvo no histórico e contabilizado no total de horas do monitor
```

**Cenário 2: Registro de ausência**
```
Given: horário de um agendamento já passou
When:  monitor registra o aluno como "ausente"
Then:  registro é salvo no histórico mas não contabilizado no total de horas
```

**Cenário 3: Registro antes do horário**
```
Given: agendamento com horário ainda no futuro
When:  monitor tenta registrar presença ou ausência
Then:  sistema rejeita com mensagem de que o horário ainda não chegou
```

---

### US18 — Admin vê total de horas de monitoria por monitor no mês

**Cenário 1: Painel de horas**
```
Given: admin autenticado no painel de controle de bolsas
When:  acessa o relatório do mês corrente
Then:  sistema exibe total de horas por monitor com destaque para quem está abaixo de 1h semanal
```

**Cenário 2: Filtro por disciplina**
```
Given: admin no painel de horas
When:  filtra por uma disciplina específica
Then:  sistema exibe apenas os monitores vinculados àquela disciplina
```

**Cenário 3: Apenas sessões com presença contam**
```
Given: monitor tem 3 agendamentos no mês — 2 com registro "presente" e 1 com "ausente"
When:  admin consulta o total de horas desse monitor
Then:  sistema contabiliza apenas as 2 sessões com presença confirmada
```

---

## EP05 — Relatórios e Notificações

### US20 — Admin gera relatório de participação por disciplina

**Cenário 1: Geração do relatório**
```
Given: admin seleciona uma disciplina e um período
When:  solicita a geração do relatório
Then:  sistema exibe relatório com total de sessões realizadas, alunos atendidos, horas realizadas e monitores ativos
```

**Cenário 2: Exportação**
```
Given: admin visualiza relatório gerado
When:  solicita exportação
Then:  arquivo PDF ou CSV é gerado e disponibilizado para download
```

---

### US21 — Aluno recebe confirmação ao agendar

**Cenário 1: Flash message após agendamento**
```
Given: aluno que acabou de reservar um horário disponível
When:  o agendamento é confirmado pelo sistema
Then:  aluno vê mensagem de confirmação com data, hora e nome do monitor
```

**Cenário 2: Agendamento persiste na agenda**
```
Given: aluno que confirmou um agendamento
When:  acessa a seção "Horários agendados" na agenda
Then:  o agendamento aparece listado com data, hora, monitor e local
```

---

### US22 — Lembrete visual para atendimentos próximos

**Cenário 1: Badge de lembrete exibido**
```
Given: aluno com agendamento confirmado nas próximas 24 horas
When:  acessa a tela de agenda
Then:  sistema exibe badge "Hoje/Amanhã" no agendamento próximo com data e hora
```

**Cenário 2: Sem agendamentos próximos**
```
Given: aluno sem agendamentos nas próximas 24 horas
When:  acessa a tela de agenda
Then:  nenhum badge de lembrete é exibido
```

---

### US24 — Aluno vota em horário preferido para sessão semanal

**Cenário 1: Voto bem-sucedido**
```
Given: aluno matriculado na disciplina com votação aberta para a semana
When:  seleciona uma ou duas opções de horário e confirma
Then:  voto é registrado e aluno vê mensagem de confirmação de sucesso
```

**Cenário 2: Número de opções excedido**
```
Given: votação configurada para máximo de 1 opção
When:  aluno tenta enviar mais de uma opção selecionada
Then:  sistema rejeita com mensagem indicando o limite permitido
```

**Cenário 3: Votação indisponível**
```
Given: disciplina sem votação aberta na semana corrente
When:  aluno tenta votar
Then:  sistema rejeita com mensagem de votação indisponível
```

**Cenário 4: Aluno sem matrícula na disciplina**
```
Given: usuário sem matrícula na disciplina
When:  tenta registrar voto
Then:  sistema rejeita com erro de permissão
```

---

### US25 — Monitor configura carga horária e confirma horário semanal

**Cenário 1: Configurar carga de 1 hora**
```
Given: monitor autenticado com votação aberta na semana
When:  define carga horária como 1 hora e salva
Then:  opções de 1h são geradas para votação dos alunos
```

**Cenário 2: Configurar carga de 2h consecutivas**
```
Given: monitor autenticado com votação aberta
When:  define 2 horas no modo CONSECUTIVAS
Then:  opções são geradas como blocos de 2h seguidas
```

**Cenário 3: Configurar carga de 2h separadas**
```
Given: monitor autenticado com votação aberta
When:  define 2 horas no modo SEPARADAS
Then:  alunos podem selecionar dois horários distintos na mesma semana
```

**Cenário 4: Confirmar com votos suficientes**
```
Given: votação aberta com ≥50% dos alunos matriculados tendo votado
When:  monitor seleciona horário(s) e confirma
Then:  sessão(ões) de monitoria são criadas na semana corrente e votação é encerrada
```

**Cenário 5: Confirmar sem votos suficientes**
```
Given: votação com menos de 50% dos alunos tendo votado
When:  monitor tenta confirmar
Then:  sistema rejeita com mensagem de votos insuficientes
```

**Cenário 6: Monitor sem permissão**
```
Given: usuário que não é o monitor ativo da disciplina
When:  tenta configurar ou confirmar a votação
Then:  sistema rejeita com erro de permissão
```

---

### US26 — Aluno confirma ou cancela presença em sessão coletiva

**Cenário 1: Confirmação de presença**
```
Given: aluno matriculado com sessão de monitoria futura na semana
When:  confirma presença na sessão
Then:  status CONFIRMADA é registrado e exibido na página da disciplina
```

**Cenário 2: Marcação de ausência**
```
Given: aluno matriculado com sessão de monitoria futura
When:  registra ausência
Then:  status AUSENTE é registrado
```

**Cenário 3: Cancelamento com antecedência**
```
Given: aluno com presença CONFIRMADA em sessão com mais de 6 horas de antecedência
When:  cancela a presença
Then:  status volta para AUSENTE e aluno vê mensagem de confirmação
```

**Cenário 4: Cancelamento fora do prazo**
```
Given: sessão ocorre em menos de 6 horas
When:  aluno tenta cancelar presença confirmada
Then:  sistema rejeita com mensagem "Cancelamento não permitido com menos de 6 horas de antecedência"
```

**Cenário 5: Sessão já começou**
```
Given: sessão com data_inicio no passado
When:  aluno tenta confirmar presença
Then:  sistema rejeita com mensagem de que a sessão já começou
```

**Cenário 6: Aluno sem matrícula**
```
Given: usuário sem matrícula na disciplina
When:  tenta confirmar presença
Then:  sistema rejeita com erro de permissão
```
