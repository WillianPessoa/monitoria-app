# Correções e Implementações — Design Refactor

Data de referência: 24/06/2026

---

## Sumário

| # | Área | Item | Tipo |
|---|------|------|------|
| 1 | Relatórios | Mínimo de horas dinâmico por semanas concluídas | Implementação |
| 2 | Monitor | Finalizar sessão pendente em "Ver detalhes" | Implementação |
| 3 | Monitor | Campo de contato livre (sem tipo fixo) | Correção |
| 4 | Aluno | Votações abertas na página "Monitorias" | Implementação |
| 5 | Admin | Botão "Ver sessões" na tabela de horas por monitor | Implementação |
| 6 | Admin | Indicador de mínimo 1h/semana no relatório de participação | Implementação |
| 7 | Monitor | Aviso visual de votos insuficientes na votação da semana | Implementação |
| 8 | Monitor | Finalizar sessão pendente em "Ver turma" | Implementação |
| 9 | Monitor | Contato obrigatório com tipo e validação por formato | Correção + Implementação |
| 10 | Admin | Campo "Até" restringe datas anteriores a "De" | Correção |
| 11 | Admin | Bug: mínimo de horas 7/6→14/6 retornava 2h em vez de 1h | Correção de bug |
| 12 | Monitor | Máscara de celular e mensagens de erro específicas por tipo | Implementação |

---

## 1. Mínimo de horas dinâmico (Relatórios)

**Problema:** A página de relatórios exibia o mínimo mensal de horas baseado no total de semanas do mês, sem considerar o dia atual.

**Solução:** O mínimo agora é calculado contando apenas as semanas cujo domingo já passou (semanas concluídas). Cada semana concluída vale 1h.

**Arquivos alterados:**
- `backend/relatorios/service.py` — `get_painel_horas`: substituída a contagem fixa por iteração sobre `calendar.monthcalendar`, filtrando semanas onde `week[6] > 0` (domingo existe no mês) e `date(..., week[6]) < hoje`.

**Exemplo:**
- 24/06 → 3h (semanas 1–3 encerradas)
- 29/06 → 4h (semana 4 encerrada em 28/06)

---

## 2. Finalizar sessão pendente em "Ver detalhes"

**Problema:** O monitor só podia finalizar sessões pendentes pela agenda principal, não pela página de detalhes da sessão.

**Solução:** A página de detalhes da sessão exibe um card "Ação necessária" com botão "Finalizar monitoria" quando a sessão está `AGENDADA` e o `data_fim` já passou.

**Arquivos alterados:**
- `backend/monitorias/routes.py` — rota `sessao_detalhe`: quando `is_monitor` e sessão pendente, busca `alunos_sessao` via `service.list_alunos_for_sessao` e passa `now_value` ao template.
- `frontend/templates/monitorias/sessao_detalhe.html` — seção "Ação necessária" adicionada no topo do conteúdo, com `<dialog>` contendo formulário de registro (alunos presentes, assunto, materiais), postando para `monitorias.registrar_sessao`.

---

## 3. Campo de contato livre (sem tipo fixo)

**Contexto:** O formulário de perfil do monitor exigia a seleção de tipo ("Celular" ou "E-mail") através de um select que incluía "Selecione" como opção padrão. Monitores sem contato salvo ficavam presos: salvar com "Selecione" falhava na validação do serviço.

**Solução (versão intermediária):** Removido o select de tipo; mantido apenas campo de texto livre sem validação de formato. O serviço passou a aceitar qualquer texto quando o tipo não era explicitamente "email" ou "celular".

> Esta solução foi posteriormente substituída pelo item 9 (abaixo).

**Arquivos alterados:**
- `backend/usuarios/service.py` — removido `else: return False` na validação de tipo.
- `frontend/templates/usuarios/my_profile.html` — select de tipo removido; `contato_valor` com placeholder genérico.

---

## 4. Votações abertas na página "Monitorias" (Aluno)

**Problema:** Alunos não tinham visibilidade de votações abertas para suas disciplinas na página "Monitorias", sendo obrigados a acessar cada disciplina individualmente.

**Solução:** Para usuários sem monitoria ativa, a rota da agenda passa a consultar votações abertas para cada disciplina matriculada. A seção "Votações abertas" é exibida acima dos agendamentos quando há votações pendentes.

