from db.connection import get_connection


def list_disciplinas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT d.id,
                   d.codigo,
                   d.nome,
                   d.status,
                   d.professor_id,
                   p.nome AS professor_nome,
                   d.criado_em
            FROM disciplinas d
            JOIN usuarios p ON p.id = d.professor_id
            ORDER BY d.criado_em DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_by_professor(professor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
        SELECT id, codigo, nome
            FROM disciplinas
        WHERE professor_id = %s
          AND status = 'ATIVA'
            ORDER BY nome ASC
        """,
            (professor_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_disciplina_by_codigo(codigo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, codigo
            FROM disciplinas
            WHERE codigo = %s
            """,
            (codigo,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_disciplina(codigo, nome, professor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO disciplinas (codigo, nome, professor_id)
            VALUES (%s, %s, %s)
            """,
            (codigo, nome, professor_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def list_disciplinas_admin():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT d.id,
                   d.codigo,
                   d.nome,
                   d.status,
                   d.professor_id,
                   p.nome AS professor_nome,
                   m.aluno_id AS monitor_aluno_id,
                   a.nome AS monitor_nome,
                   COUNT(DISTINCT da.aluno_id) AS alunos_count,
                   d.criado_em
            FROM disciplinas d
            JOIN usuarios p ON p.id = d.professor_id
            LEFT JOIN monitorias m
              ON m.disciplina_id = d.id
             AND m.status = 'ATIVO'
            LEFT JOIN usuarios a ON a.id = m.aluno_id
            LEFT JOIN disciplina_alunos da ON da.disciplina_id = d.id
            GROUP BY d.id, d.codigo, d.nome, d.status, d.professor_id, p.nome, m.aluno_id, a.nome, d.criado_em
            ORDER BY d.criado_em DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_disciplina_by_id(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, codigo, nome, professor_id, status
            FROM disciplinas
            WHERE id = %s
            """,
            (disciplina_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_disciplina(disciplina_id, codigo, nome, professor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE disciplinas
            SET codigo = %s,
                nome = %s,
                professor_id = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (codigo, nome, professor_id, disciplina_id),
        )
        affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def set_disciplina_status(disciplina_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE disciplinas
            SET status = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (status, disciplina_id),
        )
        affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def list_alunos_by_disciplina(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.id, u.nome, u.email
            FROM disciplina_alunos da
            JOIN usuarios u ON u.id = da.aluno_id
            WHERE da.disciplina_id = %s
            ORDER BY u.nome ASC
            """,
            (disciplina_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_alunos_nao_matriculados(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.id, u.nome, u.email
            FROM usuarios u
            LEFT JOIN disciplina_alunos da
                ON da.aluno_id = u.id
             AND da.disciplina_id = %s
            WHERE u.papel = 'ALUNO'
                AND u.status = 'ATIVO'
                AND da.id IS NULL
            ORDER BY u.nome ASC
            """,
            (disciplina_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_alunos_by_disciplina_filtered(disciplina_id, term):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        like_term = f"%{term}%"
        cursor.execute(
            """
            SELECT u.id, u.nome, u.email
            FROM disciplina_alunos da
            JOIN usuarios u ON u.id = da.aluno_id
            WHERE da.disciplina_id = %s
              AND (u.nome LIKE %s OR u.email LIKE %s)
            ORDER BY u.nome ASC
            """,
            (disciplina_id, like_term, like_term),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def count_alunos_disciplina(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM disciplina_alunos
            WHERE disciplina_id = %s
            """,
            (disciplina_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def list_disciplinas_by_aluno(aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT d.id, d.codigo, d.nome
            FROM disciplina_alunos da
            JOIN disciplinas d ON d.id = da.disciplina_id
            WHERE da.aluno_id = %s
              AND d.status = 'ATIVA'
            ORDER BY d.nome ASC
            """,
            (aluno_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_by_professor_with_stats(professor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT d.id,
                   d.codigo,
                   d.nome,
                   d.status,
                   m.aluno_id AS monitor_aluno_id,
                   a.nome AS monitor_nome,
                   COUNT(DISTINCT da.aluno_id) AS alunos_count
            FROM disciplinas d
            LEFT JOIN monitorias m
              ON m.disciplina_id = d.id
             AND m.status = 'ATIVO'
            LEFT JOIN usuarios a ON a.id = m.aluno_id
            LEFT JOIN disciplina_alunos da ON da.disciplina_id = d.id
            WHERE d.professor_id = %s
              AND d.status = 'ATIVA'
            GROUP BY d.id, d.codigo, d.nome, d.status, m.aluno_id, a.nome
            ORDER BY d.nome ASC
            """,
            (professor_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def add_aluno_to_disciplina(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO disciplina_alunos (disciplina_id, aluno_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE atualizado_em = CURRENT_TIMESTAMP
            """,
            (disciplina_id, aluno_id),
        )
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def remove_aluno_from_disciplina(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM disciplina_alunos
            WHERE disciplina_id = %s AND aluno_id = %s
            """,
            (disciplina_id, aluno_id),
        )
        affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def remove_alunos_from_disciplina(disciplina_id, aluno_ids):
    if not aluno_ids:
        return 0
    conn = get_connection()
    cursor = conn.cursor()
    try:
        placeholders = ", ".join(["%s"] * len(aluno_ids))
        cursor.execute(
            f"""
            DELETE FROM disciplina_alunos
            WHERE disciplina_id = %s
              AND aluno_id IN ({placeholders})
            """,
            (disciplina_id, *aluno_ids),
        )
        affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        cursor.close()
        conn.close()


def list_sessoes_com_presencas(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT s.id AS sessao_id,
                   s.data_inicio,
                   s.data_fim,
                   s.assunto,
                   m.nome AS monitor_nome,
                   a.nome AS aluno_nome,
                   p.status AS presenca_status
            FROM monitoria_sessoes s
            JOIN usuarios m ON m.id = s.monitor_id
            JOIN presencas p ON p.sessao_id = s.id
            JOIN usuarios a ON a.id = p.aluno_id
            WHERE s.disciplina_id = %s
              AND s.status = 'CONCLUIDA'
              AND p.status IN ('CONFIRMADA', 'AUSENTE')
            ORDER BY s.data_inicio DESC, a.nome ASC
            """,
            (disciplina_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_alunos_com_presencas(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.id, u.nome, u.email,
                   COUNT(p.id) AS presencas_confirmadas
            FROM disciplina_alunos da
            JOIN usuarios u ON u.id = da.aluno_id
            LEFT JOIN presencas p
                ON p.aluno_id = da.aluno_id
               AND p.status = 'CONFIRMADA'
               AND p.sessao_id IN (
                   SELECT id FROM monitoria_sessoes
                   WHERE disciplina_id = %s AND status = 'CONCLUIDA'
               )
            WHERE da.disciplina_id = %s
            GROUP BY u.id, u.nome, u.email
            ORDER BY u.nome ASC
            """,
            (disciplina_id, disciplina_id),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_total_horas_concluidas(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COALESCE(
                SUM(TIMESTAMPDIFF(MINUTE, data_inicio, data_fim)) / 60.0,
                0
            )
            FROM monitoria_sessoes
            WHERE disciplina_id = %s AND status = 'CONCLUIDA'
            """,
            (disciplina_id,),
        )
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    finally:
        cursor.close()
        conn.close()


def list_sessoes_resumo(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT s.id,
                   s.data_inicio,
                   s.data_fim,
                   s.assunto,
                   s.status,
                   u.nome AS monitor_nome,
                   COUNT(p.id) AS total_presentes
            FROM monitoria_sessoes s
            JOIN usuarios u ON u.id = s.monitor_id
            LEFT JOIN presencas p
                ON p.sessao_id = s.id AND p.status = 'CONFIRMADA'
            WHERE s.disciplina_id = %s AND s.status = 'CONCLUIDA'
            GROUP BY s.id, s.data_inicio, s.data_fim, s.assunto, s.status, u.nome
            ORDER BY s.data_inicio DESC
            """,
            (disciplina_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_disciplinas_ativas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT d.id,
                   d.codigo,
                   d.nome,
                   d.status,
                   d.professor_id,
                   p.nome AS professor_nome,
                   d.criado_em
            FROM disciplinas d
            JOIN usuarios p ON p.id = d.professor_id
            WHERE d.status = 'ATIVA'
            ORDER BY d.nome ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_disciplinas_admin_filtered(q=None, status=None, professor_id=None, aluno_id=None, min_hours=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conditions = []
        params = []

        if status and status != "TODAS":
            conditions.append("d.status = %s")
            params.append(status)

        if q:
            like_q = f"%{q}%"
            conditions.append("(d.codigo LIKE %s OR d.nome LIKE %s)")
            params.extend([like_q, like_q])

        if professor_id:
            conditions.append("d.professor_id = %s")
            params.append(professor_id)

        if aluno_id:
            conditions.append(
                "EXISTS (SELECT 1 FROM disciplina_alunos daf WHERE daf.disciplina_id = d.id AND daf.aluno_id = %s)"
            )
            params.append(aluno_id)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        cursor.execute(
            f"""
            SELECT d.id,
                   d.codigo,
                   d.nome,
                   d.status,
                   d.professor_id,
                   p.nome AS professor_nome,
                   m.aluno_id AS monitor_aluno_id,
                   a.nome AS monitor_nome,
                   COUNT(DISTINCT da.aluno_id) AS alunos_count,
                   d.criado_em,
                   (SELECT COALESCE(SUM(TIMESTAMPDIFF(MINUTE, ms.data_inicio, ms.data_fim) / 60.0), 0)
                    FROM monitoria_sessoes ms
                    WHERE ms.disciplina_id = d.id AND ms.status = 'CONCLUIDA') AS total_horas,
                   GREATEST(
                       DATEDIFF(
                           CASE WHEN d.status = 'ATIVA' THEN CURDATE()
                               ELSE COALESCE(
                                   (SELECT DATE(MAX(ms2.data_inicio))
                                    FROM monitoria_sessoes ms2
                                    WHERE ms2.disciplina_id = d.id AND ms2.status = 'CONCLUIDA'),
                                   DATE(d.criado_em))
                           END,
                           DATE(d.criado_em)
                       ) / 7.0,
                       1
                   ) AS semanas_ativas
            FROM disciplinas d
            JOIN usuarios p ON p.id = d.professor_id
            LEFT JOIN monitorias m ON m.disciplina_id = d.id AND m.status = 'ATIVO'
            LEFT JOIN usuarios a ON a.id = m.aluno_id
            LEFT JOIN disciplina_alunos da ON da.disciplina_id = d.id
            {where_clause}
            GROUP BY d.id, d.codigo, d.nome, d.status, d.professor_id, p.nome, m.aluno_id, a.nome, d.criado_em
            ORDER BY d.criado_em DESC
            """,
            params,
        )
        rows = cursor.fetchall()
        for row in rows:
            row["cumpre_minimo"] = float(row["total_horas"]) >= float(row["semanas_ativas"])

        if min_hours == "cumpridas":
            rows = [r for r in rows if r["cumpre_minimo"]]
        elif min_hours == "nao_cumpridas":
            rows = [r for r in rows if not r["cumpre_minimo"]]

        return rows
    finally:
        cursor.close()
        conn.close()


def is_aluno_matriculado(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 1
            FROM disciplina_alunos
            WHERE disciplina_id = %s AND aluno_id = %s
            LIMIT 1
            """,
            (disciplina_id, aluno_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
