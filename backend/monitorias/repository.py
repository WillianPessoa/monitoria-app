from db.connection import get_connection


def list_pending_monitorias():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               m.disciplina_id,
               d.nome AS disciplina,
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
            return False

        # Set the aluno user to MONITOR and ATIVO
        cursor.execute(
            """
            UPDATE usuarios
            SET papel = 'MONITOR', status = 'ATIVO', atualizado_em = CURRENT_TIMESTAMP
            WHERE id = (
                SELECT aluno_id FROM monitorias WHERE id = %s
            )
            """,
            (monitoria_id,),
        )
        conn.commit()
        return True
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
