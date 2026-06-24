# Prompt / Plano — Correção de bugs e novas funcionalidades

> Use este documento como prompt de implementação. Cada item traz **causa-raiz já investigada**,
> os **arquivos exatos** a tocar e o **passo a passo**. Stack: Flask + Jinja2 + fetch/HTML,
> MySQL com queries diretas (ver `docs/adr/0004-banco-queries-diretas.md`). Sem build de frontend:
> JS em `frontend/static/js/ui.js`, CSS em `frontend/static/css/styles.css`.
>
> Projeto acadêmico — priorizar correção funcional e simplicidade, não hardening.

---

## Convenções do código (seguir)

- Camadas por blueprint: `routes.py` (HTTP/flash) → `service.py` (regras) → `repository.py` (SQL).
- Tempo sempre via `utils/time.py` (`now_sp_naive`, `hours_until`, `week_bounds_sp`). Datas são naïve em horário SP.
- Migrations idempotentes em `backend/db/migrations/AAAA_MM_DD_*.sql` (usar `IF NOT EXISTS`, tolerar coluna duplicada — ver commits recentes). Refletir também em `backend/db/schema.sql`.
- Permissões via `@login_required` / `@require_role(...)` e checagem de matrícula `disciplinas.repository.is_aluno_matriculado`.
- Cada US tem teste em `backend/tests/` (unit) e `backend/tests/ui/` (UI). Adicionar/atualizar testes.

---

## BUGS

### B1 — Fundo da área de overscroll com cor diferente

**Causa-raiz:** em `frontend/static/css/styles.css`, `--app-bg` é um `radial-gradient` aplicado em
`body` (linha ~38). O elemento `html` não tem `background`. Ao rolar além do conteúdo (overscroll) ou
quando o conteúdo excede a viewport, aparece o fundo padrão do `html`, que não combina com o fim do
gradiente (`#050d18`).

**Correção:**
1. Em `styles.css`, dar ao `html` uma cor de base sólida igual ao fim do gradiente e fixar o gradiente:
   ```css
   html { background: #050d18; }
   body { background: var(--app-bg); background-attachment: fixed; min-height: 100%; }
   ```
2. Conferir o tema claro (`[data-theme="light"]`, se existir nos tokens) e definir o `html { background }`
   equivalente, ou usar uma variável `--app-bg-solid` trocada por tema.
3. Validar visualmente rolando a Home logada e uma página longa (ex.: `disciplinas/detalhe`).

---

### B2 — Perfil do monitor: "Formato das 2h" e grade de horários não reagem dinamicamente

**Causa-raiz (principal):** o JS de perfil em `ui.js` (a partir da linha 226) é ativado por
`document.querySelector('[data-profile-config]')`, mas **esse atributo não existe em nenhum template** —
`frontend/templates/usuarios/my_profile.html` nunca o renderiza. Logo todo o comportamento dinâmico
está morto; só vale o estado renderizado pelo servidor.

Além disso, mesmo o JS atual não cobre o requisito:
- só alterna entre grade "1h" e grade "2h consecutivas"; não troca os **intervalos** da grade para o
  modo "duas sessões de 1h";
- `update2hOverlaps()` **desabilita** sobreposições — o requisito é **permitir** sobreposição.

**Correção:**
1. Em `my_profile.html`, adicionar o atributo âncora `data-profile-config` no formulário (ou num wrapper
   dentro dele) para o JS engatar. Confirmar que existem os demais hooks já esperados pelo JS:
   `data-carga-horaria`, `data-modo-2h` (no `<select>`), `data-grid-1h`, `data-grid-2h`,
   `data-profile-actions`, `data-profile-cancel`, `data-profile-save`.
2. Comportamento dinâmico (sem reload), em `ui.js`:
   - **Carga 1h** → ocultar o `<label>` "Formato das 2h" e usar grade de 1h (intervalos `HH:00–HH+1`).
   - **Carga 2h** → exibir "Formato das 2h".
     - **Uma sessão de 2h (`CONSECUTIVAS`)** → grade com intervalos de 2 em 2h (`HH:00–HH+2`).
     - **Duas sessões de 1h (`SEPARADAS`)** → grade de 1h (intervalos de 1 em 1h), permitindo escolher
       múltiplos horários.
