# Sprint 2 — Cadastro do Domínio Principal

**Time:** Bruna, Thais, João Pedro Bianco, Willian Gomes Pessoa, Pedro Chaves, Gabriel dos Reis Benevides, Gustavo Blandy de Oliveira
**Período:** 14/05/2026 – 20/05/2026

---

## 1. Objetivo da Sprint

Implementar o **cadastro das entidades centrais do sistema**, habilitando:
- Gestão de disciplinas pelo admin (criar, editar, ativar/desativar, matricular alunos)
- Indicação de monitor pelo professor
- Aprovação ou rejeição de indicações pelo admin
- Visibilidade do vínculo monitor–disciplina

**Product Goal relacionado:**
> Ter um sistema que permita ao aluno encontrar um monitor e agendar um atendimento — **continuando com o domínio de disciplinas e monitores**.

---

## 2. Entregáveis do Enunciado

| Entregável | Implementação | Status |
|---|---|:---:|
| Cadastro das disciplinas | US06 — Admin cadastra disciplinas com nome, código e professor | ✅ |
| Cadastro das bolsas de monitoria disponíveis | US07 + US08 — Indicação pelo professor + aprovação pelo admin criam o vínculo de monitoria ativo (a bolsa) | ✅ |
| Associação monitor–disciplina | US07 + US08 — Vínculo estabelecido pela indicação e confirmado pela aprovação | ✅ |

---

## 3. Histórias Entregues (EP02)

### ✅ US06 — Admin cadastra disciplinas

**Status:** Concluído
**Responsável:** Gustavo

**O que foi implementado:**
- CRUD completo de disciplinas com nome, código e professor responsável
- Validação de código único e papel do professor
- Ativação e desativação de disciplinas
- Matrícula de alunos individual e em lote (por lista de emails)
- Listagem de alunos por disciplina com busca

**Endpoints:**
```
GET/POST /disciplinas/                         (admin only)
POST     /disciplinas/<id>/editar              (admin only)
POST     /disciplinas/<id>/desativar           (admin only)
POST     /disciplinas/<id>/ativar              (admin only)
POST     /disciplinas/<id>/matricular          (admin only)
GET      /disciplinas/<id>/alunos              (admin e professor da disciplina)
POST     /disciplinas/<id>/alunos/adicionar    (admin only)
POST     /disciplinas/<id>/alunos/remover      (admin only)
```

---

### ✅ US07 — Professor indica aluno como monitor

**Status:** Concluído
**Responsável:** João Pedro

**O que foi implementado:**
- Tela de indicação filtrando apenas as disciplinas do professor logado
- Validação server-side de propriedade da disciplina
- Validação de papel do aluno (`ALUNO`)
- Indicação criada com status `PENDENTE_APROVACAO`
- Histórico de indicações do professor na mesma tela

**Endpoints:**
```
GET/POST /monitorias/indicar    (professor only)
```

---

### ✅ US08 — Admin aprova ou rejeita indicação de monitor

**Status:** Concluído
**Responsável:** Pedro

**O que foi implementado:**
- Fila de indicações pendentes para o admin
- Aprovação com validação de unicidade (aluno não pode ser monitor em duas disciplinas simultaneamente)
- Rejeição com registro de motivo
- Indicação processada sai automaticamente da fila

**Endpoints:**
```
GET  /monitorias/pendentes          (admin only)
POST /monitorias/<id>/aprovar       (admin only)
POST /monitorias/<id>/rejeitar      (admin only)
```

---

### ❌ US09 — Admin lista monitorias ativas por disciplina

**Status:** Não entregue — branch isolada, não integrada à branch principal antes do encerramento da sprint.

**Ação tomada pelo QM:** história devolvida ao Sprint Backlog com critérios de aceitação definidos retroativamente. Será replanejada na Sprint 3.

---

## 4. Restrições de Acesso Implementadas

**Matriz de Acesso — Sprint 2:**

