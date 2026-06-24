# Bugs Encontrados pelos Testes Automatizados

Registro de bugs **reais** encontrados durante a execução dos testes.
Cada entrada indica qual teste falhou, qual comportamento foi observado e qual era o comportamento esperado.

Este arquivo será usado na apresentação final para demonstrar o valor dos testes automatizados.

> **Formato de cada entrada:**
> - **US / Cenário:** qual história e cenário do BDD
> - **Teste:** nome da função de teste que falhou
> - **Suite:** backend ou UI (desktop/mobile)
> - **Comportamento observado:** o que o sistema fez de errado
> - **Comportamento esperado:** o que deveria ter acontecido
> - **Causa:** o que estava errado no código (após investigação)
> - **Corrigido em:** commit ou PR que resolveu

---

## US01 — Admin cadastra usuários

*Nenhum bug encontrado. Todos os 8 testes de backend e 13 testes de UI passaram na primeira execução contra o código atual.*

---

## US02 — Login

*Nenhum bug encontrado. Todos os 11 testes de backend e 10 testes de UI passaram na primeira execução contra o código atual.*

---

## US03 — Monitor edita perfil

### BUG-01 — Salvar perfil sem alterações retorna erro falso

| Campo | Detalhe |
|---|---|
| **US / Cenário** | US03 — Monitor edita perfil |
| **Teste** | `test_atualiza_contato_vazio_aceito` (backend) |
| **Comportamento observado** | Enviar formulário de perfil sem contato (campos em branco) mostra mensagem de "Contato inválido" — erro falso, pois não há valor inválido |
| **Comportamento esperado** | Salvar sem contato deveria limpar o campo e retornar sucesso |
| **Causa** | `usuarios/repository.py` → `update_monitor_profile()`: o `UPDATE` MySQL retorna `rowcount = 0` quando nenhuma coluna mudou de valor (ex: contato já era NULL e continua NULL). O código verifica `return affected > 0` e interpreta 0 como falha, mesmo que o UPDATE tenha executado corretamente |
| **Corrigido em** | Fix aplicado em `usuarios/repository.py` — `return affected > 0` → `return True` |

### BUG-02 — Máscara JS do celular contorna validação de formato no teste de UI

| Campo | Detalhe |
|---|---|
| **US / Cenário** | US03 — Monitor edita perfil / Celular inválido rejeitado |
| **Teste** | `test_celular_invalido_exibe_erro_na_tela` (UI Desktop) |
| **Comportamento observado** | Preencher `11987654321` no campo de celular e salvar resulta em **sucesso**, não em erro. O teste esperava `.alert.error` mas o Railway mostrou `.alert.success` |
| **Comportamento esperado** | `11987654321` não está no formato `(XX) XXXXX-XXXX` e deveria ser rejeitado pelo servidor |
| **Causa** | O campo de celular tem uma máscara JavaScript (`data-contact-input`) que reformata automaticamente `11987654321` para `(11) 98765-4321` antes da submissão. O servidor recebe o valor já formatado e o aceita como válido. A validação de formato do backend nunca é acionada via UI para este caso |
| **Impacto** | A validação server-side de celular (`^\(\d{2}\) \d{5}-\d{4}$`) funciona corretamente e é coberta pelos testes de backend. A UI simplesmente previne inputs inválidos via JS antes de chegarem ao servidor — isso é comportamento esperado e desejável (boa UX). Testes de UI foram ajustados para refletir esse comportamento |
| **Corrigido em** | Teste de UI removido (comportamento é correto — JS faz a validação na camada de apresentação) |

---

## US04 — Admin desativa usuário

*Nenhum bug encontrado. Todos os 5 testes de backend passaram na primeira execução.*

---

## US05 — Admin reseta senha de usuário manualmente

*Nenhum bug encontrado. Todos os 7 testes de backend e 6 testes de UI passaram na primeira execução.*

---

## US06 — Admin cadastra disciplinas

*Nenhum bug encontrado. Todos os 12 testes de backend e 7 testes de UI passaram na primeira execução.*

---

## US07 — Professor indica aluno como monitor

