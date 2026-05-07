# Critérios de Aceitação — Monitoria App

Referência para o DoR: uma história só entra em Sprint com os critérios abaixo revisados e aprovados pelo QM.

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
- [ ] Estrutura de pastas definida e criada (ex: `routes/`, `models/`, `controllers/` ou equivalente no framework)
- [ ] Servidor sobe sem erros e responde a uma rota de saúde (ex: `GET /health` → 200)
- [ ] Dependências listadas em `requirements.txt` com versões fixadas
- [ ] `.gitignore` configurado para Python e variáveis de ambiente

### TT05 — Configurar conexão da aplicação com MySQL
- [ ] Aplicação conecta ao banco na inicialização
- [ ] Configuração de banco via variável de ambiente (não hardcoded)
- [ ] Erro de conexão é logado de forma clara no console
- [ ] Conexão funciona no ambiente de desenvolvimento de todos os membros do time

---

## EP01 — Perfis e Autenticação

### US01 — Admin cadastra usuários com perfis
- [ ] Admin pode cadastrar usuário informando: nome, email e papel (aluno, monitor, professor, admin)
- [ ] Sistema gera senha temporária aleatória e exibe ao admin no momento do cadastro
- [ ] Usuário criado com status "Pendente" até realizar a troca de senha
- [ ] Tentativa de cadastrar email já existente é rejeitada com mensagem clara
- [ ] Usuário sem papel definido não pode ser cadastrado

### US02 — Usuário faz login com email e senha
- [ ] Login aceita email e senha
- [ ] Credenciais inválidas retornam mensagem de erro sem revelar qual campo está errado
- [ ] Usuário com status "Pendente" é redirecionado para troca de senha obrigatória
- [ ] Usuário com status "Inativo" não consegue fazer login, com mensagem clara
- [ ] Após login bem-sucedido, usuário é redirecionado para a tela correspondente ao seu papel

---

## EP02 — Cadastro de Disciplinas e Monitores

### US06 — Admin cadastra disciplinas
- [ ] Admin pode cadastrar disciplina informando: nome, código e professor responsável
- [ ] Código de disciplina duplicado é rejeitado com mensagem clara
- [ ] Apenas usuários com papel "professor" podem ser associados como responsáveis
- [ ] Disciplina cadastrada aparece imediatamente na listagem
- [ ] Campos obrigatórios (nome e código) não podem ficar em branco

### US07 — Professor indica aluno como monitor
- [ ] Professor autenticado pode indicar um aluno como monitor de uma das suas disciplinas
- [ ] Apenas usuários com papel "aluno" podem ser indicados
- [ ] A indicação cria um vínculo com status "Pendente de aprovação"
- [ ] Professor não pode indicar monitor para disciplina de outro professor
- [ ] Uma disciplina não pode ter duas indicações pendentes para o mesmo aluno

### US08 — Admin aprova ou rejeita indicação de monitor
- [ ] Admin vê lista de indicações com status "Pendente de aprovação"
- [ ] Admin pode aprovar → vínculo muda para "Ativo" e papel do usuário passa a incluir "monitor"
- [ ] Admin pode rejeitar com motivo obrigatório → vínculo muda para "Rejeitado"
- [ ] Indicação aprovada ou rejeitada sai da lista de pendentes
- [ ] Professor pode ver o resultado da indicação no sistema

---

## EP03 — Agenda e Agendamento

### US10 — Monitor cria horários de atendimento
- [ ] Monitor pode criar um bloco de disponibilidade informando: data, horário de início, horário de fim e local (presencial ou link)
- [ ] O sistema rejeita horários sobrepostos com aviso claro
- [ ] Monitor pode ver sua agenda com os blocos criados
- [ ] Não é possível criar horários com data/hora no passado
- [ ] Monitor pode cancelar um horário sem agendamentos vinculados

### US11 — Aluno vê horários disponíveis de um monitor
- [ ] Aluno pode buscar monitores por disciplina
- [ ] Listagem exibe: nome do monitor, data, horário de início/fim e local
- [ ] Apenas horários com vagas disponíveis aparecem
- [ ] Horários com data/hora passada não aparecem na listagem

### US12 — Aluno agenda um horário disponível
- [ ] Aluno pode confirmar um agendamento em horário disponível
- [ ] Agendamento é confirmado imediatamente e horário sai da lista de disponíveis
- [ ] Aluno não pode agendar dois atendimentos no mesmo horário
- [ ] Aluno não pode ter dois agendamentos ativos com o mesmo monitor no mesmo dia
- [ ] Monitor recebe o novo agendamento visível na sua agenda

### US13 — Monitor vê agenda com agendamentos confirmados
- [ ] Monitor vê lista de agendamentos com: nome do aluno, data, horário e local
- [ ] A visualização distingue horários com agendamento dos horários livres
- [ ] Monitor pode ver agendamentos futuros e histórico de passados

---

## EP04 — Registro de Atendimentos e Bolsas

### US16 — Monitor registra presença ou ausência do aluno
- [ ] Após o horário do agendamento, monitor pode registrar: presente, ausente ou cancelado
- [ ] Registro só é possível a partir do horário de início do agendamento
- [ ] Registro fica no histórico do aluno, do monitor e da disciplina
- [ ] Agendamento sem registro após 24h aparece como pendente no painel do monitor

### US18 — Admin vê total de horas de monitoria por monitor no mês
- [ ] Admin vê painel com total de horas realizadas por monitor no mês corrente
- [ ] Painel sinaliza monitores abaixo do mínimo de 1h semanal
- [ ] Apenas sessões com presença registrada ("presente") contam para o total
- [ ] É possível filtrar por disciplina
- [ ] É possível selecionar mês de referência

---

## EP05 — Relatórios e Notificações

### US20 — Admin gera relatório de participação por disciplina
- [ ] Admin pode gerar relatório de uma disciplina informando o período (mês/semestre)
- [ ] Relatório inclui: total de sessões realizadas, total de alunos atendidos, horas realizadas e monitores ativos
- [ ] Relatório pode ser exportado em PDF ou CSV
- [ ] Dados refletem apenas sessões com registro de presença confirmado