| Endpoint | ADMIN | PROFESSOR | MONITOR | ALUNO | Anônimo |
|----------|:-----:|:---------:|:-------:|:-----:|:-------:|
| GET/POST /disciplinas/ | ✅ | ❌ | ❌ | ❌ | ❌ |
| GET /disciplinas/<id>/alunos | ✅ | ⚠️* | ❌ | ❌ | ❌ |
| POST /disciplinas/<id>/alunos/* | ✅ | ❌ | ❌ | ❌ | ❌ |
| GET/POST /monitorias/indicar | ❌ | ✅ | ❌ | ❌ | ❌ |
| GET /monitorias/pendentes | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /monitorias/<id>/aprovar | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /monitorias/<id>/rejeitar | ✅ | ❌ | ❌ | ❌ | ❌ |

*Professor só acessa alunos da disciplina da qual é responsável.

---

## 5. Alterações no Banco de Dados

Duas migrations aplicadas automaticamente na inicialização:

```sql
ALTER TABLE disciplinas
    ADD COLUMN status ENUM('ATIVA','INATIVA') NOT NULL DEFAULT 'ATIVA';

CREATE TABLE IF NOT EXISTS disciplina_alunos (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    disciplina_id BIGINT UNSIGNED NOT NULL,
    aluno_id BIGINT UNSIGNED NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_disciplina_aluno_disciplina
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id) ON DELETE CASCADE,
    CONSTRAINT fk_disciplina_aluno_usuario
        FOREIGN KEY (aluno_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    CONSTRAINT uq_disciplina_aluno UNIQUE (disciplina_id, aluno_id)
);
```

---

## 6. Testes Manuais Realizados

| Cenário | Resultado | Responsável |
|---------|-----------|-------------|
| Admin cadastra disciplina com código único | ✅ Pass | Gustavo |
| Admin tenta cadastrar código duplicado | ✅ Pass | Gustavo |
| Admin associa professor inválido à disciplina | ✅ Pass | Willian |
| Admin matricula aluno individualmente | ✅ Pass | João Pedro |
| Admin matricula alunos em lote por email | ✅ Pass | João Pedro |
| Professor indica aluno para disciplina própria | ✅ Pass | Willian |
| Professor tenta indicar para disciplina de outro | ✅ Pass | Pedro |
| Admin aprova indicação pendente | ✅ Pass | Pedro |
| Admin rejeita indicação com motivo | ✅ Pass | Gabriel |
| Admin tenta aprovar aluno já monitor | ✅ Pass | Willian |

---

## 7. Desafios e Decisões

### 1. Branch da US09 não integrada

**Desafio:** Gabriel desenvolveu a US09 numa branch que não partiu do estado atual do repositório, impossibilitando o merge antes do encerramento.

**Decisão:** QM devolveu a história ao Sprint Backlog. O action item da retrospectiva define que todas as branches devem partir da `dev` e abrir PR antes do encerramento da sprint.

**Resultado:** Estrutura de branches reformulada ao final da sprint — `main` (estável) e `dev` (desenvolvimento).

---

### 2. Validação de unicidade de monitor

**Desafio:** Um aluno pode receber indicações pendentes de múltiplos professores simultaneamente. Como evitar que seja aprovado duas vezes?

**Decisão:** A validação de "aluno já monitor" ocorre no momento da aprovação, não da criação da indicação. Registrada em ADR-0006.

**Resultado:** ✅ Implementado — primeiro admin a aprovar passa; os demais recebem erro `ALUNO_JA_MONITOR`.

---

### 3. Decisão de produto — Cancelamento de agendamento

**Contexto:** A PO Bruna identificou, ao final desta sprint, que o escopo de agendamento (Sprint 3) não cobria o cancelamento pelo monitor nem definia prazo mínimo.

**Decisão:** Criada nova história "Monitor cancela agendamento confirmado" (issue #33, must-have) com regra de 6 horas de antecedência. A US14 existente (aluno cancela) foi atualizada com a mesma regra.

---

## 8. Quadro de Progresso

| Prioridade | IDs | Status |
|------------|-----|:------:|
| **Must** | US06, US07, US08 | ✅ Concluído |
| **Should** | US09 | ❌ Devolvido ao Sprint Backlog |

**Total de histórias:** 3/4 entregues

---

## 9. Épicos Completados

| Épico | Status | Observação |
|-------|:------:|-----------|
| EP02 — Cadastro de Disciplinas e Monitores | ⚠️ **75%** | US09 pendente para Sprint 3 |

---

## 10. O Que Esperar da Sprint 3

**Sprint 3 — Agenda e Agendamento**

Foco no EP03, com as histórias:
- **US10 (8pts):** Monitor cria horários de atendimento
- **US11 (3pts):** Aluno vê horários disponíveis
- **US12 (8pts):** Aluno agenda um horário
- **US13 (3pts):** Monitor vê agenda com agendamentos
- **US09 (2pts):** Admin lista monitorias ativas *(herdada da Sprint 2)*
- **Nova (3pts):** Monitor cancela agendamento confirmado *(must-have, PO Bruna)*
- **US14 (3pts):** Aluno cancela agendamento *(should)*
- **US15 (2pts):** Monitor bloqueia horário *(should)*

**Dependências de Sprint 2 que Sprint 3 usará:**
- Disciplinas cadastradas ✅ (US06)
- Vínculo monitor–disciplina ativo ✅ (US07 + US08)
- Autenticação e controle de acesso ✅ (Sprint 1)

---

## 11. Retrospectiva

Realizada no formato Easy Retro. Documento completo em `docs/retrospectivas/sprint-2.md`.

**Resumo:**
- ✅ Sprint Goal atingido; ambiente Docker estabilizado
- 🔴 Branches isoladas causaram problema de integração; tarefas sem deadline interno concentradas no final
- 🔵 Branch `dev` criada como ponto único de desenvolvimento; definir prazo máximo por tarefa no início de cada sprint
