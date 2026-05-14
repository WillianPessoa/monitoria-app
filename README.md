# Monitoria App

Sistema para centralizar o programa de monitoria acadêmica: cadastro de monitores, agendas de atendimento, agendamento por alunos e relatórios para professores e coordenação.

## Time

| Nome | Papel QScrum |
|------|-------------|
| Bruna | Product Owner |
| Thais | Product Owner |
| João Pedro Bianco | Scrum Master |
| Pedro Chaves | Developer |
| Gabriel dos Reis Benevides | Developer |
| Gustavo Blandy de Oliveira | Developer |
| Willian Gomes Pessoa | Quality Manager |

## Stack

- **Backend:** Python 3.12 + Flask 3.0.3
- **Frontend:** HTML + CSS (Jinja2 no backend)
- **Banco de dados:** MySQL 8.0
- **Hospedagem:** (a definir)

Detalhamento da stack em [docs/stack.md](docs/stack.md).

## Como rodar localmente

1. Abra [docs/setup.md](docs/setup.md) e siga o passo a passo.
2. Entre na pasta `backend/`.
3. Instale dependencias com `pip install -r requirements.txt`.
4. Suba o banco containerizado com `docker compose -f docker-sql.yaml up -d` na raiz do projeto.
5. Copie `backend/.env.example` como base e exporte as variaveis no shell.
6. Rode `python app.py`.
7. Para smoke test automatizado da Sprint 1, rode `bash scripts/smoke_test_sprint1.sh` dentro de `backend/`.
8. Reset de senha e gestao de acesso ficam nas maos do admin na tela de usuarios.

Arquivos de referencia:

- Setup local: [docs/setup.md](docs/setup.md)
- Modelagem do banco (ER): [docs/modelagem-banco.md](docs/modelagem-banco.md)
- Schema SQL: [backend/db/schema.sql](backend/db/schema.sql)
- Docker SQL: [docker-sql.yaml](docker-sql.yaml)

## Sprints

| Sprint | Período | Foco |
|--------|---------|------|
| Sprint 0 | 30/04 | Definição + infra |
| Sprint 1 | 07/05 | Perfis e autenticação |
| Sprint 2 | 14/05 | Cadastro do domínio |
| Sprint 3 | 21/05 | Agenda e agendamento |
| Sprint 4 | 28/05 | Gestão e operação |
| Sprint 5 | 18/06 | Relatórios e notificações |

## Disciplina

Oficina de Engenharia de Software — UFRJ 2026.1
