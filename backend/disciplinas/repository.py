from db.connection import get_connection


def list_disciplinas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_by_professor(professor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_disciplina_by_codigo(codigo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, codigo
        FROM disciplinas
        WHERE codigo = %s
        """,
        (codigo,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_disciplina(codigo, nome, professor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO disciplinas (codigo, nome, professor_id)
        VALUES (%s, %s, %s)
        """,
        (codigo, nome, professor_id),
    )
    conn.commit()
    disciplina_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return disciplina_id


def list_disciplinas_admin():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_disciplina_by_id(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, codigo, nome, professor_id, status
        FROM disciplinas
        WHERE id = %s
        """,
        (disciplina_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_disciplina(disciplina_id, codigo, nome, professor_id):
    conn = get_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return affected > 0


def set_disciplina_status(disciplina_id, status):
    conn = get_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return affected > 0


def list_alunos_by_disciplina(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_alunos_nao_matriculados(disciplina_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
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
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows


def list_alunos_by_disciplina_filtered(disciplina_id, term):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_disciplinas_by_aluno(aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_by_professor_with_stats(professor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
        GROUP BY d.id, d.codigo, d.nome, d.status, m.aluno_id, a.nome
        ORDER BY d.nome ASC
        """,
        (professor_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_aluno_to_disciplina(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO disciplina_alunos (disciplina_id, aluno_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE atualizado_em = CURRENT_TIMESTAMP
        """,
        (disciplina_id, aluno_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True


def remove_aluno_from_disciplina(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM disciplina_alunos
        WHERE disciplina_id = %s AND aluno_id = %s
        """,
        (disciplina_id, aluno_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


def remove_alunos_from_disciplina(disciplina_id, aluno_ids):
    if not aluno_ids:
        return 0
    conn = get_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return affected


def is_aluno_matriculado(disciplina_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM disciplina_alunos
        WHERE disciplina_id = %s AND aluno_id = %s
        LIMIT 1
        """,
        (disciplina_id, aluno_id),
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists
