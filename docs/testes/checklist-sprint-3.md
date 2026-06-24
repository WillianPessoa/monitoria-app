# Checklist de Testes — Sprint 3

**Sprint:** 3 — Agenda e Agendamentos  
**QM:** Willian Gomes Pessoa  
**Data de testes:** 2026-05-28  
**Ambiente:** https://web-production-1f724.up.railway.app

**Contas de teste:**
| Usuário | Email | Senha | Papel |
|---|---|---|---|
| Aluno Comum | aluno-comum@email.com.br | monitoria-app | ALUNO |
| Aluno Monitor | aluno-monitor@email.com.br | monitoria-app | MONITOR |
| Professor | professor@email.com.br | monitoria-app | PROFESSOR |

---

## US10 — Monitor cria horários de atendimento

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Criar horário futuro válido | Login como Monitor → Agenda → preencher data futura, duração 60 min → Criar horário | Horário aparece em "Meus horários de atendimento" com status Disponível | | |
| 2 | Tentar criar horário no passado | Data anterior à atual → Criar horário | Mensagem de erro: "A data e hora devem estar no futuro" | | |
| 3 | Tentar criar horário que se sobrepõe | Criar segundo horário com data idêntica ao anterior → Criar horário | Mensagem de erro: "Já existe um horário que se sobrepõe" | | |
| 4 | Criar com local preenchido | Preencher campo Local → Criar horário | Local aparece na coluna da tabela | | |
| 5 | Criar sem local | Deixar Local vazio → Criar horário | Coluna local mostra "—" | | |
| 6 | Usuário não-monitor não vê a seção | Login como Aluno Comum → Agenda | Seção "Minha agenda como monitor" não aparece | | |

---

## US11 — Aluno vê horários disponíveis de um monitor

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Aluno vê horários de disciplinas matriculadas | Login como Aluno Comum → Agenda → seção "Horários disponíveis" | Lista horários das disciplinas do aluno (status DISPONIVEL, data futura) | | |
| 2 | Aluno não vê horários de outras disciplinas | Aluno sem matrícula numa disciplina | Horários dessa disciplina não aparecem | | |
| 3 | Horário bloqueado não aparece | Monitor bloqueia um horário → Aluno acessa Agenda | Horário bloqueado ausente da lista | | |
| 4 | Horário já agendado não aparece | Outro aluno reserva → primeiro aluno acessa Agenda | Horário com status AGENDADO não aparece | | |

---

## US12 — Aluno agenda um horário disponível

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Agendar horário disponível | Login como Aluno → Agenda → clicar Reservar | Sucesso; horário aparece em "Meus agendamentos"; status muda para AGENDADO | | |
| 2 | Tentar agendar horário que outro acabou de reservar | Dois alunos acessam ao mesmo tempo (simular via dois navegadores) | Segundo aluno recebe erro "Horário indisponível" — race condition protegida por SELECT FOR UPDATE | | |
| 3 | Tentar agendar horário que já agendou (conflito de horário) | Tentar reservar dois horários que se sobrepõem | Mensagem de erro "Você já possui um agendamento no mesmo período" | | |

---

## US13 — Monitor vê agenda com agendamentos confirmados

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Monitor vê próprios horários e alunos | Login como Monitor → Agenda → seção "Meus horários de atendimento" | Tabela mostra data, duração, local, status, nome do aluno (ou "—" se disponível) | | |
| 2 | Status AGENDADO aparece correto | Aluno reserva horário → Monitor acessa Agenda | Status do horário aparece como "Agendado" (pill verde) e nome do aluno preenchido | | |
| 3 | Status DISPONIVEL aparece correto | Horário sem reserva | Status "Disponível" (pill neutro), aluno "—" | | |
| 4 | Status BLOQUEADO aparece correto | Monitor bloqueia um horário | Status "Bloqueado" (pill vermelho) | | |

---

## US14 — Aluno cancela um agendamento

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Cancelar com mais de 6h de antecedência | Agendar horário futuro (>6h) → clicar Cancelar | Sucesso; agendamento some de "Meus agendamentos"; horário volta ao status DISPONIVEL | | |
| 2 | Tentar cancelar com menos de 6h | Agendar para dentro de 6h (se possível criar slot próximo) | Mensagem de erro "Cancelamento permitido somente com mais de 6 horas de antecedência" | | |
| 3 | Aluno não cancela agendamento de outro | Tentar acessar cancel de agendamento_id de outro usuário | Mensagem "Você não tem permissão para cancelar este agendamento" | | |

---

## US15 — Monitor bloqueia um horário da agenda

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Bloquear horário disponível | Login como Monitor → Agenda → clicar Bloquear em horário DISPONIVEL | Status muda para BLOQUEADO; botão muda para Desbloquear; horário some da lista pública | | |
| 2 | Desbloquear horário bloqueado | Clicar Desbloquear em horário BLOQUEADO | Status volta para DISPONIVEL; horário reaparece na lista pública | | |
| 3 | Tentar bloquear horário com reserva | Horário com aluno reservado (status AGENDADO) → clicar Bloquear | Mensagem "Só é possível bloquear horários disponíveis (sem agendamento ativo)" | | |
| 4 | Monitor não bloqueia horário de outro monitor | Tentar POST direto com slot_id de outro monitor | Retorna erro — service valida que o monitor é dono do slot | | |

---

## US16-novo — Monitor cancela sessão de monitoria confirmada

| # | Cenário | Passos | Esperado | Status | Observações |
|---|---------|--------|----------|--------|-------------|
| 1 | Monitor cancela sessão futura | Login como Monitor → Agenda → seção "Monitorias confirmadas" → clicar Cancelar | Sessão cancelada; votação reaberta para a semana | | |
| 2 | Cancelamento reabre votação | Após cancelar sessão, Monitor acessa Agenda | Seção "Votação da semana" reaparece com opções para nova votação | | |

---

## Notas gerais

- Todos os botões de ação usam `<form method="post">` — POST não pode ser chamado por GET diretamente
- Flash messages de sucesso aparecem em verde, erro em vermelho
- Após qualquer ação, a página redireciona para `GET /agenda/` (PRG pattern)