3. **Permitir sobreposição:** remover a lógica que faz `cb.disabled = true` em `update2hOverlaps()`.
   O monitor pode marcar 13–15 e 14–16; a turma decide na votação. Manter apenas o controle visual de
   marcado/desmarcado, sem bloquear vizinhos.
4. Persistência: revisar o handler POST de perfil em `backend/usuarios/routes.py`/`service.py` para
   aceitar os formatos de `slots` das três variações (`weekday|hour` e `weekday|hour|2`) e gravar em
   `disponibilidade`/`modo_2h`/`carga_horaria_semanal` (coluna em `usuarios`).
5. Atualizar `backend/tests/ui/test_ui_us03_editar_perfil.py` cobrindo: mostrar/ocultar "Formato das 2h",
   troca de intervalos por modo, e seleção de horários sobrepostos aceita.

---

### B3 — Aluno cancela presença: marca "ausência confirmada" mas não consegue voltar atrás

**Causa-raiz:** em `frontend/templates/disciplinas/detalhe.html` (ramo `is_aluno`), quando
`status == 'AUSENTE'` só é renderizado o pill "Ausência confirmada" — **sem botão** para reverter. O
backend já suporta reverter: `disciplinas.routes.presenca` aceita `status == 'CONFIRMADA'` e faz upsert
via `monitoria_service.set_presenca` (só exige que a sessão não tenha começado).

