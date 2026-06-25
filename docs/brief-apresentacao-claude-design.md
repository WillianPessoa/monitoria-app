# Brief de estilo — Apresentação Monitoria App (para o Claude Design)

> Texto para passar ao Claude Design. Foca em **contexto, estilo e elementos estruturais** — não no conteúdo dos slides (o conteúdo já existe e será reaproveitado). O pedido central é: **redesenhar a apresentação** corrigindo os problemas abaixo, e **entregar variações** da direção visual para eu escolher.

---

## 1. Contexto

- É a **apresentação final** de um projeto de grupo da disciplina *Oficina de Engenharia de Software* (UFRJ — Instituto de Computação).
- O produto apresentado é o **Monitoria App**: um sistema web de monitoria acadêmica (Flask + MySQL + Jinja2/CSS puro), com app real em produção no Railway.
- Formato: **deck HTML de slide único** (um arquivo `.html`, sem build, sem framework JS — CSS puro com navegação por `:target` + um pouco de JS vanilla). Manter esse formato.
- A apresentação é **falada ao vivo por um humano** diante de uma turma + professor. Os slides são apoio visual, não documento de leitura.
- Existe uma versão atual (`docs/apresentacao.html`, 27 slides, tema escuro) que **eu não gostei**. Os problemas estão na seção 3. Use-a como referência do que NÃO repetir, não como base a preservar.

## 2. Onde vai ser exibida (crítico para o design)

- **Tela de referência: MacBook 2560×1600 Retina (proporção 16:10).** Desenhe pensando nessa tela.
- A exibição real será em **projetor ou TV (16:9)**. Portanto:
  - O conteúdo deve **preencher a tela inteira** — nada de grandes faixas vazias / margens mortas. Hoje sobra muito espaço (ver problema 3.3).
  - Garanta que nada crítico seja cortado num **16:9**: trate o canvas como fluido / full-viewport e teste em 1920×1080 (16:9) e 2560×1600 (16:10).
- **Legibilidade a distância** é prioridade: numa projeção, texto pequeno some. Veja problema 3.1.

## 3. Problemas da versão atual a corrigir (estes são os requisitos)

1. **Fontes pequenas demais.** Aumentar a escala tipográfica de forma geral — corpo, rótulos, números. Pensar em legibilidade de projetor, não de monitor a 50 cm.
2. **Densidade / hierarquia ruim em slides "narrativos".** Slides como "Como funciona a monitoria hoje" e "A proposta" estão apertados e ao mesmo tempo com espaço sobrando — texto pequeno num bloco e vazio em volta. Quero:
   - **Quebrar slides densos em vários slides** com texto maior e respiração. Ex.: a "proposta" (hoje 4 pilares num grid pequeno) poderia virar **4 slides separados**, um por pilar, com texto grande e uma **ilustração SVG** pertinente em cada. O mesmo vale para "como funciona a monitoria".
3. **Slides não usam o espaço.** Vários slides têm muito vazio. Quero composições que **preencham a tela** — conteúdo aproveitando a área toda, sem buracos.
4. **Igualdade do time (importante).** Hoje meu nome (Willian, QM) aparece destacado e os desenvolvedores aparecem "apagados" / em cinza, como se fossem menos importantes. **Errado.** Quero:
   - **Todos os membros com o mesmo peso visual** — devs não devem ficar apagados, eles são importantes.
   - Diferenciação **apenas por cor** (uma cor por pessoa ou por papel), não por destaque/opacidade.
   - Nada de tratar meu nome como "estrela" da apresentação.
5. **Navegação por teclado (setas ←/→) precisa funcionar de forma confiável.** A versão atual tem um esboço disso mas não funciona bem. Setas devem sempre andar entre slides (inclusive cobrindo o caso do foco estar num iframe de demo).
6. **Tema duplo (claro + escuro).** Hoje é só escuro. Quero **os dois temas completos, de primeira classe, com toggle visível** — não um principal e outro secundário. Ambos devem casar com a aplicação (paletas na seção 5). O claro importa especialmente porque, num projetor, o escuro pode "não aparecer"; mas os dois devem ficar igualmente caprichados. O toggle deve estar acessível durante a apresentação e, idealmente, lembrar a escolha.
7. **A linha do tempo (timeline) está ruim.** Hoje é uma trilha pequena com cards que trocam. Quero outro comportamento:
   - **Mostrar a timeline inteira primeiro** (visão geral de todas as etapas/sprints).
   - Depois, ao avançar, **percorrer step a step**, dando **destaque total a cada etapa** (a etapa ativa cresce/foca, texto grande), em vez de cards minúsculos lado a lado.

