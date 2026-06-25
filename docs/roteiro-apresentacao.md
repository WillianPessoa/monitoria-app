# Roteiro de conteúdo — Apresentação Monitoria App

> Documento de **orientação**: descreve, para cada slide, **o que deve ter de conteúdo** e **como deve ser apresentado**. Não é código — vira HTML só depois que o conteúdo estiver fechado.
> Direção visual já definida: **Ousado** (blocos de cor, tipografia gigante, número-fantasma), tema **claro + escuro** com toggle, navegação por **teclado + substeps**.
> Cadência: **bloco a bloco**. Status: 🟢 fechado · 🟡 rascunho · ⚪ a preencher.
>
> ✅ **Deck completo implementado** em `apresentacao-ousado.html` (29 slides). Este roteiro é a referência de conteúdo; a fonte da verdade visual agora é o HTML. Conteúdo dos slides 10–29 foi decidido na construção (ver o HTML).

---

## Estrutura (6 blocos)

| # | Bloco | Slide | Status |
|---|---|---|---|
| 1 | Abertura | Capa | 🟢 |
| 2 | 1 · Contexto | O time | 🟢 |
| 3 | 1 · Contexto | O problema (como funciona hoje) | 🟢 |
| 4 | 1 · Contexto | A proposta (abertura + hub) | 🟢 |
| 5–8 | 1 · Contexto | 4 pilares da proposta | 🟢 |
| 9 | 2 · Processo | QScrum | 🟢 |
| 10 | 2 · Processo | Papéis e responsabilidades | 🟢 |
| 11 | 2 · Processo | A dinâmica real das sprints | 🟢 |
| 12 | 2 · Processo | Linha do tempo (S0–S5) | 🟢 |
| 13–16 | 3 · Construção | Decisões · fácil/travou · funcionou · não funcionou | 🟢 |
| 17 | 4 · Demo | Transição + credenciais | 🟢 |
| 18–22 | 4 · Demo | Fluxos Admin · Professor · Monitor · Aluno · Relatórios | 🟢 |
| 23 | 5 · Qualidade | Validação Paralela (diagrama) | 🟢 |
| 24 | 5 · Qualidade | Critérios BDD | 🟢 |
| 25 | 5 · Qualidade | Testes automatizados (stats) | 🟢 |
| 26–28 | 6 · Aprendizados | Técnicos · processo · próximos passos | 🟢 |
| 29 | Encerramento | Obrigado / perguntas | 🟢 |

---

# BLOCO 1 · CONTEXTO

## Slide 1 — Capa 🟢

**O que comunica:** abertura — o que é o produto e o enquadramento da apresentação.

**Conteúdo:**
- Marca: **MonitoriaApp**
- Tagline (título gigante): *Monitoria acadêmica, do jeito certo.*
- Subtítulo: Sistema web de gestão de monitoria — Flask · MySQL · Jinja2, em produção no Railway.
- Kicker: Apresentação final · Projeto de grupo
- Meta (4 itens): Disciplina = Oficina de Eng. de Software · Processo = QScrum · Status = ● Em produção · Sprints = S0 → S5

**Como apresentar:** tipografia gigante ocupando a tela, blob de cor no canto, palavra "acadêmica" destacada na cor primária. Meta numa linha inferior. Sóbrio mas marcante.

---

## Slide 2 — O time 🟢

**O que comunica:** quem fez, com os papéis do QScrum — todos com o mesmo peso.

**Conteúdo:** título "Quem construiu." + 6 cards — **só nome + papel** (sem descrição do que cada um fez):

| Pessoa | Papel |
|---|---|
| Bruna & Thais | Product Owner |
| João Pedro Bianco | Scrum Master |
| Willian G. Pessoa | Quality Manager |
| Pedro Chaves | Desenvolvedor |
| Gabriel Benevides | Desenvolvedor |
| Gustavo Blandy | Desenvolvedor |

**Como apresentar:** grade 3×2 de cards, **uma cor distinta por pessoa**, mesmo tamanho/destaque (ninguém apagado, nenhum nome em evidência). Cada card = avatar com iniciais + nome + papel. Cards limpos, sem texto descritivo — o foco é nome e papel.

---

## Slide 3 — O problema (como funciona a monitoria hoje) 🟢

**O que comunica:** a dor antes do sistema — por que ele precisa existir.

**Conteúdo:**
- Enquadramento (1 linha, no topo): hoje a monitoria roda em ferramentas soltas.
- As 3 ferramentas atuais, **sinalizadas por imagem** (não por texto). Cada uma é uma imagem reconhecível, com a falha apenas como legenda curtíssima embaixo:
  - **WhatsApp** (imagem: balão de conversa / ícone do WhatsApp) — legenda: "agendamentos que se perdem".
  - **Planilha Excel** (imagem: grade de planilha / ícone do Excel) — legenda: "presença no manual".
  - **Boca a boca** (imagem: pessoas conversando / balões de fala) — legenda: "sem alcance garantido".
- O que se perde com isso (consequências — texto, em slide ou metade separada):
  - Aluno "achou que tinha marcado" — sem confirmação.
  - Sem histórico de atendimentos para o professor.
  - Professor sem visibilidade (quantos alunos foram atendidos?).
  - Monitor sem controle (difícil bloquear horário / ver agenda).
  - Admin sem dados (quem é monitor de quê fica em e-mail).

