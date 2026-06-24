from db.connection import get_connection


def get_sumario_participacao(disciplina_id, data_inicio, data_fim):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                d.codigo AS disciplina_codigo,
                d.nome   AS disciplina_nome,
                (SELECT COUNT(DISTINCT s.id)
                 FROM monitoria_sessoes s
                 WHERE s.disciplina_id = d.id
                   AND s.status = 'CONCLUIDA'
                   AND DATE(s.data_inicio) BETWEEN %s AND %s) AS total_sessoes,
                (SELECT COUNT(DISTINCT p.aluno_id)
                 FROM presencas p
                 JOIN monitoria_sessoes s ON s.id = p.sessao_id
                 WHERE s.disciplina_id = d.id
                   AND s.status = 'CONCLUIDA'
                   AND DATE(s.data_inicio) BETWEEN %s AND %s
                   AND p.status = 'CONFIRMADA') AS alunos_atendidos,
                (SELECT COALESCE(ROUND(
                     SUM(TIMESTAMPDIFF(MINUTE, s.data_inicio, s.data_fim)) / 60, 2), 0)
                 FROM monitoria_sessoes s
                 WHERE s.disciplina_id = d.id
                   AND s.status = 'CONCLUIDA'
                   AND DATE(s.data_inicio) BETWEEN %s AND %s
                   AND EXISTS (
                       SELECT 1 FROM presencas p
                       WHERE p.sessao_id = s.id AND p.status = 'CONFIRMADA'
                   )) AS horas_realizadas,
                (SELECT COUNT(DISTINCT s.monitor_id)
                 FROM monitoria_sessoes s
                 WHERE s.disciplina_id = d.id
                   AND s.status = 'CONCLUIDA'
                   AND DATE(s.data_inicio) BETWEEN %s AND %s) AS monitores_ativos
            FROM disciplinas d
            WHERE d.id = %s AND d.status = 'ATIVA'
            """,
            [
                data_inicio, data_fim,
                data_inicio, data_fim,
                data_inicio, data_fim,
                data_inicio, data_fim,
                disciplina_id,
            ],
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_detalhes_por_monitor(disciplina_id, data_inicio, data_fim):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.nome AS monitor_nome,
                COUNT(DISTINCT s.id) AS sessoes,
                COALESCE(ROUND(
                    SUM(TIMESTAMPDIFF(MINUTE, s.data_inicio, s.data_fim)) / 60, 2), 0) AS horas,
                COUNT(DISTINCT p.aluno_id) AS alunos_atendidos
            FROM monitorias m
            JOIN usuarios u ON u.id = m.aluno_id
            LEFT JOIN monitoria_sessoes s
                ON s.disciplina_id = m.disciplina_id
               AND s.monitor_id   = m.aluno_id
               AND s.status       = 'CONCLUIDA'
               AND DATE(s.data_inicio) BETWEEN %s AND %s
            LEFT JOIN presencas p ON p.sessao_id = s.id AND p.status = 'CONFIRMADA'
            WHERE m.disciplina_id = %s
              AND m.status = 'ATIVO'
            GROUP BY m.aluno_id, u.nome
            ORDER BY u.nome ASC
            """,
            [data_inicio, data_fim, disciplina_id],
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


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
                   m.disciplina_id AS disciplina_id,
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
