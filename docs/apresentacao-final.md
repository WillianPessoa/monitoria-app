# Apresentação Final — Monitoria App

**Prazo:** semana de 23/06/2026  
**Duração alvo:** 30–50 min (objetivo: ocupar o tempo total)  
**Formato:** slides em HTML puro + CSS (arquivo único `apresentacao.html`)  
**Responsável pela criação:** Willian (QM)

---

## Decisões de formato

- **HTML puro + CSS** — sem frameworks JS; navegação por teclado (← →) com CSS `:target`
- Uma seção `<section id="slideN">` por slide
- Estilo minimalista, cores do projeto
- Funciona localmente e online (arquivo único, sem servidor)

---

## Fio narrativo

A apresentação não é um catálogo de features — é a **história de como o produto foi
construído**: as decisões, os problemas reais, o que foi aprendido. O demo mostra o
produto como evidência concreta do que foi feito, não como peça central.

Arco: **contexto → como trabalhamos → o que foi difícil → o produto em funcionamento → o que aprendemos**

---

## Estrutura da apresentação

### Bloco 1 — Quem somos e o que estávamos tentando resolver (5 min)
1. **Capa** — nome do projeto, time, disciplina, data
2. **O time** — apresentação rápida: nome, papel no QScrum (PO, SM, QM, Dev)
3. **O problema** — como funciona a monitoria hoje: WhatsApp, planilha, boca a boca; o que se perde nesse processo
4. **A proposta** — uma frase; print da tela inicial em produção

### Bloco 2 — Como decidimos trabalhar (7 min)
5. **QScrum** — o que é, por que foi escolhido para este projeto, diferença prática para Scrum puro
6. **Papéis e responsabilidades** — o que cada papel fez de concreto (não só o título); destaque para Validação Paralela do QM
7. **A dinâmica real das sprints** — como foi na prática: cerimônias que funcionaram, o que adaptamos, o que abandonamos
8. **Linha do tempo** — Sprint 0 a Sprint 4: o que foi entregue em cada uma (slide visual, não lista)

### Bloco 3 — Como construímos (8 min)
> Foco na execução real: decisões técnicas, problemas encontrados, como foram resolvidos.

9. **As primeiras decisões** — stack (Flask, MySQL, Railway), estrutura de blueprints; por que essas escolhas
10. **Construção sprint a sprint** — o que foi fácil, o que travou; exemplo concreto de US que custou mais do que o esperado
11. **O que funcionou no processo** — ex.: Validação Paralela cortou retrabalho, sprints curtas forçaram entregas reais
12. **O que não funcionou** — ex.: conflito de branches entre sprints, schema em produção sem migration, comunicação assíncrona
13. **Novidades encontradas no caminho** — tecnologias, padrões ou dinâmicas que o time não conhecia antes e aprendeu fazendo

### Bloco 4 — O produto em funcionamento — DEMO AO VIVO (15–18 min)
> Maior bloco. Dados já populados pelo seed script antes da apresentação.
> Cada fluxo é apresentado com referência explícita ao que foi construído ("essa US foi da Sprint X, o critério BDD dizia que…").

14. **Slide de transição "Demo"** — abrir browser com Railway
15. **Fluxo Admin** — cria usuários, cadastra disciplina, aprova indicação de monitor
    - _referência: US01, US06, US08 — Sprint 1 e 2_
16. **Fluxo Professor** — indica aluno como monitor
    - _referência: US07 — Sprint 2_
17. **Fluxo Monitor** — cria horários, vê agenda com agendamentos confirmados
    - _referência: US10, US13 — Sprint 3_
18. **Fluxo Aluno** — busca horários, agenda atendimento
    - _referência: US11, US12 — Sprint 3_
19. **Fluxo de Registros** — monitor registra presença; admin vê relatório de horas e participação
    - _referência: US16, US18, US20 — Sprint 4_
20. **Slide de transição "Voltando"**

### Bloco 5 — Qualidade: como garantimos que funciona (5 min)
21. **Validação Paralela na prática** — o fluxo: Dev entrega → QM valida critério BDD → aprovado ou retorna; exemplo real de um bug encontrado nesse processo
22. **Critérios BDD** — mostrar um cenário do documento; conectar com o que foi visto no demo
23. **Testes automatizados** — o que foi coberto, como o seed script popula produção para demo

### Bloco 6 — O que aprendemos e para onde vai (5 min)
24. **Aprendizados técnicos** — Flask sem ORM, MySQL em produção, Railway, Jinja2
25. **Aprendizados de processo** — QScrum na prática de uma equipe pequena; o que cada membro levaria para o próximo projeto
26. **Próximos passos do produto** — notificações por email (US21–US23); o que ficou fora do escopo e por quê
27. **Obrigado / Perguntas**

---

## Checklist de preparação

### Slides
- [ ] Criar `docs/apresentacao.html` com CSS de slides (seções `:target`)
- [ ] Preencher todos os 24 slides com conteúdo
- [ ] Adicionar screenshots reais da aplicação (tirar do Railway antes)
- [ ] Testar navegação e timing (ensaio cronometrado)

### Demo ao vivo
- [ ] Rodar `seed_production.py` para popular Railway com dados realistas
- [ ] Testar o fluxo completo de demo no Railway antes da apresentação
- [ ] Preparar aba do browser com Railway já aberto e logado como admin
- [ ] Ter credenciais de cada papel disponíveis (tabela no slide de "Demo")

### Conteúdo
- [ ] Confirmar com o time os pontos que cada membro vai apresentar
- [ ] Fazer ensaio cronometrado — alvo 40 min (deixa margem para perguntas)

---

## Divisão sugerida de apresentação por membro

| Bloco | Quem | Tempo |
|---|---|---|
| Bloco 1 — Contexto e problema | João Pedro (SM) | 5 min |
| Bloco 2 — Como decidimos trabalhar | João Pedro (SM) | 7 min |
| Bloco 3 — Como construímos | Gabriel, Pedro ou Gustavo | 8 min |
| Bloco 4 — Demo ao vivo | Willian (QM) ou Gustavo | 16 min |
| Bloco 5 — Qualidade | Willian (QM) | 5 min |
| Bloco 6 — Aprendizados + Fechamento | Todo o time | 5 min |

> No bloco 6, cada membro fala brevemente o seu aprendizado principal — distribui
> a voz e dá mais peso humano ao encerramento.

---

## Referências

- Critérios de aceitação: `docs/criterios-de-aceitacao.md`
- Estratégia de testes: `docs/testes/estrategia-tt07.md`
- Seed de produção: `backend/scripts/seed_production.py`
- Produção: https://web-production-1f724.up.railway.app
