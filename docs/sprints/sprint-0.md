# Sprint 0 — Entregáveis do Grupo

**Time:** Bruna, Thais, João Pedro Bianco, Willian Gomes Pessoa, Pedro Chaves, Gabriel dos Reis Benevides, Gustavo Blandy de Oliveira
**Data:** 30/04/2026

---

## 1. Visão do Produto

**Nome do sistema:** Monitoria App

**Para quem é:** Alunos, monitores, professores e coordenação da universidade.

**Qual problema resolve:**
O programa de monitoria hoje é conduzido de forma desorganizada — horários divulgados em grupos de mensagem, indicações por e-mail e controle de bolsas em planilhas. Isso faz com que alunos não consigam encontrar monitores, monitores não consigam organizar seus atendimentos e professores não tenham dados para acompanhar o impacto da monitoria.

**O que o sistema faz:**
Centraliza toda a gestão do programa de monitoria: cadastro de usuários e disciplinas, criação de agendas pelos monitores, agendamento de atendimentos pelos alunos, registro de presença e geração de relatórios para professores e coordenação.

A coordenação tem acesso a um painel de acompanhamento que mostra se o monitor está de fato realizando atendimentos. Caso um monitor fique sem atividade por um período, o sistema sinaliza isso para que a secretaria possa tomar providências — inclusive a suspensão da bolsa. Dessa forma, o controle de bolsas deixa de ser manual e passa a ser baseado em dados reais do sistema.

**O que está fora do escopo:**
- Integração com sistemas acadêmicos existentes (ex: SIGA)
- App mobile
- Videoconferência integrada

**Product Goal:**
> Ter um sistema que permita ao aluno encontrar um monitor e agendar um atendimento, ao monitor organizar sua agenda e registrar os atendimentos, à coordenação acompanhar a atividade dos monitores e controlar as bolsas — tudo em um único lugar.

---

## 2. Personas

### Persona 1 — Ana, a Aluna
**Perfil:** Aluna do 2º período de Engenharia, com dificuldade em Cálculo II.
**Dores:**
- Não sabe quando vai ter monitoria nem como avisar que não vai conseguir comparecer
- Tem dificuldade de comunicar previamente ao monitor quais são suas dificuldades — não sabe como estruturar isso ou onde registrar
- Quando vai, o monitor muitas vezes não está preparado porque não sabia o que ela precisava
- Quando não pode ir, não tem como acompanhar o que foi visto

**O que ela precisa:** agendar um horário, informar suas dificuldades com antecedência, e — se não puder ir — acessar um registro ou gravação do que foi coberto na monitoria.

---

### Persona 2 — Lucas, o Monitor
**Perfil:** Aluno do 4º período, monitor de Programação I.
**Dores:**
- Não tem como avisar todos os alunos sobre os horários — manda no grupo e poucos veem
- Abre a sala e não vai ninguém, sem aviso prévio
- Não sabe o que os alunos precisam antes do encontro, então não consegue se preparar
- Às vezes resolve um exercício ou grava uma explicação para um aluno específico, mas esse conteúdo fica perdido — deveria estar disponível para todos da disciplina
- Alunos às vezes relatam dificuldades fora da monitoria (por mensagem, por exemplo), mas esse contato não fica registrado em lugar nenhum
- Tem que comprovar as horas para a secretaria, mas o controle é manual

**O que ele precisa:** divulgar horários, saber o que os alunos precisam antes do encontro, e ter um mural por disciplina onde possa postar materiais, resoluções e gravações — tornando o conteúdo produzido na monitoria acessível a todos, não só a quem estava presente.

---

### Persona 3 — Prof. Carlos, o Professor
**Perfil:** Professor de Cálculo II, com alto índice de reprovação na turma.
**Dores:**
- Não tem visibilidade se a monitoria está acontecendo de fato
- Não recebe feedback se os alunos estão melhorando ou se as dúvidas estão sendo resolvidas
- A monitoria deveria ser uma estratégia combinada entre ele e o monitor, mas hoje não tem canal para isso

**O que ele precisa:** acompanhar a frequência da monitoria, receber um resumo do que está sendo coberto e ter algum indicativo de se os alunos estão evoluindo.

---

### Persona 4 — Secretaria / Coordenação
**Perfil:** Responsável pelo controle administrativo do programa de monitoria.
**Dores:**
- Controla tudo em planilha — cruza e-mails, relatórios e frequência manualmente todo mês
- Não tem como saber automaticamente se um monitor está cumprindo a carga mínima semanal
- Liberar ou suspender bolsas é um processo lento e sujeito a erro

**O que ela precisa:** um painel que mostre automaticamente quais monitores cumpriram o mínimo de 1h semanal, com sinalização clara de quem está irregular para tomar providências sobre a bolsa.

---

## 3. Épicos

| ID | Épico | Sprint alvo |
|----|-------|:-----------:|
| EP00 | Infraestrutura e Setup | Sprint 0 |
| EP01 | Perfis e Autenticação | Sprint 1 |
| EP02 | Cadastro de Disciplinas e Monitores | Sprint 2 |
| EP03 | Agenda e Agendamento | Sprint 3 |
| EP04 | Registro de Atendimentos e Bolsas | Sprint 4 |
| EP05 | Relatórios e Notificações | Sprint 5 |