**Arquivos alterados:**
- `backend/agenda/routes.py` — bloco `else` (não-monitor): itera sobre `disciplinas_service.list_disciplinas_by_aluno`, verifica se há sessão futura na semana e se existe `get_open_votacao` para a disciplina; monta `votacoes_pendentes_aluno` com opções e voto atual do aluno.
- `frontend/templates/agenda/index.html` — seção "Votações abertas" com card por disciplina e `<dialog>` de votação (checkboxes por opção, POST para `disciplinas.votar`). Exibe pill "Votou" e botão "Alterar voto" para alunos que já votaram.

---

## 5. Botão "Ver sessões" na tabela de horas por monitor (Admin)

**Problema:** A tabela de monitores no relatório de horas exibia a disciplina como sublabel abaixo do nome (visualmente na mesma coluna), sem ação associada.

**Solução:** Disciplina movida para coluna própria; adicionado botão "Ver sessões" com link para `disciplinas.monitoria_detalhe` daquela disciplina.

**Arquivos alterados:**
- `backend/relatorios/repository.py` — `list_horas_por_monitor`: adicionado `m.disciplina_id AS disciplina_id` ao SELECT.
- `frontend/templates/relatorios/horas.html` — reestruturado o `user-row`: monitor e disciplina em `flex:1` separados; adicionada coluna de ação com `<a class="button btn-outline btn-sm">Ver sessões</a>`.

---

## 6. Indicador de mínimo 1h/semana no relatório de participação (Admin)

**Implementação:** O relatório de participação por disciplina exibe, para cada monitor no período selecionado, se ele atingiu o mínimo de 1h por semana.

**Cálculo:** O número de semanas no período é `max(1, (data_fim - data_inicio).days // 7)`. O mínimo esperado é `semanas_no_periodo × 1h`.

**Arquivos alterados:**
- `backend/relatorios/routes.py` — função `_count_weeks_in_period(data_inicio, data_fim)` adicionada; `participacao` calcula `semanas_no_periodo` e `minimo_esperado_horas` quando há disciplina selecionada.
- `frontend/templates/relatorios/participacao.html` — coluna "Mínimo 1h/sem." adicionada à tabela de monitores: pill verde "Atingiu" ou pill vermelha "X/Yh" quando abaixo; cabeçalho do card exibe o resumo do período.

---

## 7. Aviso visual de votos insuficientes na votação da semana (Monitor)

**Problema:** Quando não havia votos suficientes, os checkboxes estavam desabilitados mas não havia indicação clara do motivo ou do progresso.

**Solução:** Card de aviso amarelo exibido em dois cenários:
- Nenhum voto ainda: "Aguardando votos dos alunos — 0 de N votos mínimos. A grade aparecerá quando os alunos votarem."
- Votos parciais: "X de N votos mínimos recebidos. Confirmação disponível após atingir o mínimo."

**Arquivos alterados:**
- `backend/agenda/routes.py` — `max_votos` calculado como `max(c["votos"] for c in votacao_cells.values(), default=0)` e passado ao template.
- `frontend/templates/agenda/index.html` — card de aviso condicional `{% if max_votos < required_votes %}` inserido acima da grade de votação; seção `{% else %}` (sem votos) substituída pelo mesmo card com contagem 0.

---

## 8. Finalizar sessão pendente em "Ver turma" (Monitor)

**Problema:** A página "Ver turma" (`monitoria_detalhe`) listava sessões pendentes sem ação disponível — o monitor precisava ir à agenda principal.

**Solução:** Cada sessão pendente na lista exibe um botão "Finalizar" (visível apenas para o monitor da disciplina), que abre um `<dialog>` com o formulário completo de registro.

**Arquivos alterados:**
- `backend/disciplinas/routes.py` — rota `monitoria_detalhe`: quando `is_monitor_for_this`, itera sobre `sessoes_pendentes` e preenche `session_alunos_map[s["id"]]` via `monitoria_service.list_alunos_for_sessao`; `now_value` incluído no contexto do template.
- `frontend/templates/disciplinas/monitoria_detalhe.html` — dentro do loop `{% for s in sessoes_pendentes %}`: botão "Finalizar" adicionado ao `agenda-row`; `<dialog>` com formulário de registro (alunos, assunto, materiais) postando para `monitorias.registrar_sessao`.

---

## 9. Contato obrigatório com tipo e validação por formato (Monitor)

**Problema (bug):** Monitores sem contato salvo não conseguiam salvar o perfil (campo vazio + tipo "Selecione" causavam falha silenciosa no serviço). A solução intermediária do item 3 removeu a validação por tipo mas perdeu a separação entre e-mail e celular.

**Solução definitiva:**
- Select de tipo restaurado com apenas "Celular" e "E-mail" (sem "Selecione").
- Campo `contato_valor` marcado como `required`.
- Serviço valida o formato conforme o tipo selecionado.
- Mensagens de erro específicas por caso.