**Como apresentar:** as 3 ferramentas dominam o slide como **3 imagens grandes** lado a lado (ícones/ilustrações), cada uma com uma marca visual de "isso falha" (ex.: traço/X sutil, ou em tom dessaturado). Quase sem texto — a imagem carrega a mensagem; a legenda é só uma âncora. As consequências entram menores embaixo ou no slide seguinte.

**Imagens (decidido):** ícones/SVGs, **logos reais liberados** — usar os logos oficiais do WhatsApp e do Excel (como SVG) e um ícone para "boca a boca" (balões de fala). Manter coerência de tamanho entre os três.

**Divisão (decidido):** **um slide só** — 3 imagens grandes em cima, consequências menores embaixo.

---

## Slide 4 — A proposta (abertura) 🟢

**O que comunica:** a virada — um sistema único que centraliza tudo.

**Conteúdo:**
- Frase-âncora: *Um sistema web que centraliza agendamentos, registros e relatórios de monitoria.*
- Os 4 papéis que ele conecta: Admin · Professor · Monitor · Aluno.

**Como apresentar:** slide de respiro, frase grande no centro/esquerda + **hub SVG** (núcleo central ligado aos 4 papéis, com linhas animadas). Serve de "porta de entrada" para os 4 pilares seguintes. (Decidido: slide próprio.)

---

## Slides 5–8 — Os 4 pilares da proposta 🟢

**O que comunica:** as 4 capacidades centrais do produto, uma por slide, com bastante destaque.

**Como apresentar (padrão para os 4):** layout "pilar" Ousado — índice grande (01/04…04/04), título gigante, descrição em 1–2 linhas, tags, e um **SVG ilustrativo** próprio à direita. Número-fantasma de fundo.

**Pilar 01 — Agenda online**
- Descrição: o monitor cria horários (slots); o aluno agenda em poucos cliques; confirmação na hora, sem "achismo".
- Tags: Slots · Agendamento · Confirmação
- SVG: grade de horários com um slot destacado.

**Pilar 02 — Controle de presença**
- Descrição: o monitor registra quem compareceu e o assunto tratado em cada atendimento.
- Tags: Presença · Assunto · Sessão
- SVG: lista com checkmarks.

**Pilar 03 — Relatórios automáticos**
- Descrição: admin vê horas por monitor; professor vê histórico e participação — sem planilha manual.
- Tags: Horas · Participação · Histórico
- SVG: gráfico de barras.

**Pilar 04 — Fluxo de indicação**
- Descrição: professor indica um aluno, admin aprova, monitor começa — fluxo formal e rastreável.
- Tags: Professor → Admin → Monitor
- SVG: três caixas ligadas por setas.

**Ordem (decidido):** Agenda online → Controle de presença → Relatórios automáticos → Fluxo de indicação.

---

# BLOCO 2 · PROCESSO

## Slide 9 — QScrum 🟢

**O que comunica:** o processo que o time usou — Scrum com um papel a mais, focado em qualidade.

**Conteúdo:**
- Definição: QScrum = Scrum + um papel adicional, o **Quality Manager (QM)**.
- Mantém o ritmo do Scrum: sprints semanais, daily (assíncrona), planning e review.
- O diferencial: cada US tem **critérios BDD escritos antes** da implementação; o ciclo é Dev entrega → QM valida o critério BDD → merge autorizado.
- Por que muda o jogo (vs. Scrum puro):
  - QM valida **independente** do Dev que implementou.
  - Bug pego antes do merge não chega em produção.
  - Testes automatizados são condição de aprovação, não opcional.
  - Critério BDD vira linguagem comum entre PO, Dev e QM.

**Como apresentar (decidido — visão equilibrada):** título gigante "QScrum". Duas frentes lado a lado — "O que é" e "Por que muda o jogo" — apresentadas de forma balanceada, com o QM como um dos elementos (sem puxar a sardinha pro papel nem personalizar em ninguém). Mini-fluxo visual Dev → QM → merge.

## Slide 10 — Papéis e responsabilidades ⚪

(a preencher)

## Slide 11 — A dinâmica real das sprints ⚪

(a preencher)

## Slide 12 — Linha do tempo 🟡

**O que comunica:** a evolução do projeto, sprint a sprint.

**Como apresentar:** mostra a timeline inteira (S0–S5); cada → foca um sprint com texto grande + número-fantasma. Conteúdo por sprint:

| Sprint | Datas | Foco | Tags |
|---|---|---|---|
| S0 Fundação | 30/04–06/05 | Infra antes de qualquer US (repo, Flask, Docker MySQL, Railway). | Setup · Schema |
| S1 EP01 | 07–13/05 | Usuários e autenticação — 1ª entrega no ar. | US01–US05 |
| S2 EP02 | 14–20/05 | Disciplinas e indicação (professor → admin → monitor). | US06–US09 |
| S3 EP03 | 21–27/05 | Agenda e atendimentos. | US10–US15 |
| S4 EP04 | 28/05–19/06 | Registros e relatórios. | US16–US20 |
| S5 Entrega | 20–24/06 | Extras, testes e apresentação. | US21–US26 · 308 testes |

---

# Próximos blocos (a preencher juntos)

- ⚪ **Bloco 3 · Construção** — Decisões (stack) · fácil/travou · o que funcionou · o que não funcionou
- ⚪ **Bloco 4 · Demo ao vivo** — transição + credenciais + 5 fluxos (iframe da app em produção)
- ⚪ **Bloco 5 · Qualidade** — Validação Paralela (diagrama) · BDD · Testes (stats)
- ⚪ **Bloco 6 · Aprendizados** — técnicos · processo · próximos passos · encerramento
