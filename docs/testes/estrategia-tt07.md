# TT07 — Estratégia de Testes Automatizados

**Issue:** #35  
**Responsável:** Willian (QM)  
**Status:** Sprint Backlog — DoR em definição

---

## Objetivo

Cobrir os critérios BDD do `criterios-de-aceitacao.md` com testes automatizados,
e fornecer um script de seed para popular o ambiente de produção (Railway) com
dados realistas para demo e apresentação.

---

## Decisões de framework

| Decisão | Escolha | Motivo |
|---|---|---|
| Framework de testes | `pytest` | Já é Python; padrão Flask |
| Estilo BDD | pytest puro com nomes descritivos | Sem dependência extra (pytest-bdd) |
| Escopo unitário/integração | Flask test client | Sem rede; rodar localmente |
| Seed de produção | Script `requests` contra Railway | Independente do framework de teste |

---

## Estrutura de arquivos

```
backend/
  tests/
    conftest.py                     ← fixtures: app, client, dados de fábrica
    test_us01_cadastro_usuarios.py
    test_us02_login.py
    test_us06_disciplinas.py
    test_us07_indicacao_monitor.py
    test_us08_aprovacao_monitor.py
    test_us10_criar_horarios.py
    test_us11_ver_horarios.py
    test_us12_agendar.py
    test_us16_registrar_presenca.py
    test_us18_relatorio_horas.py
    test_us20_relatorio_participacao.py
  scripts/
    seed_production.py              ← popula Railway com dados de demo
```

---

## Cobertura planejada por US

### US01 — Admin cadastra usuários
- [ ] Cenário 1: cadastro bem-sucedido → usuário criado com status Pendente
- [ ] Cenário 2: email duplicado → 400 com mensagem "Email já cadastrado"
- [ ] Cenário 3: campos obrigatórios ausentes → form rejeita

### US02 — Login
- [ ] Cenário 1: credenciais corretas → redirecionado pelo papel
- [ ] Cenário 2: credenciais inválidas → erro genérico
- [ ] Cenário 3: primeiro acesso (Pendente) → redireciona para troca de senha
- [ ] Cenário 4: usuário inativo → login negado

### US06 — Admin cadastra disciplinas
- [ ] Cenário 1: cadastro bem-sucedido
- [ ] Cenário 2: código duplicado → rejeitado
- [ ] Cenário 3: professor inválido → rejeitado

### US07 — Professor indica monitor
- [ ] Cenário 1: indicação bem-sucedida → status Pendente
- [ ] Cenário 2: papel inválido → rejeitado

### US08 — Admin aprova/rejeita indicação
- [ ] Cenário 1: aprovação → vínculo Ativo
- [ ] Cenário 2: rejeição com motivo → registrado
- [ ] Cenário 3: indicação processada sai da fila

### US10 — Monitor cria horários
- [ ] Cenário 1: criação bem-sucedida → aparece na agenda
- [ ] Cenário 2: sobreposição → rejeitado
- [ ] Cenário 3: data no passado → rejeitado

### US11 — Aluno vê horários disponíveis
- [ ] Cenário 1: busca por disciplina → lista com dados corretos
- [ ] Cenário 2: horário lotado não aparece
- [ ] Cenário 3: horário passado não aparece

### US12 — Aluno agenda horário
- [ ] Cenário 1: agendamento bem-sucedido → sai da listagem de disponíveis
- [ ] Cenário 2: conflito de horário do aluno → rejeitado

### US16 — Monitor registra presença
- [ ] Cenário 1: registro "presente" → contabilizado em horas
- [ ] Cenário 2: registro "ausente" → não contabilizado
- [ ] Cenário 3: horário futuro → rejeitado

### US18 — Admin vê horas por monitor
- [ ] Cenário 1: painel do mês corrente → total por monitor
- [ ] Cenário 2: filtro por disciplina
- [ ] Cenário 3: apenas sessões "presente" contam

### US20 — Admin gera relatório
- [ ] Cenário 1: geração do relatório por disciplina/período
- [ ] Cenário 2: exportação disponível

---

## Seed script — dados de demo

O script `seed_production.py` autentica na Railway e cria:

### Usuários criados (via POST admin)
- 3 professores (`prof.calculo@test.com`, `prof.bd@test.com`, `prof.poo@test.com`)
- 6 alunos (`aluno1@test.com` … `aluno6@test.com`)
- 3 monitores (alunos com indicação aprovada)

### Disciplinas
- Cálculo I (MAB123) — Prof. Cálculo
- Banco de Dados (MAB456) — Prof. BD
- Programação OO (MAB789) — Prof. POO

### Fluxo de monitoria
- Cada professor indica 1 monitor → admin aprova
- Cada monitor cria 4 horários (2 passados, 2 futuros para a demo)
- 2 alunos agendaram horários passados → registros de presença e ausência criados
- 1 aluno tem agendamento futuro (para demonstrar durante a apresentação)

### Execução
```bash
# Rodas antes da apresentação:
cd backend
python scripts/seed_production.py --url https://web-production-1f724.up.railway.app
```

O script verifica se os dados já existem (idempotente) e não duplica nada.

---

## Dependências a instalar

```
pytest==8.x
pytest-cov           # cobertura
requests             # seed script
```

Adicionar em `requirements.txt` com versões fixadas.

---

## Critério de done (DoD)

- [ ] Todos os cenários BDD cobertos com pelo menos 1 teste
- [ ] `pytest` passa localmente sem erros
- [ ] Cobertura ≥ 70% das rotas principais
- [ ] `seed_production.py` roda sem erros contra Railway
- [ ] Dados de demo visíveis em produção antes da apresentação
