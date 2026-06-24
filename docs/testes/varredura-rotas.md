# Varredura de Rotas — Mapeamento de Cobertura

**Data:** 2026-06-24  
**Branch:** `design/refactor`  
**Responsável:** QM Willian Gomes Pessoa

---

## Mapa completo: rota → US → teste

### Blueprint `auth` (prefixo `/auth`)

| Rota | Método | US | Arquivo de teste |
|---|---|---|---|
| `/auth/login` | GET, POST | US02 | `test_us02_login.py` |
| `/auth/logout` | POST | US02 | `test_us02_login.py` |
| `/auth/primeiro-acesso` | GET, POST | US02 | `test_us02_login.py` |

### Blueprint `usuarios` (prefixo `/usuarios`)

| Rota | Método | US | Arquivo de teste |
|---|---|---|---|
| `/usuarios/` | GET, POST | US01 | `test_us01_cadastro_usuarios.py` |
| `/usuarios/<id>/desativar` | POST | US04 | `test_us04_desativar_usuario.py` |
| `/usuarios/<id>/reativar` | POST | US04 | `test_us04_desativar_usuario.py` |
| `/usuarios/<id>/resetar-senha` | POST | US05 | `test_us05_resetar_senha.py` |
| `/usuarios/meu-perfil` | GET, POST | US03 | `test_us03_editar_perfil.py` |

### Blueprint `disciplinas` (prefixo `/disciplinas`)

| Rota | Método | US | Arquivo de teste | Observação |
|---|---|---|---|---|
| `/disciplinas/` | GET, POST | US06 | `test_us06_cadastrar_disciplinas.py` | |
| `/disciplinas/<id>/editar` | POST | US06 | `test_us06_cadastrar_disciplinas.py` | |
| `/disciplinas/<id>/desativar` | POST | US06 | `test_us06_cadastrar_disciplinas.py` | |
| `/disciplinas/<id>/ativar` | POST | US06 | `test_us06_cadastrar_disciplinas.py` | |
| `/disciplinas/<id>` | GET | US09, US11 | `test_us09_listar_monitorias_ativas.py`, `test_us11_ver_horarios.py` | Página de detalhe da disciplina |
| `/disciplinas/<id>/historico` | GET | US19 | `test_us19_historico_professor.py` | |
| `/disciplinas/<id>/alunos` | GET | US06 (gestão) | `test_gerenciar_alunos_disciplina.py` | Página de gestão de alunos |
| `/disciplinas/<id>/alunos/adicionar` | POST | US06 (gestão) | `test_gerenciar_alunos_disciplina.py` | Substituiu `/matricular` |
| `/disciplinas/<id>/alunos/remover` | POST | US06 (gestão) | `test_gerenciar_alunos_disciplina.py` | Substituiu `/remover-aluno` |
| `/disciplinas/<id>/votar` | POST | ⚠️ sem US formal | `test_votacao_aluno_votar.py` | Sistema de votação de horário |
| `/disciplinas/<id>/presenca` | POST | ⚠️ sem US formal | `test_presenca_sessao.py` | Aluno confirma presença em sessão |
| `/disciplinas/<id>/cancelar` | POST | ⚠️ sem US formal | `test_presenca_sessao.py` | Aluno cancela presença confirmada |
| `/disciplinas/<id>/matricular` | POST | 🔴 código morto | — | Supersedido por `/alunos/adicionar` — remover |
| `/disciplinas/<id>/remover-aluno` | POST | 🔴 código morto | — | Supersedido por `/alunos/remover` — remover |

### Blueprint `monitorias` (prefixo `/monitorias`)

| Rota | Método | US | Arquivo de teste | Observação |
|---|---|---|---|---|
| `/monitorias/pendentes` | GET | US08 | `test_us08_aprovar_rejeitar_indicacao.py` | |
| `/monitorias/<id>/aprovar` | POST | US08 | `test_us08_aprovar_rejeitar_indicacao.py` | |
| `/monitorias/<id>/rejeitar` | POST | US08 | `test_us08_aprovar_rejeitar_indicacao.py` | |
| `/monitorias/indicar` | GET, POST | US07 | `test_us07_indicar_monitor.py` | |
| `/monitorias/votacao/<id>/confirmar` | POST | ⚠️ sem US formal | `test_votacao_monitor_confirmar.py` | Monitor confirma horário da semana |
| `/monitorias/votacao/<id>/configurar` | POST | ⚠️ sem US formal | `test_votacao_monitor_configurar.py` | Monitor configura carga horária da votação |
| `/monitorias/sessoes/<id>/cancelar` | POST | US16-novo | `test_us16_novo_cancelar_sessao.py` | |
| `/monitorias/sessoes/<id>/registrar` | POST | US16, US17 | `test_us16_us17_registrar_sessao.py` | |
| `/monitorias/sessoes/<id>` | GET | — | — | Placeholder sem conteúdo de negócio |

