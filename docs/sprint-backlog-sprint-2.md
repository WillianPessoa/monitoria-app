# Sprint Backlog — Sprint 2

**Projeto:** Monitoria App
**Sprint:** 2 — Cadastro do Domínio Principal
**Período:** 14/05/2026 a 20/05/2026
**QM:** Willian Gomes Pessoa
**Time:** Bruna, Thais, João Pedro Bianco, Willian Gomes Pessoa, Pedro Chaves, Gabriel dos Reis Benevides, Gustavo Blandy de Oliveira

---

## Meta da Sprint

> O admin consegue cadastrar disciplinas e o professor consegue indicar um monitor, que é aprovado pelo admin.

---

## Itens Comprometidos

O Sprint 2 comprometeu 5 itens: 4 Must e 1 Should, todos do épico EP02 (Cadastro de Disciplinas e Monitores) mais a tarefa técnica TT06 de deploy.

**Must — EP02:** US06 (Admin cadastra disciplinas), US07 (Professor indica aluno como monitor), US08 (Admin aprova ou rejeita indicação). Responsáveis: Gustavo (US06), João Pedro (US07), Pedro (US08). Todos concluídos.

**Must — EP00:** TT06 (Publicar aplicação no Railway). Responsável: Willian. Concluído.

**Should — EP02:** US09 (Admin lista monitorias ativas). Responsável: João Pedro. Concluído — implementado junto com US07/US08 no PR #32.

---

## Detalhamento dos Itens

### US06 — Admin cadastra disciplinas

**Cenário 1: Cadastro bem-sucedido**
```
Given: admin autenticado na tela de gestão de disciplinas
When:  preenche nome, código e seleciona professor responsável e confirma
Then:  disciplina é criada e aparece imediatamente na listagem
```

**Cenário 2: Código duplicado**
```
Given: admin tenta cadastrar disciplina com código já existente
When:  confirma o cadastro
Then:  sistema rejeita com mensagem de código duplicado
```

**Resultado:** CRUD de disciplinas implementado em `disciplinas/`. Matrícula de alunos individual e em lote disponíveis. Validação de professor pelo papel e de código único.

---

### US07 — Professor indica aluno como monitor

**Cenário 1: Indicação bem-sucedida**
```
Given: professor autenticado na tela de indicação
When:  seleciona sua disciplina e um aluno ativo e confirma
Then:  indicação criada com status "Pendente de aprovação" e aparece no histórico do professor
```

**Cenário 2: Professor tenta indicar para disciplina de outro**
```
Given: professor tenta forjar o formulário com disciplina de outro professor
When:  confirma a indicação
Then:  sistema rejeita — validação de propriedade feita no backend
```

**Resultado:** Implementado em `GET/POST /monitorias/indicar`. Professor vê apenas suas disciplinas. Vínculo criado com status `PENDENTE_APROVACAO`.

---

### US08 — Admin aprova ou rejeita indicação de monitor

**Cenário 1: Aprovação bem-sucedida**
```
Given: admin na fila de indicações pendentes
When:  aprova indicação de aluno sem monitoria ativa
Then:  status atualizado para "Ativo"; indicação sai da fila
```

**Cenário 2: Aluno já é monitor em outra disciplina**
```
Given: admin tenta aprovar indicação de aluno já monitor
When:  confirma a aprovação
Then:  sistema rejeita com erro ALUNO_JA_MONITOR
```

**Cenário 3: Rejeição com motivo**
```
Given: admin rejeita indicação
When:  informa o motivo e confirma
Then:  status atualizado para "Rejeitado"; indicação sai da fila
```

**Resultado:** Implementado em `GET /monitorias/pendentes`, `POST /monitorias/<id>/aprovar` e `POST /monitorias/<id>/rejeitar`. Decisão de design documentada em ADR-0006.

---

### US09 — Admin lista monitorias ativas por disciplina

**Cenário 1: Listagem com registros**
```
Given: admin na tela de disciplinas
When:  acessa a listagem de monitorias ativas
Then:  vê tabela com disciplina, monitor e professor responsável
```

**Resultado:** `list_active_monitorias()` retorna todos os vínculos com `status = 'ATIVO'`. Exibida na tela de gestão de disciplinas do admin. Implementada via PR #32.

---

### TT06 — Publicar aplicação em servidor na nuvem

**Critérios de aceitação:**
- Aplicação acessível publicamente via URL
- Deploy automatizado a cada push na branch principal
- Schema e seed de admins aplicados automaticamente no boot

**Resultado:** Deploy no Railway com `Procfile` (gunicorn) e `railpack.json`. `config.py` adaptado para variáveis do Railway. `init_db()` aplica schema, migrations e seed automaticamente. URL: https://web-production-1f724.up.railway.app

---

## Resumo da Sprint

O Sprint 2 entregou todos os 5 itens comprometidos (100%). Sprint Goal atingido: disciplinas cadastradas, indicação de monitor pelo professor e aprovação pelo admin funcionando em produção. US09 foi integrada via PR #32 junto com US07/US08 — flag de integração levantada e resolvida pelo QM após confirmação.

---

## Definition of Done — Verificação

**US06 — Admin cadastra disciplinas**
Todos os cenários BDD verificados. CRUD completo com validação de código único e papel do professor. Matrícula em lote e individual funcionando. Sem flags do QM. Sprint Tales atualizado.

**US07 — Professor indica aluno como monitor**
Cenários BDD verificados: indicação bem-sucedida e rejeição de indicação para disciplina de outro professor. Validação server-side confirmada. Sem flags do QM. Sprint Tales atualizado.

**US08 — Admin aprova ou rejeita indicação**
Todos os 3 cenários verificados: aprovação, rejeição por aluno já monitor, rejeição com motivo. ADR-0006 documentado. Sem flags do QM. Sprint Tales atualizado.

**US09 — Admin lista monitorias ativas**
Listagem funcionando na tela de disciplinas. Flag de integração resolvida após revisão do QM confirmar implementação no PR #32. Sprint Tales atualizado.

**TT06 — Publicação no Railway**
Aplicação acessível em https://web-production-1f724.up.railway.app. Deploy ativo. Schema e seed automáticos confirmados. Sem flags do QM. Sprint Tales atualizado.
