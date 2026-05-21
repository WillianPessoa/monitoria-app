# Relatório Parcial — Sprint 2

**Número da Sprint:** 2

**Data da Entrega:** 20/05/2026

---

## Perguntas Gerais

**Qual foi o tempo médio das reuniões Daily Stand-Up desta semana?**

Houve uma Daily presencial em aula no dia 14/05, com duração aproximada de 10 minutos. Nos demais dias, o acompanhamento ocorreu de forma assíncrona via grupo do WhatsApp, com cada membro reportando o andamento das suas tarefas. Não houve outras reuniões formais de Daily ao longo da semana.

**Houve levantamento de questões técnicas pela equipe antes de iniciarem o desenvolvimento das tarefas? Se sim, quantas e quais?**

Não foram levantadas questões técnicas formais antes do início do desenvolvimento. As dúvidas foram resolvidas de forma assíncrona conforme surgiram durante a implementação.

**Houve tarefas rejeitadas pelo Product Owner por erro de interpretação ou execução incorreta? Se sim, quantas e quais?**

Não houve tarefas rejeitadas pelo Product Owner.

**Bugs foram identificados na entrega final ou durante as revisões semanais? Se sim, quantos e quais?**

Não foram identificados bugs funcionais nas histórias entregues. O QM identificou um problema de integração: a branch da US09 (Admin lista monitorias ativas) foi desenvolvida de forma isolada e não foi integrada à branch principal antes do encerramento da sprint, impossibilitando sua entrega. A tarefa foi devolvida ao Sprint Backlog.

**Como se deu o levantamento de dúvidas e compartilhamento de conhecimento durante a sprint?**

O compartilhamento de conhecimento ocorreu de forma assíncrona via WhatsApp e por revisão direta do código entre os membros.

**Quantidade de Tarefas Planejadas:** 4 (US06, US07, US08, US09)

**Quantidade de Tarefas Concluídas (Done):** 3 (US06, US07, US08)

**Outras Observações:**

O Sprint Goal da Sprint 2 — "O admin consegue cadastrar disciplinas e o professor consegue indicar um monitor, que é aprovado pelo admin" — foi atingido. As três histórias centrais do EP02 (US06, US07, US08) foram implementadas e estão funcionando no ambiente de produção (Railway). A US09 não foi integrada a tempo e retornou ao Sprint Backlog para a próxima sprint.

---

## Perguntas QScrum

**Flags foram inseridas pelo Quality Manager esta semana?**

Sim. Foram inseridas 4 flags.

- **Quantidade:** 4
- **Motivos:**
  1. Sprint Tales da Sprint 2 não havia sido preenchido ao término do desenvolvimento
  2. Lógica técnica não havia sido formalmente repassada ao QM
  3. US09 entrou em desenvolvimento sem critérios de aceitação definidos (falha no DoR)
  4. Branch da US09 não foi integrada à branch principal antes do encerramento da sprint
- **Tempo entre inserção e resolução:** As flags de documentação (Sprint Tales e lógica técnica) foram resolvidas ao longo do encerramento da sprint. As flags de US09 (DoR e integração) permanecem abertas — a história voltou ao Sprint Backlog com os critérios de aceitação agora definidos pelo QM.

**As Histórias de Usuário foram escritas no formato Given-When-Then? Se sim, o formato auxiliou de alguma forma a compreensão de seu objetivo?**

Sim. As histórias US06, US07 e US08 têm critérios de aceitação no formato BDD (Given / When / Then) no documento `docs/criterios-de-aceitacao.md` e nas respectivas issues do GitHub. O formato auxiliou a identificação de cenários de borda — em particular, o cenário de "professor inválido" em US06 e o cenário de "aluno já monitor em outra disciplina" em US08, que poderiam ter sido ignorados sem a formalização dos critérios.

**O Quality Manager validou as tarefas através do checklist do Definition of Ready?**

Sim. O QM aplicou o checklist do DoR nas tarefas. A flag referente à US09 decorreu exatamente dessa validação — a história não possuía critérios de aceitação e não deveria ter entrado em desenvolvimento. Os critérios foram definidos retroativamente pelo QM, e a história retornou ao Sprint Backlog.

---

## Artefatos

- [x] Sprint Tales atualizado — `docs/sprint-tales/sprint-2.md`
- [x] Explicação da lógica técnica repassada ao Quality Manager
- [x] Sprint Backlog atualizado — issues #11, #12, #13, #14 no GitHub Projects
- [x] Evidências da Sprint Review — US06, US07 e US08 testadas e funcionando no Railway
- [ ] Board da Retrospectiva Sprint 2 — a realizar
- [x] Relatório parcial — este documento
