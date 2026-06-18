# Evidências da Sprint Review — Sprint 1

**Projeto:** Monitoria App  
**Sprint:** 1 — Perfis e Autenticação  
**Data:** 13/05/2026  
**Local:** Sala de aula  
**QM:** Willian Gomes Pessoa

---

## Participantes

- Bruna (Project Owner / Monitora)
- Thais (Project Owner / Monitora)
- Willian Gomes Pessoa (Quality Manager)
- João Pedro Bianco
- Pedro Chaves
- Gabriel dos Reis Benevides
- Gustavo Blandy de Oliveira

---

## Formato da Reunião

A Sprint Review foi realizada em sala de aula ao final da Sprint 1, com a presença das Product Owners (monitoras Bruna e Thais) e de todos os integrantes do time. A demonstração foi seguida pela Sprint Retrospective, conduzida no formato Easy Retro (registrada em `docs/retrospectivas/sprint-1.md`).

---

## Meta da Sprint

> O time consegue criar um usuário com perfil e fazer login no sistema.

**Resultado:** Meta atingida. Todas as histórias Must e Should foram entregues.

---

## O Que Foi Demonstrado

### Infraestrutura (EP00)

- **TT01 — Stack:** Apresentação das tecnologias escolhidas (Python 3.12, Flask 3.0.3, MySQL 8.0) e justificativas técnicas documentadas em `docs/stack.md`.
- **TT02 — Modelagem do banco:** Exibição do schema SQL com as 4 tabelas criadas (`usuarios`, `password_reset_tokens`, `disciplinas`, `monitorias`) e do diagrama ER.
- **TT03 — Ambiente local:** Demonstração do guia de setup com Docker Compose e script de criação do admin.
- **TT04 — Skeleton:** Apresentação da estrutura de blueprints e resposta da rota `GET /health` com HTTP 200.
- **TT05 — Conexão MySQL:** Connection pool funcionando, configuração por variáveis de ambiente, sem credenciais no código.

### Autenticação e Perfis (EP01)

- **US01 — Cadastro de usuários:** Demonstração do fluxo completo — admin cria usuário, senha temporária gerada e exibida na tela, usuário criado com status PENDENTE.
- **US02 — Login:** Demonstração dos quatro cenários: login bem-sucedido com redirecionamento por papel; credenciais inválidas com mensagem genérica; primeiro acesso com troca de senha obrigatória; login negado para usuário inativo.
- **US03 — Edição de perfil:** Monitor atualiza campos de contato e disponibilidade.
- **US04 — Desativação de usuário:** Admin desativa outro usuário; tentativa de auto-desativação rejeitada pelo sistema.

### Item não entregue

- **US05 — Reset de senha:** Classificado como Could no MoSCoW. Não implementado nesta sprint — postergado. As POs foram informadas e aceitaram a decisão.

---

## Feedback das Product Owners

A demonstração foi aceita pelas POs. Não houve rejeição de histórias. O único ponto levantado foi a ausência de critérios completos de DoR e DoD nas issues do GitHub Projects no início da sprint — registrado como item de melhoria na Retrospectiva.

---

## Resultado

Sprint 1 encerrada com aprovação das Product Owners. 10 de 11 itens entregues (91%). Sprint Goal atingido.

---

## Retrospectiva — Easy Retro

Na sequência da Sprint Review, o time conduziu a Retrospectiva no formato Easy Retro (4 colunas).

**O que foi bem**

- MVP local funcional entregue — backend Flask + autenticação + CRUD de usuários rodando no ambiente local.

**O que foi menos bem**

- Comunicação do time insuficiente ao longo da sprint.
- Pontualidade nas entregas não foi respeitada — tarefas concentradas no final.
- Divisão de tarefas não foi feita de forma clara — responsabilidades ficaram indefinidas.

**O que queremos tentar na próxima sprint**

- Reportar status de progresso em períodos regulares, sem esperar o último dia.
- Definir no GitHub Projects quais stories cada membro ficará responsável antes de começar.
- Realizar daily ao menos uma vez no meio da sprint, além da daily de abertura em aula.

**O que nos deixa em dúvida**

- As tarefas no GitHub ainda carecem de critérios completos de DoR e DoD — sem isso, não há como garantir que uma tarefa está realmente pronta para iniciar ou encerrar.
- Os quadros do GitHub Projects não refletem os compromissos definidos pelo QScrum — os status e colunas precisam ser alinhados ao processo acordado com a professora.
