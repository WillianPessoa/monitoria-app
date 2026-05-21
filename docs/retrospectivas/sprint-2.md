---
sprint: 2
data: 20/05/2026
formato: Easy Retro
status: concluído
---

# Retrospectiva — Sprint 2

**Data:** 20/05/2026
**Formato:** Easy Retro
**Participantes:** Bruna, Thais, João Pedro, Pedro, Gabriel, Gustavo, Willian

---

## Easy Retro Board

### 🟢 What Went Well

- Entregamos as histórias centrais da sprint (US06, US07, US08) com o sistema funcionando em produção
- Corrigimos o problema de execução local identificado na Sprint 1 — ambiente Docker estável para todos os membros

---

### 🔴 What Can We Improve

- Organização das branches — membros trabalharam em branches isoladas sem partir da branch principal, gerando conflitos de integração (caso US09)
- Tarefas precisam ter deadlines específicos dentro da sprint — sem data interna, o trabalho se concentrou no último dia

---

### 🔵 Action Items

- Criar uma branch única de desenvolvimento (`dev`) a partir da qual todos partem e para a qual todos abrem PRs — **já implementado ao final desta sprint**
- Definir no início da sprint um prazo máximo por tarefa correspondente a uma fração do período total da sprint, evitando acúmulo no final

---

### 🟡 What Puzzles Us

- US09 foi desenvolvida mas não integrada a tempo — o processo de abertura de PR precisa ser parte do fluxo de trabalho, não uma etapa opcional
- A ausência de Sprint Tales e repasse de lógica técnica ao QM gerou flags que atrasaram o fechamento das histórias; o time precisa incorporar esses passos como parte do desenvolvimento, não como burocracia pós-entrega