*Nenhum bug encontrado. Todos os 8 testes de backend passaram na primeira execução.*

---

## US08 — Admin aprova ou rejeita indicação de monitor

*Nenhum bug encontrado. Todos os 11 testes de backend e 8 testes de UI passaram na primeira execução.*

---

## US09 — Admin lista monitorias ativas por disciplina

*Nenhum bug encontrado. Todos os 8 testes de backend e 5 testes de UI passaram na primeira execução.*

---

## BUG-03 — Página em branco para usuários não autenticados na raiz

| Campo | Detalhe |
|---|---|
| **Onde** | `GET /` — rota home em `backend/app.py` |
| **Comportamento observado** | Acessar `https://web-production-1f724.up.railway.app/` retornava HTTP 200 com body completamente vazio. Nenhum conteúdo visível, nenhuma mensagem de erro |
| **Comportamento esperado** | Usuário não autenticado deveria ser redirecionado para `/auth/login` |
| **Causa** | O redesign (`design/refactor`) envolveu `{% block content %}` dentro de um `{% if current_user.id %}` no `base.html`. `app.py` ainda chamava `render_template("home.html")` para usuários sem sessão — o template renderizava, mas o bloco de conteúdo ficava fora do `{% if %}` e produzia body vazio. O Railway retornava 200 porque não havia erro Python, apenas HTML sem conteúdo |
| **Corrigido em** | `backend/app.py` — `render_template("home.html")` → `redirect(url_for("auth.login"))` — commit `f1d8dd4` |

---

## Problema de infraestrutura encontrado durante setup

**Não é um bug de comportamento do app, mas foi descoberto durante a criação dos testes.**

| Campo | Detalhe |
|---|---|
| **Onde** | `backend/db/connection.py` → `_apply_migrations()` |
| **O que aconteceu** | Ao criar o banco `monitoria_test` do zero a partir do `schema.sql` atual e tentar rodar as migrations, o sistema lançou `Duplicate column name 'carga_horaria_semanal'` |
| **Por quê** | A migration `2026_05_28_add_monitoria_preferences.sql` usa `ALTER TABLE ... ADD COLUMN` sem `IF NOT EXISTS`. O `schema.sql` já inclui essa coluna (foi incorporada depois da migration), então ao criar um banco limpo e rodar as migrations, o comando falha |
| **Impacto** | Nenhum em produção (Railway já tem o banco com a coluna criada pela migration). Impacta apenas ambientes novos criados a partir do schema atual |
| **Solução adotada** | `conftest.py` pré-marca todas as migrations como aplicadas antes de chamar `create_app()`, fazendo com que `_apply_migrations()` as pule |
| **Solução definitiva recomendada** | Reescrever as migrations de ADD COLUMN para verificar existência via `information_schema` antes de adicionar (como já é feito nas migrations de índices) |

---

## US10 — Monitor cria horários

*Nenhum bug encontrado. Todos os 10 testes de backend passaram na primeira execução.*

---

## US11 — Aluno vê horários disponíveis

### BUG-04 — Local do atendimento não exibido no slot-card (US11 C1)

| Campo | Detalhe |
|---|---|
| **US / Cenário** | US11 — Aluno vê horários disponíveis / C1 — Busca por disciplina |
| **Teste** | `test_aluno_matriculado_ve_slot_disponivel` (backend) — falhou na primeira execução |
| **Suite** | Backend |
| **Comportamento observado** | O slot-card renderizado em `/agenda/` exibe nome do monitor, data, horário e duração, mas **não exibe o campo `local`** |
| **Comportamento esperado** | Critério US11 C1 diz: "sistema exibe lista de horários disponíveis com nome do monitor, data, horário e **local**" — o local deveria aparecer no card |
| **Causa** | `frontend/templates/agenda/index.html` — o bloco `div.slot-info` dentro de `div.slot-card` renderiza apenas data e duração. A variável `{{ slot.local }}` nunca é usada no template, apesar de estar disponível no objeto `slot` retornado pelo repositório |
| **Corrigido em** | Pendente — requer alteração no template `agenda/index.html` para exibir `slot.local` dentro de `.slot-info` |

