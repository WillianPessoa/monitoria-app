# ADR-0004 — Acesso ao banco: mysql-connector-python com queries diretas

**Data:** 2026-05-06  
**Status:** Aceito

## Contexto

O projeto usa MySQL como banco de dados. As opções avaliadas foram SQLAlchemy (ORM) e mysql-connector-python com SQL explícito.

## Decisão

**mysql-connector-python com queries SQL diretas.**

## Justificativa

- O time já modela o banco em TT02 — faz sentido que o código reflita esse modelo diretamente em SQL, sem abstração adicional
- SQLAlchemy tem curva de aprendizado relevante e esconde o comportamento do banco, o que é indesejável em uma disciplina onde o processo é o objeto de estudo
- Queries diretas são mais fáceis de debugar: o SQL executado é exatamente o que está no código

## Implementação

Cada blueprint tem um `repository.py` com funções que encapsulam as queries:

```python
# agenda/repository.py
def listar_disponibilidades(monitor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM disponibilidade WHERE monitor_id = %s AND data >= CURDATE()",
        (monitor_id,)
    )
    return cursor.fetchall()
```

- Conexão gerenciada via `db/connection.py` com pool simples
- Parâmetros sempre via placeholder `%s` — nunca interpolação de string (prevenção de SQL injection)
- Módulo `db/` compartilhado entre blueprints

## Consequências

- SQL injection só é prevenido se o time usar placeholders consistentemente — QM deve verificar isso na Validação Paralela
- Sem migrations automáticas — schema gerenciado manualmente via `schema.sql` (ver TT02)
- Mudanças no schema exigem atualização manual do `schema.sql` e dos repositórios afetados
