# ADR-0005 — Frontend: Jinja2 + fetch seletivo

**Data:** 2026-05-06  
**Status:** Aceito

## Contexto

O frontend é HTML+CSS puro, sem framework JavaScript. O Flask oferece Jinja2 para renderização server-side. A questão é onde (se em algum lugar) usar JavaScript assíncrono via `fetch`.

## Decisão

**Jinja2 como base para todas as páginas + `fetch` apenas nas telas de agenda e agendamento.**

## Justificativa

- A maioria das telas (login, cadastro, gestão de usuários, relatórios) são formulários e listagens simples — server-side rendering é suficiente e mais simples
- As telas de agenda do monitor e agendamento pelo aluno têm interatividade que torna o reload de página inteira ruim para o usuário (selecionar horário disponível, visualizar calendário)
- Usar `fetch` em todo o frontend sem necessidade adicionaria complexidade sem benefício

## Divisão por tela

| Tela | Abordagem |
|------|-----------|
| Login / logout | Jinja2 + formulário HTML |
| Cadastro e gestão de usuários | Jinja2 + formulário HTML |
| Cadastro de disciplinas | Jinja2 + formulário HTML |
| Indicação e aprovação de monitor | Jinja2 + formulário HTML |
| Agenda do monitor (criar/bloquear horários) | Jinja2 + `fetch` para criar/remover slots sem reload |
| Agendamento pelo aluno (ver e reservar horários) | Jinja2 + `fetch` para reservar sem reload |
| Registro de presença | Jinja2 + formulário HTML |
| Painel de horas e bolsas | Jinja2 |
| Relatórios | Jinja2 |

## Consequências

- RBAC no frontend via Jinja2: `{% if session['papel'] == 'admin' %}` oculta elementos sem permissão
- JavaScript fica restrito a dois arquivos: `static/js/agenda.js` e `static/js/agendamento.js`
- Backend expõe endpoints JSON apenas para as rotas consumidas por `fetch` (ex: `GET /agenda/slots`, `POST /agendamento/reservar`)
- Todas as outras rotas devolvem HTML renderizado pelo Jinja2