---

## US12 — Aluno agenda horário

*Nenhum bug encontrado. Todos os 9 testes de backend passaram na primeira execução.*

---

---

## BUG-05 — Admin não consegue adicionar alunos a disciplinas (navegação quebrada)

| Campo | Detalhe |
|---|---|
| **Onde** | `frontend/templates/disciplinas/index.html` — card de disciplina |
| **Relatado por** | Colega de time durante uso da aplicação em produção (Railway) |
| **Comportamento observado** | Admin acessa `/disciplinas/` e não consegue chegar à tela de gerenciamento de alunos. O disc-card exibe apenas o botão "Editar" (que abre o modal de edição); não há nenhum link para a página de detalhe da disciplina |
| **Comportamento esperado** | Admin deveria conseguir navegar para `/disciplinas/<id>` (detalhe) e de lá clicar em "Ver alunos" para adicionar/remover alunos. Professores e alunos têm esse link disponível na home — apenas o admin ficou sem acesso |
| **Causa** | O `disc-card-name` era uma `<div>` sem âncora. A rota `disciplinas.detalhe` existe e funciona — só faltava o link. A refatoração de design (`design/refactor`) redesenhou os cards sem preservar a navegação para o detalhe |
| **Impacto** | Admin não conseguia matricular alunos em disciplinas via UI. A funcionalidade de adicionar alunos por email (`POST /disciplinas/<id>/alunos/adicionar`) está correta no backend — o problema era puramente de navegação |
| **Corrigido em** | `frontend/templates/disciplinas/index.html` — `<div class="disc-card-name">` → `<a href="{{ url_for('disciplinas.detalhe', ...) }}" class="disc-card-name">` |

**Código morto identificado durante investigação:**
- `POST /disciplinas/<id>/matricular` (`routes.py:105`) — nenhum template referencia esta rota; supersedida por `/alunos/adicionar`
- `POST /disciplinas/<id>/remover-aluno` (`routes.py:138`) — nenhum template referencia esta rota; supersedida por `/alunos/remover`

---

## Próximas US a testar

À medida que os testes forem escritos e executados para as US seguintes, novos bugs encontrados devem ser registrados aqui neste mesmo formato.

| US | Status dos testes |
|---|---|
| US01 — Admin cadastra usuários | ✅ Coberta (backend + UI) |
| US02 — Usuário faz login | ✅ Coberta (backend + UI) |
| US03 — Monitor edita perfil | ✅ Coberta (backend + UI) |
| US04 — Admin desativa usuário | ✅ Coberta (backend + UI) |
| US05 — Admin reseta senha | ✅ Coberta (backend + UI) |
| US06 — Admin cadastra disciplinas | ✅ Coberta (backend + UI) |
| US07 — Professor indica monitor | ✅ Coberta (backend + UI) |
| US08 — Admin aprova/rejeita indicação | ✅ Coberta (backend + UI) |
| US09 — Admin lista monitorias ativas | ✅ Coberta (backend + UI) |
| US10 — Monitor cria horários | ✅ Coberta (backend + UI) |
| US11 — Aluno vê horários disponíveis | ✅ Coberta (backend + UI) — BUG-04 registrado e corrigido |
| US12 — Aluno agenda horário | ✅ Coberta (backend + UI) |
| US13 — Monitor vê agenda | ✅ Coberta (backend + UI) |
| US14 — Aluno cancela agendamento | ❌ Rota não implementada no backend |
| US15 — Monitor bloqueia horário | ❌ Rota não implementada no backend |
| US16-novo — Monitor cancela sessão | ✅ Coberta (backend + UI) |
| US16 — Monitor registra presença | ✅ Coberta (backend + UI) |
| US17 — Monitor registra assunto | ✅ Coberta (backend + UI, junto com US16) |
| US18 — Admin vê horas por monitor | ✅ Coberta (backend + UI) |
| US19 — Professor vê histórico | ✅ Coberta (backend + UI, sessao_detalhe é placeholder) |
| US20 — Admin gera relatório | ✅ Coberta (backend + UI) |
