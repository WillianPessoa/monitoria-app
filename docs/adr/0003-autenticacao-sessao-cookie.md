# ADR-0003 — Autenticação: sessão com cookie

**Data:** 2026-05-06  
**Status:** Aceito

## Contexto

O sistema precisa autenticar usuários e controlar acesso por papel (RBAC). As opções avaliadas foram JWT e sessão com cookie.

## Decisão

**Sessão com cookie via `flask.session`.**

## Justificativa

- O frontend é HTML+CSS puro com formulários nativos — o browser envia o cookie automaticamente em cada request, sem JavaScript adicional
- JWT exigiria armazenar e enviar o token manualmente em cada request, o que só faz sentido com um SPA (React, Vue, etc.)
- `flask.session` é assinado com a chave secreta da aplicação — seguro sem infraestrutura extra
- Mais simples de implementar, debugar e entender para o time

## Implementação

- Login bem-sucedido: `session['user_id']` e `session['papel']` são gravados
- Logout: `session.clear()`
- RBAC no servidor: decorator `@requer_papel('admin')` verifica `session['papel']` antes de executar a rota
- RBAC no frontend: Jinja2 verifica `session['papel']` para ocultar elementos sem permissão (ex: `{% if papel == 'admin' %}`)

## Consequências

- Sessão é stateful no servidor — escala horizontal requer session store compartilhado (não é o caso neste projeto)
- Tempo de expiração da sessão configurável via `PERMANENT_SESSION_LIFETIME` no Flask
- Cookie deve ter `HttpOnly=True` e `Secure=True` em produção
