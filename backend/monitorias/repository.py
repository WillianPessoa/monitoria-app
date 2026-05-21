from db.connection import get_connection


def list_pending_monitorias():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               m.disciplina_id,
               d.nome AS disciplina,
               d.codigo AS disciplina_codigo,
               m.professor_id,
               p.nome AS professor_nome,
               m.aluno_id,
               a.nome AS aluno_nome,
               m.criado_em
        FROM monitorias m
        JOIN disciplinas d ON d.id = m.disciplina_id
        JOIN usuarios p ON p.id = m.professor_id
        JOIN usuarios a ON a.id = m.aluno_id
        WHERE m.status = 'PENDENTE_APROVACAO'
          AND d.status = 'ATIVA'
        ORDER BY m.criado_em DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def approve_monitoria(monitoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT m.aluno_id, m.disciplina_id
            FROM monitorias m
            JOIN disciplinas d ON d.id = m.disciplina_id
            WHERE m.id = %s
              AND m.status = 'PENDENTE_APROVACAO'
              AND d.status = 'ATIVA'
            """,
            (monitoria_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.commit()
            return False, "NAO_ENCONTRADA"

        aluno_id, disciplina_id = row
        cursor.execute(
            """
            SELECT 1
            FROM monitorias
            WHERE aluno_id = %s
              AND status = 'ATIVO'
              AND id <> %s
            LIMIT 1
            """,
            (aluno_id, monitoria_id),
        )
        if cursor.fetchone():
            conn.commit()
            return False, "ALUNO_JA_MONITOR"

        # Update monitoria status if still pending
        cursor.execute(
            """
            UPDATE monitorias
            SET status = 'ATIVO', atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'PENDENTE_APROVACAO'
            """,
            (monitoria_id,),
        )
        if cursor.rowcount == 0:
            conn.commit()
            return False, "NAO_ENCONTRADA"

        cursor.execute(
            """
            DELETE FROM disciplina_alunos
            WHERE disciplina_id = %s AND aluno_id = %s
            """,
            (disciplina_id, aluno_id),
        )
        conn.commit()
        return True, None
    finally:
        cursor.close()
        conn.close()


def reject_monitoria(monitoria_id, motivo_rejeicao=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE monitorias
            SET status = 'REJEITADO', motivo_rejeicao = %s, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'PENDENTE_APROVACAO'
            """,
            (motivo_rejeicao or None, monitoria_id),
        )
        affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def list_active_monitorias():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               m.disciplina_id,
               d.codigo AS disciplina_codigo,
               d.nome AS disciplina_nome,
               m.professor_id,
               p.nome AS professor_nome,
               m.aluno_id,
               a.nome AS aluno_nome,
               m.criado_em
        FROM monitorias m
        JOIN disciplinas d ON d.id = m.disciplina_id
        JOIN usuarios p ON p.id = m.professor_id
                JOIN usuarios a ON a.id = m.aluno_id
                WHERE m.status = 'ATIVO'
                    AND d.status = 'ATIVA'
        ORDER BY m.criado_em DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def create_indicacao(disciplina_id, professor_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
            VALUES (%s, %s, %s, 'PENDENTE_APROVACAO')
            ON DUPLICATE KEY UPDATE
                status = 'PENDENTE_APROVACAO',
                professor_id = VALUES(professor_id),
                motivo_rejeicao = NULL,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (disciplina_id, professor_id, aluno_id),
        )
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def has_active_monitoria(aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM monitorias
        WHERE aluno_id = %s
          AND status = 'ATIVO'
        LIMIT 1
        """,
        (aluno_id,),
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists


def list_by_professor(professor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               d.id AS disciplina_id,
               d.codigo AS disciplina_codigo,
               d.nome AS disciplina_nome,
               a.nome AS aluno_nome,
               m.status,
               m.motivo_rejeicao,
               m.criado_em
        FROM monitorias m
        JOIN disciplinas d ON d.id = m.disciplina_id
        JOIN usuarios a ON a.id = m.aluno_id
        WHERE m.professor_id = %s
        ORDER BY m.criado_em DESC
        """,
        (professor_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_active_by_aluno(aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               d.id AS disciplina_id,
               d.codigo AS disciplina_codigo,
               d.nome AS disciplina_nome,
               p.nome AS professor_nome
        FROM monitorias m
        JOIN disciplinas d ON d.id = m.disciplina_id
        JOIN usuarios p ON p.id = m.professor_id
        WHERE m.aluno_id = %s
          AND m.status = 'ATIVO'
          AND d.status = 'ATIVA'
        LIMIT 1
        """,
        (aluno_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def deactivate_monitorias_by_disciplina(disciplina_id, motivo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE monitorias
        SET status = 'REJEITADO',
            motivo_rejeicao = %s,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE disciplina_id = %s
          AND status = 'ATIVO'
        """,
        (motivo, disciplina_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def deactivate_monitoria(disciplina_id, aluno_id, motivo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE monitorias
        SET status = 'REJEITADO',
            motivo_rejeicao = %s,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE disciplina_id = %s
          AND aluno_id = %s
          AND status = 'ATIVO'
        """,
        (motivo, disciplina_id, aluno_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def set_monitor_for_disciplina(disciplina_id, professor_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if aluno_id is None:
            cursor.execute(
                """
                UPDATE monitorias
                SET status = 'REJEITADO',
                    motivo_rejeicao = 'Monitor removido pelo admin.',
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE disciplina_id = %s
                  AND status = 'ATIVO'
                """,
                (disciplina_id,),
            )
            conn.commit()
            return True, None

        cursor.execute(
            """
            SELECT 1
            FROM monitorias
            WHERE aluno_id = %s
              AND status = 'ATIVO'
              AND disciplina_id <> %s
            LIMIT 1
            """,
            (aluno_id, disciplina_id),
        )
        if cursor.fetchone():
            conn.commit()
            return False, "Aluno ja possui monitoria ativa."

        cursor.execute(
            """
            UPDATE monitorias
            SET status = 'REJEITADO',
                motivo_rejeicao = 'Monitor trocado pelo admin.',
                atualizado_em = CURRENT_TIMESTAMP
            WHERE disciplina_id = %s
              AND status = 'ATIVO'
              AND aluno_id <> %s
            """,
            (disciplina_id, aluno_id),
        )

        cursor.execute(
            """
            INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
            VALUES (%s, %s, %s, 'ATIVO')
            ON DUPLICATE KEY UPDATE
                status = 'ATIVO',
                professor_id = VALUES(professor_id),
                motivo_rejeicao = NULL,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (disciplina_id, professor_id, aluno_id),
        )

        cursor.execute(
            """
            DELETE FROM disciplina_alunos
            WHERE disciplina_id = %s AND aluno_id = %s
            """,
            (disciplina_id, aluno_id),
        )
        conn.commit()
        return True, None
    finally:
        cursor.close()
        conn.close()
