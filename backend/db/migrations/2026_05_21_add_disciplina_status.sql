-- Adiciona coluna status à tabela disciplinas.
-- Esta coluna foi incluída diretamente no schema.sql mas faltou a migration
-- correspondente, causando erro em bancos criados antes desta data.
ALTER TABLE disciplinas
ADD COLUMN status ENUM('ATIVA', 'INATIVA') NOT NULL DEFAULT 'ATIVA'
AFTER professor_id;
