# ADR-0002 — Organização do backend: Blueprints por domínio

**Data:** 2026-05-06  
**Status:** Aceito

## Contexto

Com Flask, a estrutura do projeto é definida pelo time. A alternativa mais comum é MVC clássico (models/, views/, controllers/), mas o projeto tem épicos bem separados por domínio.

## Decisão

**Blueprint por domínio.** Cada épico do backlog corresponde a um blueprint Flask:

```
backend/
├── app.py
├── auth/          ← EP01 — login, sessão, primeiro acesso
├── usuarios/      ← EP01 — CRUD de usuários (admin)
├── disciplinas/   ← EP02 — disciplinas e vínculos de monitoria
├── agenda/        ← EP03 — disponibilidade e agendamentos
├── registros/     ← EP04 — presença e bolsas
└── relatorios/    ← EP05 — relatórios e notificações
```

Cada blueprint contém suas próprias rotas (`routes.py`), lógica de negócio (`service.py`) e queries (`repository.py`).

## Justificativa

- Divisão natural com os épicos do backlog — cada dev pode trabalhar em um blueprint sem conflito
- O QM sabe exatamente onde olhar ao revisar uma história
- Evita o problema do MVC clássico: abrir três pastas diferentes para mexer em uma funcionalidade

## Consequências

- `app.py` registra os blueprints e configura a aplicação
- Rotas de cada blueprint têm prefixo de URL correspondente (ex: `/agenda/`, `/usuarios/`)
- Models de banco de dados podem ser compartilhados entre blueprints via módulo `db/`