## 4. Elementos estruturais que existem hoje (mantê-los, mas redesenhar — e quero variações de cada)

Não precisa do conteúdo de cada um — só saiba que estes "tipos de slide" existem e devem ser repensados visualmente:

1. **Capa / encerramento** — título do projeto, identidade, lista do time.
2. **Slide de time** — 5 papéis (SM, QM, 3 Devs) + PO. (Ver requisito de igualdade 3.4.)
3. **Slides narrativos** — problema atual, proposta, processo (QScrum), decisões técnicas, "o que funcionou / não funcionou", aprendizados. São os que precisam virar mais slides + maiores + com SVGs (3.2).
4. **Timeline de sprints** — 6 etapas (Sprint 0 a 5). Reformular conforme 3.7.
5. **Bloco de demo ao vivo** — 5 slides que embutem a **app real em produção via `<iframe>`** (cada um focado num fluxo: Admin, Professor, Monitor, Aluno, Relatórios), + 1 slide de credenciais de acesso. **Manter a integração por iframe** — é parte central da apresentação.
6. **Diagrama de fluxo (SVG)** — fluxo de "Validação Paralela" (Dev → QM → aprovado/bug). Manter como diagrama vetorial, redesenhar.
7. **Bloco de código BDD** — um cenário Given/When/Then estilizado como código. Manter o tratamento "monospace/código".
8. **Estatísticas / números grandes** + **barras de cobertura animadas** (números de testes por épico).
9. **Slides de transição** entre blocos (divisores de seção).

**Para cada um desses, quero ver variações de abordagem visual** — não uma única proposta fechada.

## 5. Sistema visual

### Tipografia (manter — casa com a aplicação)
- Títulos/numéricos: **Space Grotesk**.
- Corpo/rótulos: **Manrope**.
- Código/BDD: monospace (SF Mono / Fira Mono / Consolas).
- **Mas aumentar toda a escala** (requisito 3.1).

### Paleta — TEMA ESCURO (atual da app)
```
bg gradient : radial-gradient(1100px 700px at 15% -10%, #0a1b2e, #050d18)
card        : #0d1626
surface2    : #0a1322
border      : rgba(125,211,252,0.10)
text        : #e6eef6
muted       : #8da0b0
primary     : #4fd1c5   (teal)
accent      : #7dd3fc   (azul claro)
success     : #34d399
warning     : #fbbf24
error       : #fb7185
```

### Paleta — TEMA CLARO (igual ao `data-theme='light'` da app — usar este para o tema claro)
```
bg gradient : linear-gradient(180deg, #f4f7fb, #eaf0f7)
card        : #ffffff
surface2    : #f1f5fa
border      : rgba(13,40,71,0.10)
shadow      : 0 8px 24px rgba(13,40,71,0.08)
text        : #0c1a2b
muted       : #5b6b7a
primary     : #0e9c8e   (teal escuro p/ contraste em branco)
success     : #0f9d6b
warning     : #a86a00
error       : #e11d48
```

### Cores por membro do time (sugestão — diferenciar por cor, peso igual)
Use cores distintas da paleta para os 5 papéis (ex.: primary, accent, success, warning, e uma neutra forte) **sem** rebaixar ninguém para cinza apagado.

## 6. Restrições técnicas

- **Um único arquivo `.html`**, autossuficiente. Sem bundler, sem React/Vue, sem dependências de build.
- Navegação: CSS `:target` + JS vanilla mínimo (teclado, animações de barra, timeline, troca de tema, iframe da demo).
- Fontes via Google Fonts (já em uso).
- A demo embute `https://web-production-1f724.up.railway.app` via iframe — manter o mecanismo.
- Deve abrir direto no navegador (file:// ou servidor estático), sem passos extras.

## 7. O que eu quero de volta

- **Variações da direção visual** (não uma única proposta) — especialmente para: capa, slide de time, timeline e os slides narrativos.
- Tipografia maior e composições que **preencham a tela**.
- **Tema duplo (claro + escuro)**, ambos completos e com toggle, fiéis à app.
- **Navegação por setas funcionando.**
- Timeline com o comportamento "ver tudo → focar etapa a etapa".
- Sugestões de **SVGs ilustrativos** para os slides narrativos quebrados.

> O conteúdo textual de cada slide eu passo depois / aproveito do deck atual. Aqui o foco é **a linguagem visual e a estrutura**.
