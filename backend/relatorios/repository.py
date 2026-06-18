from db.connection import get_connection


def list_horas_por_monitor(primeiro_dia, ultimo_dia, disciplina_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        params = [primeiro_dia, ultimo_dia]
        disciplina_filter = ""
        if disciplina_id:
            disciplina_filter = "AND m.disciplina_id = %s"
            params.append(disciplina_id)

        cursor.execute(
            f"""
            SELECT m.aluno_id AS monitor_id,
                   u.nome AS monitor_nome,
                   d.codigo AS disciplina_codigo,
                   d.nome AS disciplina_nome,
                   COALESCE(
                       ROUND(
                           SUM(TIMESTAMPDIFF(MINUTE, s.data_inicio, s.data_fim)) / 60,
                           2
                       ),
                       0
                   ) AS total_horas
            FROM monitorias m
            JOIN usuarios u ON u.id = m.aluno_id
            JOIN disciplinas d ON d.id = m.disciplina_id
            LEFT JOIN monitoria_sessoes s
              ON s.disciplina_id = m.disciplina_id
             AND s.monitor_id = m.aluno_id
             AND s.status = 'CONCLUIDA'
             AND s.data_inicio >= %s
             AND s.data_inicio <= %s
             AND EXISTS (
                 SELECT 1
                 FROM presencas p
                 WHERE p.sessao_id = s.id
                   AND p.status = 'CONFIRMADA'
             )
            WHERE m.status = 'ATIVO'
              AND d.status = 'ATIVA'
              {disciplina_filter}
            GROUP BY m.aluno_id, u.nome, d.codigo, d.nome
            ORDER BY u.nome ASC
            """,
            params,
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
