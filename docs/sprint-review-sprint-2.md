# Evidências da Sprint Review — Sprint 2

**Projeto:** Monitoria App
**Sprint:** 2 — Cadastro do Domínio Principal
**Data:** 20/05/2026
**Local:** Sala de aula
**QM:** Willian Gomes Pessoa

---

## Participantes

- Bruna (Product Owner / Monitora)
- Thais (Product Owner / Monitora)
- Willian Gomes Pessoa (Quality Manager)
- João Pedro Bianco
- Pedro Chaves
- Gabriel dos Reis Benevides
- Gustavo Blandy de Oliveira

---

## Formato da Reunião

A Sprint Review foi realizada em sala de aula ao final do Sprint 2, com a presença das Product Owners (monitoras Bruna e Thais) e de todos os integrantes do time. A demonstração foi feita a partir da aplicação publicada no Railway (https://web-production-1f724.up.railway.app). A reunião foi seguida pela Sprint Retrospective no formato Easy Retro.

---

## Meta da Sprint

> O admin consegue cadastrar disciplinas e o professor consegue indicar um monitor, que é aprovado pelo admin.

**Resultado:** Meta atingida. Todos os 5 itens comprometidos foram entregues.

---

## O Que Foi Demonstrado

### TT06 — Aplicação no Railway

Demonstração do acesso à URL pública (https://web-production-1f724.up.railway.app). Todos os membros e as POs conseguem acessar o sistema sem depender do ambiente local de nenhum desenvolvedor.

### US06 — Cadastro de disciplinas

Demonstração do fluxo completo pelo admin: criação de disciplina com código, nome e professor responsável; validação de código duplicado; ativação e desativação; matrícula de alunos individual e em lote por lista de emails.

### US07 — Indicação de monitor pelo professor

Demonstração do fluxo pelo professor: acesso à tela de indicação exibindo apenas as disciplinas do próprio professor; seleção de aluno e confirmação; indicação aparecendo com status "Pendente de aprovação" no histórico.

### US08 — Aprovação de indicação pelo admin

Demonstração pelo admin: fila de indicações pendentes; aprovação de indicação criando o vínculo ativo; rejeição com motivo; tentativa de aprovar aluno já monitor em outra disciplina sendo bloqueada pelo sistema.

### US09 — Listagem de monitorias ativas

Demonstração da tabela de monitorias ativas na tela de gestão de disciplinas, exibindo disciplina, monitor e professor responsável para cada vínculo ativo.

---

## Feedback das Product Owners

A demonstração foi aceita pelas POs. Não houve rejeição de histórias. Durante a sprint review, a PO Bruna identificou uma lacuna no escopo de agendamento para a Sprint 3: o sistema precisaria cobrir o cancelamento de agendamento confirmado pelo monitor, com regra de antecedência de 6 horas. A história foi registrada como US16-novo (issue #33) e adicionada ao backlog.

---

## Resultado

Sprint 2 encerrada com aprovação das Product Owners. 5 de 5 itens entregues (100%). Sprint Goal atingido.

---

## Retrospectiva — Easy Retro

Na sequência da Sprint Review, o time conduziu a Retrospectiva no formato Easy Retro (4 colunas).

**O que foi bem**

- Entregamos as histórias centrais da sprint (US06, US07, US08) com o sistema funcionando em produção.
- Corrigimos o problema de execução local identificado na Sprint 1 — ambiente Docker estável para todos os membros.

**O que pode melhorar**

- Organização das branches — membros trabalharam em branches isoladas sem partir da branch principal, gerando conflitos de integração (caso US09).
- Tarefas precisam ter deadlines específicos dentro da sprint — sem data interna, o trabalho se concentrou no último dia.

**Action Items**

- Criar uma branch única de desenvolvimento (`dev`) a partir da qual todos partem e para a qual todos abrem PRs — já implementado ao final desta sprint.
- Definir no início da sprint um prazo máximo por tarefa correspondente a uma fração do período total da sprint, evitando acúmulo no final.

**O que nos deixa em dúvida**

- US09 foi desenvolvida mas não integrada a tempo — o processo de abertura de PR precisa ser parte do fluxo de trabalho, não uma etapa opcional.
- A ausência de Sprint Tales e repasse de lógica técnica ao QM gerou flags que atrasaram o fechamento das histórias; o time precisa incorporar esses passos como parte do desenvolvimento, não como burocracia pós-entrega.
