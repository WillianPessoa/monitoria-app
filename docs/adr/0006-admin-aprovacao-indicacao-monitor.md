# ADR-0006 — Admin aprova ou rejeita indicações de monitor

**Data:** 2026-05-20  
**Status:** Aceito

## Contexto

O projeto já suportava usuários com papéis distintos (`ADMIN`, `PROFESSOR`, `ALUNO`, `MONITOR`) e um pipeline de autenticação por sessão. Faltava uma forma para o admin gerir as indicações de monitor feitas pelos professores, aprovar ou recusar cada indicação e transformar o aluno indicado em monitor quando aprovado.

## Decisão

**Adicionar um domínio `monitorias` com aprovação/rejeição de indicações acessível apenas para admins.**

## Justificativa

- A aprovação de indicação é uma regra de negócio distinta e merece um domínio separado, em linha com a arquitetura de blueprints por épico.
- Admins já têm papel e acesso à gestão de usuários — faz sentido centralizar a aprovação de indicações em uma tela administrativa.
- O fluxo deve ser simples: listar indicações pendentes, permitir aprovar ou rejeitar, e atualizar o status do registro e do usuário indicado.
- O script de teste deve gerar dados de exemplo e inicializar a aplicação para facilitar a validação manual.

## Implementação

- Adicionado blueprint `monitorias` no backend:
  - `backend/monitorias/__init__.py`
  - `backend/monitorias/routes.py`
  - `backend/monitorias/service.py`
  - `backend/monitorias/repository.py`
- Registrado `monitorias` em `backend/app.py`.
- Criada página administrativa de pendências em `frontend/templates/monitorias/pending.html`.
- Atualizado `frontend/templates/base.html` para expor o link `Indicações` apenas para admins.
- Implementado repositório com consultas e comandos SQL diretos:
  - listar indicações pendentes
  - aprovar indicação e promover o aluno a monitor ativo
  - rejeitar indicação e gravar motivo de recusa
- Garantido controle de acesso com `@require_role('ADMIN')` nas rotas de monitorias.
- Ajustada inicialização do banco em `backend/db/connection.py` para expor erro claro se a conexão MySQL falhar.
- Criado script de teste/seed em `backend/scripts/create_admin_indicacao_test.py` e wrapper `backend/scripts/create_admin_indicacao_test.sh`:
  - cria admin de teste com nome `AdminTeste`, email `admin@teste.com`, senha `AdminSenha123`
  - cria professor e aluno de exemplo
  - cria disciplina de teste e indicação pendente
  - inicia o app e aguarda o health check em `http://localhost:5000/health`

## Consequências

- Admins têm nova tela para gerir indicações de monitor, reduzindo trabalho manual no banco.
- O fluxo de aprovação agora atualiza corretamente o papel do aluno indicado para `MONITOR` e o deixa `ATIVO`.
- A infraestrutura do backend segue o padrão de blueprints e queries diretas do projeto.
- O script de teste permite validar o fluxo sem depender do cliente `mysql` no terminal, usando `mysql-connector-python` via Python.
- A documentação de arquitetura recebe um registro desta sessão para rastreabilidade e revisão futura.
