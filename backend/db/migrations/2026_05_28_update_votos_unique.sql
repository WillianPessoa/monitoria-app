SET @idx_opcao_sql = (
	SELECT IF(
		COUNT(*) = 0,
		'CREATE INDEX idx_votos_opcao_id ON votos (opcao_id)',
		'SELECT 1'
	)
	FROM information_schema.STATISTICS
	WHERE TABLE_SCHEMA = DATABASE()
		AND TABLE_NAME = 'votos'
		AND INDEX_NAME = 'idx_votos_opcao_id'
);
PREPARE stmt FROM @idx_opcao_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_aluno_sql = (
	SELECT IF(
		COUNT(*) = 0,
		'CREATE INDEX idx_votos_aluno_id ON votos (aluno_id)',
		'SELECT 1'
	)
	FROM information_schema.STATISTICS
	WHERE TABLE_SCHEMA = DATABASE()
		AND TABLE_NAME = 'votos'
		AND INDEX_NAME = 'idx_votos_aluno_id'
);
PREPARE stmt FROM @idx_aluno_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_votacao_sql = (
	SELECT IF(
		COUNT(*) = 0,
		'CREATE INDEX idx_votos_votacao_id ON votos (votacao_id)',
		'SELECT 1'
	)
	FROM information_schema.STATISTICS
	WHERE TABLE_SCHEMA = DATABASE()
		AND TABLE_NAME = 'votos'
		AND INDEX_NAME = 'idx_votos_votacao_id'
);
PREPARE stmt FROM @idx_votacao_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_drop_sql = (
	SELECT IF(
		COUNT(*) > 0,
		'ALTER TABLE votos DROP INDEX uq_voto_unico',
		'SELECT 1'
	)
	FROM information_schema.STATISTICS
	WHERE TABLE_SCHEMA = DATABASE()
		AND TABLE_NAME = 'votos'
		AND INDEX_NAME = 'uq_voto_unico'
);
PREPARE stmt FROM @idx_drop_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

ALTER TABLE votos ADD UNIQUE KEY uq_voto_unico (votacao_id, aluno_id, opcao_id);
