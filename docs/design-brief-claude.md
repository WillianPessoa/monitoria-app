# Design Brief — Monitoria App

## O que é o app

**Monitoria App** é um sistema web de gestão de monitoria acadêmica da UFRJ/IC.
Substitui o processo atual (WhatsApp, planilhas, comunicação informal) com um
fluxo estruturado de agendamento de atendimentos entre alunos, monitores e professores.

Stack: **Python Flask + Jinja2 templates + CSS puro**. Sem frameworks JS.
Um único arquivo CSS (`styles.css`). Deploy no Railway.

---

## Papéis de usuário e o que cada um faz

### ADMIN
- Cadastra todos os usuários do sistema (aluno, professor, admin)
- Cadastra disciplinas e associa um professor responsável
- Aprova ou rejeita indicações de monitor feitas por professores
- Visualiza relatórios: horas por monitor, participação por disciplina

### PROFESSOR
- Vê suas disciplinas
- Indica um aluno como monitor para uma de suas disciplinas
- Vê histórico de atendimentos da disciplina

### MONITOR (é também um ALUNO com vínculo ativo de monitoria)
- Cria horários de atendimento disponíveis (data, hora início, hora fim, local)
- Vê sua agenda: horários criados + quem agendou
- Registra presença/ausência dos alunos após cada sessão
- Registra o assunto tratado na sessão

### ALUNO
- Vê disciplinas em que está matriculado
- Busca horários disponíveis de monitoria por disciplina
- Agenda um horário com o monitor
- Cancela agendamento com antecedência mínima
- Vê status dos seus agendamentos

---

## Telas existentes

| Rota | Quem acessa | O que faz |
|---|---|---|
| `/login` | Todos | Login com email + senha |
| `/first-access` | Todos (primeiro login) | Troca de senha obrigatória |
| `/` (home) | Todos | Dashboard por papel |
| `/usuarios/` | Admin | Cadastrar usuário + lista de usuários |
| `/disciplinas/` | Admin | Cadastrar disciplina + lista |
| `/disciplinas/<id>` | Aluno, Monitor, Professor | Detalhe da disciplina + monitorias |
| `/disciplinas/<id>/alunos` | Professor | Lista de alunos da disciplina |
| `/disciplinas/<id>/historico` | Professor | Histórico de sessões |
| `/monitorias/pendentes` | Admin | Fila de indicações aguardando aprovação |
| `/monitorias/indicar` | Professor | Indicar aluno como monitor |
| `/agenda/` | Aluno, Monitor | Agenda (tela compartilhada — maior problema de UX) |
| `/relatorios/` | Admin | Relatório de horas + participação |
| `/usuarios/perfil` | Monitor | Ver/editar perfil |

---

## Problemas de design e fluxo a resolver

### 1. Navegação sem hierarquia
Nav links e botões de ação usam a mesma classe visual. O usuário não distingue
"ir para Disciplinas" de "Sair". Não há título de página visível na tela —
o `<h1>` do topbar é sempre "Monitoria App".

**O que queremos:** navegação claramente separada de ações. Cada tela tem seu
próprio título e contexto visual. Considerar sidebar lateral para desktop.

### 2. Home como relatório, não dashboard
A home do professor é uma tabela de 6 colunas com um formulário ("Indicar monitor")
embutido dentro de uma célula. A home do aluno é uma tabela de 1 coluna com links.
Nenhuma home tem cards de resumo, números relevantes ou ações rápidas em destaque.

**O que queremos:** home por papel que age como dashboard — card de estado atual
(ex.: "você tem 2 horários disponíveis esta semana"), ação primária em destaque,
lista secundária de contexto. Não tabelas.

### 3. Agenda como dump único
A rota `/agenda` serve monitor e aluno na mesma página, empilhando:
para o monitor — votação de horários + agenda confirmada + formulário de registro de presença + log;
para o aluno — horários disponíveis para agendar + meus agendamentos.