**Correção:**
1. Em `detalhe.html`, no bloco `elif status == 'AUSENTE'`, manter o pill "Ausência confirmada" **e**
   adicionar um formulário POST para `disciplinas.presenca` com `status=CONFIRMADA` ("Confirmar presença
   novamente"), análogo ao botão de confirmar já existente. Exibir só se a sessão ainda não começou
   (reutilizar a checagem de horário; hoje `presenca` valida `hours_until > 0`).
2. Conferir que `set_presenca` faz `INSERT ... ON DUPLICATE KEY UPDATE` (tabela `presencas` tem
   `uq_presenca_unica (sessao_id, aluno_id)`), permitindo alternar CONFIRMADA↔AUSENTE quantas vezes for.
3. Teste em `backend/tests/test_us14_cancelar_agendamento_aluno.py` (ou novo): ausente → confirmar
   novamente volta para CONFIRMADA.

---

## FUNCIONALIDADES

### F1 — Renomear "Minha agenda" → "Monitorias" e reformular a página do monitor

Arquivos: `frontend/templates/base.html` (item de nav do monitor, linha ~82–84),
`frontend/templates/agenda/index.html`, `backend/agenda/routes.py`, `backend/monitorias/routes.py`.

1. **Renomear** o rótulo de navegação e títulos de "Minha agenda" para "Monitorias" (base.html `nav-item`,
   `home.html` botão "Ver minha agenda", e os blocks `page_title`/`page_sub` em `agenda/index.html`).
2. **Próxima monitoria por votação:** já existe o bloco de votação/confirmação (`confirmar_votacao`).
   Manter e destacar como ação principal "marcar a próxima monitoria".
3. **Monitorias anteriores com detalhes:** transformar o `<details>` de histórico em uma lista com botão
   "Ver detalhes" apontando para `monitorias.sessao_detalhe` (ver F6), exibindo assuntos tratados, alunos
   presentes e materiais compartilhados.
4. **Cancelar sessão agendada — apenas mensagem de confirmação** (DECISÃO: sem janela de desfazer/10 min):
   - No template, trocar o submit direto por uma **confirmação** antes de cancelar — `<dialog>` nativo
     (já usado no projeto) ou `confirm()` mínimo — com texto claro do que será cancelado.
   - **Não** alterar a lógica de backend de `cancelar_sessao`: manter o comportamento atual (incluindo a
     abertura de nova votação). Nenhuma rota de "desfazer" e nenhuma mudança de schema.
5. Atualizar testes UI `test_ui_us13_us16novo_agenda_monitor.py` para refletir o passo de confirmação;
   os testes de backend de cancelamento permanecem válidos.

### F2 — Remover agendamento avulso (horários e agendamentos só por votação)

DECISÃO: remover **todo** o fluxo de disponibilidades/agendamento avulso — tanto a criação pelo monitor
quanto a busca/agendamento pelo aluno. Os agendamentos passam a existir **apenas** via votação.

Arquivos: `frontend/templates/agenda/index.html`, `backend/agenda/{routes,service,repository}.py`,
`frontend/templates/home.html` (CTAs "Buscar monitoria"/"Ver meus agendamentos" do aluno),
`frontend/templates/base.html` (nav "Buscar monitoria" do aluno).

1. **Monitor:** remover do template a seção "Criar horário de atendimento" (US10, ~181–211) e
   "Meus horários cadastrados" (`own_slots`, ~213–248).
2. **Aluno:** remover do template a seção "Horários disponíveis" (`available_slots`/`book_slot`, ~256–299)
   e "Horários agendados" (`student_agendamentos`/`cancel_agendamento`, ~301–328). Manter apenas
   "Meus agendamentos" (`weekly_sessions`, sessões vindas de votação) e o status de presença.
3. Em `agenda/routes.py::index`, parar de montar `own_slots`, `available_slots`, `student_agendamentos`.
   Remover as rotas `create_slot`, `book_slot`, `cancel_agendamento`, `block_slot`, `unblock_slot` e os
   serviços/queries correspondentes em `service.py`/`repository.py`. As tabelas `disponibilidades` e
   `agendamentos` deixam de ser escritas; podem permanecer no schema sem uso (não dropar para evitar
   migrations destrutivas neste momento).
4. **Home/Nav do aluno:** trocar os CTAs e o item de nav que apontam para "Buscar monitoria" por links
   para as disciplinas do aluno (`disciplinas.detalhe`), de onde sai a votação/agendamento.
5. Remover/atualizar `test_us10_criar_horarios.py`, `test_us11_ver_horarios.py`, `test_us12_agendar_horario.py`,
   `test_us14_cancelar_agendamento_aluno.py` e as UIs `test_ui_us10_us11_us12_agenda.py` correspondentes.

### F3 — Admin: "Ver detalhes" de monitoria ativa em Disciplinas

Arquivos: `frontend/templates/disciplinas/index.html` (seção "Monitorias ativas"), nova rota+template,
`backend/disciplinas/{routes,service,repository}.py`, `backend/monitorias/{service,repository}.py`.

1. Na seção "Monitorias ativas" de `disciplinas/index.html`, adicionar botão "Ver detalhes" →
   nova rota `disciplinas.monitoria_detalhe(disciplina_id)` (GET, `@require_role("ADMIN")` + acesso de
   PROFESSOR responsável, ver F4 — reaproveitar a mesma view com flag `pode_adicionar`).
2. Nova página `frontend/templates/disciplinas/monitoria_detalhe.html` com:
   - **Tabela de alunos inscritos:** nome, e-mail, nº de monitorias em que esteve presente
     (contar `presencas.status='CONFIRMADA'` por aluno na disciplina).
   - **Relatório de horas de monitoria até o momento** (somar duração das `monitoria_sessoes`
     `CONCLUIDA` da disciplina — reaproveitar lógica de `get_monitor_hours_count`/relatórios).
   - **Lista de monitorias da disciplina:** por sessão, qtd de alunos presentes + assuntos tratados, com
     botão "Ver alunos" (abre F6 ou um detalhe inline com os presentes).
   - **Adicionar alunos:** reaproveitar o dialog/rota existente
     `disciplinas.adicionar_alunos` (já aceita lista de e-mails). Exibir só quando `pode_adicionar`.
3. Repositório: novas queries para (a) alunos da disciplina com contagem de presenças confirmadas,
   (b) total de horas concluídas, (c) sessões com contagem de presentes. Seguir padrão de queries diretas.
4. Testes: nova suíte `test_us21_detalhe_monitoria.py` + UI correspondente.

### F4 — Professor: abrir disciplina a partir do Início (mesma página do F3, sem adicionar alunos)

Arquivos: `frontend/templates/home.html` (ramo PROFESSOR já lista disciplinas e linka
`disciplinas.detalhe`), reusar a view de F3.

1. O Início do professor já mostra "Suas disciplinas" com link "Abrir →" para `disciplinas.detalhe`.
   Apontar (ou adicionar) para a nova `disciplinas.monitoria_detalhe` quando o objetivo for o relatório
   detalhado, passando `pode_adicionar=False` para PROFESSOR responsável.
2. Na view de F3, autorizar: `ADMIN` (com adicionar) **ou** `PROFESSOR` cujo `professor_id == disciplina`
   (sem adicionar). Reusar o padrão de checagem já presente em `disciplinas.routes.historico`.
3. Testes: cobrir acesso do professor responsável e bloqueio de professor não-responsável.

### F5 — Aluno: abrir disciplina inscrita a partir do Início

Arquivos: `frontend/templates/home.html` (ramo ALUNO já linka `disciplinas.detalhe`),
`frontend/templates/disciplinas/detalhe.html` (já existe e cobre boa parte).

A página `disciplinas/detalhe.html` para aluno **já** entrega: (1) votação para a próxima monitoria
(`show_votacao`), (2) histórico de monitorias passadas com botão "Detalhes" → `monitorias.sessao_detalhe`.
DECISÃO: o item (3) do pedido foi erro de digitação — **não há terceiro requisito**. A página fica
completa com votação + histórico. Pendências:
1. Garantir que o link do Início do aluno leva a essa página (já leva).
2. Implementar de fato o detalhe da sessão (F6), pois hoje é placeholder.

### F6 — Detalhe da sessão de monitoria (hoje é placeholder)

Arquivos: `backend/monitorias/routes.py::sessao_detalhe` (renderiza `placeholder.html`),
novo `frontend/templates/monitorias/sessao_detalhe.html`, `backend/monitorias/{service,repository}.py`.

1. Substituir o `render_template("placeholder.html", ...)` por uma página real mostrando:
   data/horário, assunto tratado, **alunos presentes** (`list_session_participants` + status), e
   **materiais compartilhados**.
2. **Materiais compartilhados não existem no schema** — criar suporte:
   - Migration `backend/db/migrations/2026_06_24_add_sessao_materiais.sql` + `schema.sql`:
     tabela `sessao_materiais (id, sessao_id FK, descricao, url NULL, criado_em)` **ou**, se simples
     bastar, uma coluna `materiais TEXT NULL` em `monitoria_sessoes`. Recomendado: tabela própria para
     listar vários itens.
   - Permitir o monitor anexar materiais no registro da sessão (formulário em
     `monitorias.registrar_sessao`, junto de `assunto`).
3. Autorização já existe na rota (admin/professor/monitor/aluno matriculado). Manter.
4. Reusar essa página como "Ver alunos" do F3 e como "Detalhes" do histórico do aluno (F5).
5. Teste: `test_us21_sessao_detalhe.py` + UI.

---

## Migrations a criar
- `2026_06_24_add_sessao_materiais.sql` (F6) — tabela `sessao_materiais` (ou coluna `materiais`).
- F1 não exige schema novo (apenas confirmação de UI).
Refletir tudo em `backend/db/schema.sql`. Migrations idempotentes (`IF NOT EXISTS`).

## Ordem sugerida de execução
1. B1 (CSS) → 2. B3 (1 botão) → 3. B2 (perfil dinâmico) → 4. F2 (remoção do agendamento avulso) →
5. F1 (renomear "Monitorias" + confirmação de cancelamento) → 6. F6 (detalhe + materiais, base de F3/F5) →
7. F3 (admin) → 8. F4 (professor) → 9. F5 (aluno).

## Decisões tomadas (confirmadas pelo usuário)
- **F5 item (3):** erro de digitação — não existe terceiro requisito; página fica com votação + histórico.
- **F2:** remover **também** o agendamento avulso do aluno; agendamentos passam a ser só por votação.
- **F1:** esquecer a janela de 10 min/desfazer — apenas adicionar a mensagem de confirmação ao cancelar.

## Verificação final
- `cd backend && pytest` (unit + UI Selenium) — manter a suíte TT07 verde.
- Conferir visualmente cada tela tocada (login como ADMIN, PROFESSOR, MONITOR, ALUNO).
