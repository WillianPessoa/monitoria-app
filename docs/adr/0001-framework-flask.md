# ADR-0001 — Framework Python: Flask

**Data:** 2026-05-06  
**Status:** Aceito

## Contexto

O projeto precisa de um servidor HTTP em Python que exponha rotas para o frontend HTML+CSS. As opções avaliadas foram Flask, FastAPI e Django.

## Decisão

**Flask.**

## Justificativa

- O time tem 5 sprints curtas e o objetivo da disciplina é aprender o processo, não dominar um framework
- Flask é minimal e sem opinião forte — o time monta a estrutura explicitamente, o que torna o aprendizado mais transparente
- FastAPI exige async e type hints, com curva de aprendizado desnecessária para o escopo
- Django esconde demais o que acontece — ruim para uma disciplina onde o processo de desenvolvimento é o objeto de estudo

## Consequências

- A estrutura de pastas e a organização de rotas são responsabilidade do time (ver ADR-0002)
- Sem ORM embutido — banco de dados tratado separadamente (ver ADR-0004)
- Jinja2 disponível nativamente para renderização de templates