O resultado é uma página longa e confusa onde nada tem prioridade.

**O que queremos:** separação clara. Para o monitor, a tela de agenda deve
priorizar "o que precisa de ação agora" (sessões passadas sem registro >
próximas sessões > histórico). Para o aluno, separar "buscar e agendar" de
"meus agendamentos".

### 4. Formulários dentro de tabelas
O fluxo de "professor indica monitor" é feito com um `<select>` + `<button>`
dentro de uma célula de tabela na home. Isso é frágil, confuso e tem ux horrível
em mobile.

**O que queremos:** ação de indicação numa tela dedicada ou modal, não embutida
numa tabela.

### 5. Ações destrutivas sem confirmação
"Desativar usuário", "Cancelar agendamento" e "Resetar senha" são botões diretos
sem nenhum passo de confirmação. O CSS já tem suporte a `<dialog>` nativo.

**O que queremos:** ações destrutivas abrem um dialog de confirmação antes de executar.

### 6. Status como texto bruto
Status exibidos como ENUM (`ATIVA`, `CONCLUIDA`, `PENDENTE_APROVACAO`) sem formatação.
O CSS já tem `.status-pill` mas é usado inconsistentemente.

**O que queremos:** status sempre como pill traduzido e colorido por estado
(verde = ativo/confirmado, amarelo = pendente, vermelho = rejeitado/cancelado).

---

## Constraints técnicas

- **Sem frameworks JS** — nenhum React, Vue, Alpine. JS puro mínimo (já existe `ui.js` para menu mobile e tema).
- **Jinja2 templates** — server-side rendering, sem SPA. Navegação é POST/GET e redirect.
- **CSS puro** — um único `styles.css`. Pode adicionar classes, reorganizar, reescrever partes. Os tokens de cor já existem em `:root` e funcionam.
- **Sem mudança de rotas Flask** — o refactor é de frontend (templates + CSS) only.
- **Tema claro e escuro** — já implementado via `data-theme="light"` no `<html>`. Qualquer novo componente deve ter override no tema claro.

---

## Tokens de cor existentes

```css
--bg-start: #071225     /* fundo escuro */
--bg-end:   #071b2a
--card:     #0b1220     /* superfície de card */
--muted:    #9aa7b2     /* texto secundário */
--text:     #e6eef6     /* texto principal */
--primary:  #4fd1c5     /* teal — ação principal */
--accent:   #7dd3fc     /* azul claro — destaque */
--success:  #34d399     /* verde */
--error:    #fb7185     /* vermelho */
--radius:   12px
```

Tema claro já tem overrides para todas as variáveis acima.

---

## O que esperamos desta sessão de design

1. **Proposta de layout base** — como fica a estrutura de cada tela:
   nav/sidebar, header de página, área de conteúdo principal, área de ação secundária

2. **Componentes para definir** (com exemplos de HTML + CSS):
   - Card de dashboard (stat card com número + label + link de ação)
   - Nav lateral ou topbar reestruturada
   - Status pill padronizado
   - Dialog de confirmação de ação destrutiva
   - Empty state component

3. **Proposta de reorganização da Agenda** — como separar monitor de aluno,
   como priorizar "o que precisa de ação agora"

4. **Proposta de Home por papel** — professor, monitor, aluno, admin

O resultado esperado são alterações diretas nos arquivos:
- `frontend/static/css/styles.css`
- `frontend/templates/base.html`
- `frontend/templates/home.html`
- `frontend/templates/agenda/index.html`
- demais templates conforme necessário

---

## Referências de estado atual

- Produção (Railway, branch dev): https://web-production-1f724.up.railway.app
- Credenciais de teste:
  - Admin: willian.pessoa.cs@gmail.com / monitoria-app
  - Aluno: aluno-comum@email.com.br / monitoria-app
  - Monitor: aluno-monitor@email.com.br / monitoria-app
  - Professor: professor@email.com.br / monitoria-app
