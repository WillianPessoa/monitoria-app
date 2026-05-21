from db.connection import get_connection


def list_monitorias_ativas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.id,
               d.codigo,
               d.nome AS disciplina_nome,
               a.nome AS monitor_nome,
               p.nome AS professor_nome
        FROM monitorias m
        JOIN disciplinas d ON d.id = m.disciplina_id
        JOIN usuarios a ON a.id = m.aluno_id
        JOIN usuarios p ON p.id = m.professor_id
        WHERE m.status = 'ATIVO'
        ORDER BY d.nome, a.nome
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