**Regras de validação:**
| Tipo | Formato exigido |
|------|----------------|
| Celular | `(XX) XXXXX-XXXX` |
| E-mail | padrão `x@x.x` |

**Arquivos alterados:**
- `backend/usuarios/service.py` — `update_monitor_profile` retorna `(True, None)` ou `(False, mensagem_de_erro)` em vez de `bool`.
- `backend/usuarios/routes.py` — desempacota `(ok, error_msg)` e usa a mensagem retornada no `flash`.
- `frontend/templates/usuarios/my_profile.html` — select de tipo com opções "Celular" e "E-mail"; campo `contato_valor` com `required`.

---

## 10. Campo "Até" restringe datas anteriores a "De" (Admin — Relatório de Participação)

**Problema:** Era possível selecionar uma data "Até" anterior à data "De", gerando relatórios com período inválido.

**Solução:** O campo `data_fim` recebe `min="{{ data_inicio }}"` como valor inicial. Um handler `onchange` no campo `data_inicio` atualiza dinamicamente o `min` de `data_fim` e avança seu valor se necessário.

**Arquivo alterado:**
- `frontend/templates/relatorios/participacao.html` — atributo `min` no `<input>` de `data_fim`; `onchange` inline no `<input>` de `data_inicio`.

---

## 11. Bug: mínimo de horas retornava 2h para período de 7 dias (Admin)

**Problema:** O período de 07/06 a 14/06 retornava mínimo de 2h ao invés de 1h.

**Causa:** A função `_count_weeks_in_period` usada anteriormente contava semanas calendário (Mon–Dom) que se sobrepunham ao período. Como 07/06 é domingo (final de uma semana) e 08–14/06 é outra semana, o algoritmo contava 2 semanas para um intervalo de exatamente 7 dias.

**Correção:** Fórmula simplificada para `max(1, (data_fim - data_inicio).days // 7)`, que divide os dias corridos entre as duas datas por 7.

| Período | Dias | Semanas (correto) |
|---------|------|-------------------|
| 07/06 → 14/06 | 7 | 1 |
| 01/06 → 21/06 | 20 | 2 |
| 01/06 → 30/06 | 29 | 4 |

**Arquivo alterado:**
- `backend/relatorios/routes.py` — `_count_weeks_in_period` reescrita.

---

## 12. Máscara de celular e mensagens de erro específicas (Monitor)

**Implementação:** Complemento ao item 9.

**Máscara de celular:** Script inline em `my_profile.html` aplica máscara `(XX) XXXXX-XXXX` em tempo real via evento `input`, ativada somente quando o tipo selecionado é "Celular". Ao trocar para "E-mail", a máscara é desanexada e o placeholder atualiza.

**Mensagens de erro:** O serviço retorna mensagens distintas:
- Campo vazio → `"Informe um contato."`
- Celular fora do formato → `"Celular inválido. Use o formato (XX) XXXXX-XXXX."`
- E-mail fora do formato → `"E-mail inválido. Verifique o endereço informado."`
- Falha no banco → `"Não foi possível salvar o perfil."`

**Arquivos alterados:**
- `frontend/templates/usuarios/my_profile.html` — bloco `<script>` com funções `maskPhone` e `applyTipo`; `addEventListener('change')` no select de tipo.
- `backend/usuarios/service.py` — mensagens de erro específicas por caso de falha.
- `backend/usuarios/routes.py` — `flash(error_msg, "error")` usando a mensagem do serviço.

---

## Arquivos modificados (visão geral)

| Arquivo | Itens |
|---------|-------|
| `backend/relatorios/service.py` | 1 |
| `backend/relatorios/repository.py` | 5 |
| `backend/relatorios/routes.py` | 6, 10, 11 |
| `backend/agenda/routes.py` | 4, 7 |
| `backend/monitorias/routes.py` | 2 |
| `backend/disciplinas/routes.py` | 8 |
| `backend/usuarios/service.py` | 3, 9, 12 |
| `backend/usuarios/routes.py` | 9, 12 |
| `frontend/templates/relatorios/horas.html` | 5 |
| `frontend/templates/relatorios/participacao.html` | 6, 10 |
| `frontend/templates/agenda/index.html` | 4, 7 |
| `frontend/templates/monitorias/sessao_detalhe.html` | 2 |
| `frontend/templates/disciplinas/monitoria_detalhe.html` | 8 |
| `frontend/templates/usuarios/my_profile.html` | 3, 9, 12 |