### Blueprint `agenda` (prefixo `/agenda`)

| Rota | Método | US | Arquivo de teste |
|---|---|---|---|
| `/agenda/` | GET | US11, US13 | `test_us11_ver_horarios.py`, `test_us13_agenda_monitor.py` |
| `/agenda/slots/create` | POST | US10 | `test_us10_criar_horarios.py` |
| `/agenda/slots/<id>/book` | POST | US12, **US21** | `test_us12_agendar_horario.py`, `test_us21_us22_confirmacao_lembrete.py` |
| `/agenda/agendamentos/<id>/cancelar` | POST | US14 | `test_us14_cancelar_agendamento_aluno.py` |
| `/agenda/slots/<id>/bloquear` | POST | US15 | `test_us15_bloquear_slot.py` |
| `/agenda/slots/<id>/desbloquear` | POST | US15 | `test_us15_bloquear_slot.py` |

### Blueprint `registros` (prefixo `/registros`)

| Rota | Método | US | Arquivo de teste | Observação |
|---|---|---|---|---|
| `/registros/` | GET | — | — | Placeholder sem conteúdo de negócio |

### Blueprint `relatorios` (prefixo `/relatorios`)

| Rota | Método | US | Arquivo de teste |
|---|---|---|---|
| `/relatorios/` | GET | US18 | `test_us18_painel_horas.py` |
| `/relatorios/participacao` | GET | US20 | `test_us20_relatorio_participacao.py` |
| `/relatorios/participacao/exportar.csv` | GET | US20 | `test_us20_relatorio_participacao.py` |

---

## Lacunas identificadas

### 1. Código morto — remover

| Rota | Arquivo | Linha | Motivo |
|---|---|---|---|
| `POST /disciplinas/<id>/matricular` | `disciplinas/routes.py` | ~105 | Supersedido por `/alunos/adicionar`; nenhum template aponta para esta rota |
| `POST /disciplinas/<id>/remover-aluno` | `disciplinas/routes.py` | ~138 | Supersedido por `/alunos/remover`; nenhum template aponta para esta rota |

**Recomendação:** remover ambas as rotas mortas antes do deploy final para evitar confusão e reduzir superfície de ataque.

### 2. Funcionalidades sem US formal (implementadas, testadas, precisam de formalização)

Estas rotas foram implementadas pelo time sem US formal no backlog. Já têm testes de integração, mas faltam AC BDD no GitHub.

| Funcionalidade | Rotas | Arquivo de teste | Testes |
|---|---|---|---|
| Votação de horário (aluno vota) | `POST /disciplinas/<id>/votar` | `test_votacao_aluno_votar.py` | 7 |
| Votação de horário (monitor configura) | `POST /monitorias/votacao/<id>/configurar` | `test_votacao_monitor_configurar.py` | 7 |
| Votação de horário (monitor confirma) | `POST /monitorias/votacao/<id>/confirmar` | `test_votacao_monitor_confirmar.py` | 8 |
| Presença em sessão (aluno confirma/cancela) | `POST /disciplinas/<id>/presenca` + `/cancelar` | `test_presenca_sessao.py` | 8 |

**Recomendação:** abrir issues de US para formalizar no backlog. Sugestão de nomes:
- `[US-VOT] Sistema de votação de horário de monitoria`
- `[US-PRE] Aluno confirma/cancela presença em sessão de monitoria`

### 3. Placeholders sem implementação

| Rota | Arquivo | Observação |
|---|---|---|
| `GET /registros/` | `registros/routes.py` | Retorna placeholder — sem conteúdo de negócio |
| `GET /monitorias/sessoes/<id>` | `monitorias/routes.py` | Retorna placeholder — sem conteúdo de negócio |

**Recomendação:** se não serão implementadas neste ciclo, remover as rotas ou redirecionar para páginas existentes.

---

## Resumo de cobertura

| Categoria | Qtd |
|---|:---:|
| Rotas com US formal e teste | 28 |
| Rotas com teste mas sem US formal | 5 |
| Código morto (sem US, sem template) | 2 |
| Placeholders (sem conteúdo de negócio) | 2 |
| **Total de rotas mapeadas** | **37** |

**US não implementadas (won't-do):**
- US23 — Professor recebe relatório mensal por email: marcado como won't-do (#28)
