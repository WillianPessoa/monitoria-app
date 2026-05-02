# Visão do Produto — Monitoria App

---

## Declaração de Visão

Para alunos, monitores, professores e a secretaria acadêmica da universidade, que sofrem com um programa de monitoria desorganizado, conduzido por e-mail, planilha e grupos de mensagem, o Monitoria App é um sistema web que centraliza o cadastro de monitores, a criação de agendas, o agendamento de atendimentos e o registro de frequência. Diferente de planilhas e grupos informais, nosso produto oferece visibilidade completa do programa para todos os envolvidos, com dados reais para tomada de decisão.

---

## Problema

| Quem sofre | Problema atual |
|---|---|
| Aluno | Não sabe quando ou onde encontrar o monitor |
| Monitor | Dificuldade de organizar horários e registrar atendimentos |
| Professor | Não tem dados para avaliar o impacto da monitoria |
| Secretaria | Não consegue controlar bolsas — frequência, relatórios e pagamentos não se comunicam |

---

## Personas

### Ana — Aluna
**Perfil:** Aluna do 2º período de Engenharia, com dificuldade em Cálculo II.
**Dores:**
- Não sabe quando vai ter monitoria nem como avisar que não vai conseguir comparecer
- Tem dificuldade de comunicar previamente ao monitor quais são suas dificuldades
- Quando vai, o monitor muitas vezes não está preparado
- Quando não pode ir, não tem como acompanhar o que foi visto

**O que ela precisa:** agendar um horário, informar suas dificuldades com antecedência, e acessar um registro do que foi coberto na monitoria.

---

### Lucas — Monitor
**Perfil:** Aluno do 4º período, monitor de Programação I.
**Dores:**
- Não tem como avisar todos os alunos sobre os horários
- Abre a sala e não vai ninguém, sem aviso prévio
- Não sabe o que os alunos precisam antes do encontro
- Conteúdo produzido na monitoria fica perdido, não fica acessível a todos
- Tem que comprovar horas para a secretaria manualmente

**O que ele precisa:** divulgar horários, saber o que os alunos precisam antes do encontro, e ter um mural por disciplina onde possa postar materiais e resoluções.

---

### Prof. Carlos — Professor
**Perfil:** Professor de Cálculo II, com alto índice de reprovação na turma.
**Dores:**
- Não tem visibilidade se a monitoria está acontecendo de fato
- Não recebe feedback se os alunos estão melhorando
- Não tem canal para coordenar estratégia com o monitor

**O que ele precisa:** acompanhar a frequência da monitoria e receber um resumo do que está sendo coberto.

---

### Secretaria / Coordenação
**Perfil:** Responsável pelo controle administrativo do programa de monitoria.
**Dores:**
- Controla tudo em planilha manualmente todo mês
- Não tem como saber automaticamente se um monitor está cumprindo a carga mínima
- Liberar ou suspender bolsas é um processo lento e sujeito a erro

**O que ela precisa:** painel que mostre automaticamente quais monitores cumpriram o mínimo de 1h semanal, com sinalização clara de quem está irregular.

---

## Objetivos do Produto

1. Centralizar cadastro de disciplinas, professores e monitores
2. Permitir que monitores gerenciem suas agendas de atendimento
3. Permitir que alunos encontrem e agendem atendimentos
4. Registrar os atendimentos realizados (presença, assunto)
5. Gerar relatórios de participação e frequência para tomada de decisão

---

## Fora do Escopo

- Integração com sistemas acadêmicos existentes (ex: SIGA)
- App mobile
- Videoconferência integrada

---

## Product Goal

> Ter um sistema que permita ao aluno encontrar um monitor e agendar um atendimento, ao monitor organizar sua agenda e registrar os atendimentos, à coordenação acompanhar a atividade dos monitores e controlar as bolsas — tudo em um único lugar.
