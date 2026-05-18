# Modelagem do Banco de Dados

Modelo inicial para suportar EP00 e EP01 (infra + perfis/autenticacao), mantendo compatibilidade com EP02 em diante.

## Diagrama ER (Mermaid)

```mermaid
erDiagram
    USUARIOS {
        BIGINT id PK
        VARCHAR nome
        VARCHAR email UK
        VARCHAR senha_hash
        ENUM papel
        ENUM status
        BOOLEAN senha_temporaria
        VARCHAR contato
        TEXT disponibilidade
        TIMESTAMP criado_em
        TIMESTAMP atualizado_em
    }

    PASSWORD_RESET_TOKENS {
        BIGINT id PK
        BIGINT usuario_id FK
        VARCHAR token UK
        DATETIME expira_em
        BOOLEAN usado
        TIMESTAMP criado_em
    }

    DISCIPLINAS {
        BIGINT id PK
        VARCHAR codigo UK
        VARCHAR nome
        BIGINT professor_id FK
        TIMESTAMP criado_em
        TIMESTAMP atualizado_em
    }

    MONITORIAS {
        BIGINT id PK
        BIGINT disciplina_id FK
        BIGINT professor_id FK
        BIGINT aluno_id FK
        ENUM status
        VARCHAR motivo_rejeicao
        TIMESTAMP criado_em
        TIMESTAMP atualizado_em
    }

    USUARIOS ||--o{ PASSWORD_RESET_TOKENS : possui
    USUARIOS ||--o{ DISCIPLINAS : leciona
    USUARIOS ||--o{ MONITORIAS : participa
    DISCIPLINAS ||--o{ MONITORIAS : contem
```

## Arquivo SQL

O schema completo esta em [backend/db/schema.sql](../backend/db/schema.sql).
