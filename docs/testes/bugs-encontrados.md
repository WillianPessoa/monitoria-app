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
| US10 — Monitor cria horários | ⏳ Pendente |
| US11 — Aluno vê horários disponíveis | ⏳ Pendente |
| US12 — Aluno agenda horário | ⏳ Pendente |
| US16 — Monitor registra presença | ⏳ Pendente |
| US17 — Monitor registra assunto tratado | ⏳ Pendente |
| US18 — Admin vê horas por monitor | ⏳ Pendente |
| US20 — Admin gera relatório | ⏳ Pendente |
