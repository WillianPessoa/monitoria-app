# Design Refactor — Monitoria App

**Status:** Planejado — executar antes dos testes automatizados (TT07)  
**Contexto:** refatoração de design e fluxo para a versão de apresentação  
**Responsável:** Willian (QM)

---

## Motivação

O app funciona, mas tem problemas visuais e de fluxo que precisam ser corrigidos
antes da apresentação e antes dos testes automatizados (os testes devem passar
na versão antiga e na nova — por isso o refactor vem primeiro).

---

## Problemas identificados

### Navegação
- Links de nav usam a mesma classe `.button` que botões de ação — impossível
  distinguir visualmente navegação de ação
- Topbar plana sem hierarquia: todos os itens aparecem com o mesmo peso
- O botão "Tema" está perdido no fim do nav sem destaque
- Não há breadcrumb nem título de página — o usuário não sabe onde está

### Home (por papel)
- **Professor**: tabela com 6 colunas incluindo um formulário de "Indicar monitor"
  embutido dentro de uma célula de tabela — anti-padrão de UX
- **Aluno/Monitor**: lista de disciplinas numa tabela de 1 coluna — sem valor visual
- Nenhuma das homes tem cards de resumo ou ações rápidas — parece um relatório,
  não um dashboard

### Agenda (página mais problemática)
- Uma única página `/agenda` serve monitor e aluno ao mesmo tempo, sem separação
  visual clara de contexto
- Hierarquia de cabeçalhos h2 → h3 → h4 → h5 dentro da mesma tela
- Monitor vê: votação + monitorias confirmadas + registrar presença + log —
  tudo empilhado sem estrutura de prioridade
- Aluno vê: horários disponíveis + monitorias agendadas — misturado com seção do monitor

### Formulários e ações destrutivas
- Botões "Desativar" e "Cancelar" não pedem confirmação — o `.dialog` existe no CSS
  mas não é usado para ações destrutivas
- "Resetar senha" e "Desativar" aparecem lado a lado sem distinção de criticidade

### Dados exibidos
- Status exibidos como ENUM bruto: "ATIVA", "PENDENTE", "CONCLUIDA" — sem formatação
  ou tradução para PT-BR
- Colunas redundantes em tabelas (ex.: disciplina aparece como código + nome em colunas separadas desnecessariamente)

### Marca e identidade
- Logo é uma `<span>` com gradiente vazio — sem identidade
- "Monitoria App" como nome está certo, mas sem tagline ou contexto de UFRJ/IC

---

## Escopo do refactor

### O que vai mudar
- [ ] Navegação: separar visualmente nav links de action buttons; considerar sidebar
  lateral para desktop
- [ ] Home por papel: substituir tabelas por cards de resumo + ações rápidas contextuais
- [ ] Agenda monitor: separar em seções com tabs ou âncoras claras (Próximas → Registrar → Histórico)
- [ ] Agenda aluno: tela própria e clara para "buscar horários" e "meus agendamentos"
- [ ] Confirmação de ações destrutivas: usar `<dialog>` nativo já com CSS pronto
- [ ] Status em PT-BR com `.status-pill` padronizado em todas as telas
- [ ] Hierarquia tipográfica: no máximo h2 → h3 numa mesma página
- [ ] Page titles: cada tela tem um `<h1>` claro (hoje o topbar tem o h1 do app inteiro)
- [ ] Formulário de indicação de monitor: página dedicada ou modal, fora da tabela

### O que NÃO muda
- Stack: Jinja2 templates, CSS puro, sem JS framework
- Um único `styles.css`
- Tokens de cor e variáveis CSS já existentes (podem ser ajustados, não reescritos)
- Estrutura de blueprints do Flask (sem mudança de rotas)

---

## Ordem de execução

1. **Brief → Claude Design** — gerar proposta de design system e layout por tela
2. **Atualizar `styles.css`** — ajustar/adicionar classes conforme proposta
3. **Refatorar templates** — de dentro para fora: base.html → home.html → agenda → demais
4. **Validar visualmente** — abrir Railway localmente (ou dev), checar cada papel
5. **Rodar testes** — garantir que TT07 passa na versão refatorada

---

## Referências

- Templates: `frontend/templates/`
- CSS: `frontend/static/css/styles.css`
- Brief para Claude Design: `docs/design-brief-claude.md`