---

## 4. Backlog Inicial

### EP00 — Infraestrutura e Setup

| ID | Tarefa | Prioridade |
|----|--------|:----------:|
| TT01 | Definir e documentar a stack (versão do Python, framework, MySQL) | **Must** |
| TT02 | Modelar banco de dados (usuários, disciplinas, monitores, agendas, atendimentos) | **Must** |
| TT03 | Configurar ambiente de desenvolvimento local (guia para o time) | **Must** |
| TT04 | Criar estrutura base do projeto (skeleton do backend) | **Must** |
| TT05 | Configurar conexão da aplicação com o MySQL | **Must** |

### EP01 — Perfis e Autenticação

| ID | Como... | Quero... | Para que... | Prioridade |
|----|---------|----------|-------------|:----------:|
| US01 | admin | cadastrar usuários com perfis diferentes (aluno, monitor, professor, admin) | cada um acesse apenas o que é permitido | **Must** |
| US02 | usuário | fazer login com email e senha | entrar no sistema | **Must** |
| US03 | monitor | editar meu perfil (contato, disponibilidade) | manter meus dados atualizados | Should |
| US04 | admin | desativar um usuário | remover o acesso de quem saiu do programa | Should |
| US05 | usuário | recuperar minha senha por email | não ficar bloqueado | Could |

### EP02 — Cadastro de Disciplinas e Monitores

| ID | Como... | Quero... | Para que... | Prioridade |
|----|---------|----------|-------------|:----------:|
| US06 | admin | cadastrar disciplinas com nome, código e professor | organizar o programa | **Must** |
| US07 | professor | indicar um aluno como monitor da minha disciplina | iniciar o vínculo de monitoria | **Must** |
| US08 | admin | aprovar ou rejeitar indicações de monitor | controlar quem entra no programa | **Must** |
| US09 | admin | listar monitorias ativas por disciplina | ter visibilidade do programa | Should |

### EP03 — Agenda e Agendamento

| ID | Como... | Quero... | Para que... | Prioridade |
|----|---------|----------|-------------|:----------:|
| US10 | monitor | criar horários de atendimento na minha agenda | os alunos saibam quando estou disponível | **Must** |
| US11 | aluno | ver os horários disponíveis de um monitor | escolher quando ser atendido | **Must** |
| US12 | aluno | agendar um horário disponível | garantir minha vaga | **Must** |
| US13 | monitor | ver minha agenda com agendamentos confirmados | me organizar | **Must** |
| US14 | aluno | cancelar um agendamento | liberar o horário se não puder ir | Should |
| US15 | monitor | bloquear um horário da agenda | marcar quando não estou disponível | Should |

### EP04 — Registro de Atendimentos e Bolsas

| ID | Como... | Quero... | Para que... | Prioridade |
|----|---------|----------|-------------|:----------:|
| US16 | monitor | registrar presença ou ausência do aluno | manter o histórico de atendimentos | **Must** |
| US17 | monitor | registrar o assunto tratado no atendimento | documentar o que foi coberto | Should |
| US18 | admin | ver total de horas de monitoria por monitor no mês | controle de bolsas | **Must** |
| US19 | professor | ver histórico de atendimentos dos monitores da minha disciplina | acompanhar o programa | Should |

### EP05 — Relatórios e Notificações

| ID | Como... | Quero... | Para que... | Prioridade |
|----|---------|----------|-------------|:----------:|
| US20 | admin | gerar relatório de participação por disciplina | avaliar o impacto do programa | **Must** |
| US21 | aluno | receber confirmação quando agendar | não esquecer o atendimento | Should |
| US22 | aluno | receber lembrete antes do atendimento | não perder o horário | Could |
| US23 | professor | receber relatório mensal por email | acompanhar sem precisar entrar no sistema | Could |

---

## 5. Priorização MoSCoW

| Classificação | IDs | Total |
|---------------|-----|:-----:|
| **Must have** | TT01, TT02, TT03, TT04, TT05, US01, US02, US06, US07, US08, US10, US11, US12, US13, US16, US18, US20 | 17 |
| **Should have** | US03, US04, US09, US14, US15, US17, US19, US21 | 8 |
| **Could have** | US05, US22, US23 | 3 |

---

## 6. Setup do Repositório

**Link do repositório:** (preencher após criar no GitHub)

**Stack escolhida:**
- Backend: Python
- Frontend: HTML + CSS
- Banco de dados: MySQL

**Papéis do QScrum:**
| Nome | Papel |
|------|-------|
| Bruna | Product Owner |
| Thais | Product Owner |
| João Pedro Bianco | Scrum Master |
| Willian Gomes Pessoa | Quality Manager |
| Pedro Chaves | Developer |
| Gabriel dos Reis Benevides | Developer |
| Gustavo Blandy de Oliveira | Developer |

---

## 7. Quadro Scrum

**Ferramenta escolhida:** (definir — GitHub Projects ou Trello)

**Link do board:** (preencher)

**Colunas do QScrum:**
| Coluna | Quem usa |
|--------|----------|
| Product Backlog | PO |
| Sprint Backlog | Time |
| Ready for Dev | Dev |
| Dev (In Progress) | Dev |
| Ready for Review | Dev → QM |
| In Review | QM |
| Ready for Deploy | Time |
| Done | Time |
