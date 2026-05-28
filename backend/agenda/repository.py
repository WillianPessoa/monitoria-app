from db.connection import get_connection


def list_available_slots_for_aluno(aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT ds.id AS disponibilidade_id,
                   ds.disciplina_id,
                   di.codigo AS disciplina_codigo,
                   di.nome AS disciplina_nome,
                   ds.monitor_id,
                   u.nome AS monitor_nome,
                   ds.data_inicio,
                   ds.data_fim,
                   ds.local
            FROM disponibilidades ds
            JOIN disciplinas di ON di.id = ds.disciplina_id
            JOIN usuarios u ON u.id = ds.monitor_id
            JOIN monitorias m ON m.disciplina_id = di.id
               AND m.aluno_id = ds.monitor_id
               AND m.status = 'ATIVO'
            JOIN disciplina_alunos da ON da.disciplina_id = di.id
               AND da.aluno_id = %s
            WHERE ds.status = 'DISPONIVEL'
              AND ds.data_inicio > NOW()
              AND di.status = 'ATIVA'
            ORDER BY ds.data_inicio ASC
            """,
            (aluno_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_slots_for_monitor(monitor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT ds.id AS disponibilidade_id,
                   ds.disciplina_id,
                   di.codigo AS disciplina_codigo,
                   di.nome AS disciplina_nome,
                   ds.data_inicio,
                   ds.data_fim,
                   ds.local,
                   ds.status,
                   a.id AS agendamento_id,
                   a.aluno_id,
                   au.nome AS aluno_nome
            FROM disponibilidades ds
            JOIN disciplinas di ON di.id = ds.disciplina_id
            LEFT JOIN agendamentos a
              ON a.disponibilidade_id = ds.id
             AND a.status = 'CONFIRMADO'
            LEFT JOIN usuarios au ON au.id = a.aluno_id
            WHERE ds.monitor_id = %s
            ORDER BY ds.data_inicio ASC
            """,
            (monitor_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_disponibilidade_by_id(disponibilidade_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, disciplina_id, monitor_id, data_inicio, data_fim, status
            FROM disponibilidades
            WHERE id = %s
            """,
            (disponibilidade_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def student_has_conflict(aluno_id, data_inicio, data_fim):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 1
            FROM agendamentos a
            JOIN disponibilidades ds ON ds.id = a.disponibilidade_id
            WHERE a.aluno_id = %s
              AND a.status = 'CONFIRMADO'
              AND ds.data_inicio < %s
              AND ds.data_fim > %s
            LIMIT 1
            """,
            (aluno_id, data_fim, data_inicio),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def monitor_has_overlap(monitor_id, data_inicio, data_fim, exclude_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 1
            FROM disponibilidades
            WHERE monitor_id = %s
              AND data_inicio < %s
              AND data_fim > %s
        """
        params = [monitor_id, data_fim, data_inicio]
        if exclude_id is not None:
            query += " AND id != %s"
            params.append(exclude_id)
        query += " LIMIT 1"
        cursor.execute(query, params)
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def create_disponibilidade(monitor_id, disciplina_id, data_inicio, data_fim, local=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
            VALUES (%s, %s, %s, %s, %s, 'DISPONIVEL')
            """,
            (disciplina_id, monitor_id, data_inicio, data_fim, local),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def reserve_slot(disponibilidade_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT status, data_inicio, data_fim
            FROM disponibilidades
            WHERE id = %s
            FOR UPDATE
            """,
            (disponibilidade_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.commit()
            return False, "Horário não encontrado."

        status, data_inicio, data_fim = row
        if status != 'DISPONIVEL':
            conn.commit()
            return False, "Horário indisponível."

        cursor.execute(
            """
            SELECT 1
            FROM agendamentos a
            JOIN disponibilidades ds ON ds.id = a.disponibilidade_id
            WHERE a.aluno_id = %s
              AND a.status = 'CONFIRMADO'
              AND ds.data_inicio < %s
              AND ds.data_fim > %s
            LIMIT 1
            """,
            (aluno_id, data_fim, data_inicio),
        )
        if cursor.fetchone():
            conn.commit()
            return False, "Você já possui um agendamento no mesmo período."

        cursor.execute(
            """
            UPDATE disponibilidades
            SET status = 'AGENDADO', atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'DISPONIVEL'
            """,
            (disponibilidade_id,),
        )
        if cursor.rowcount == 0:
            conn.commit()
            return False, "Horário indisponível."

        cursor.execute(
            """
            INSERT INTO agendamentos (disponibilidade_id, aluno_id, status)
            VALUES (%s, %s, 'CONFIRMADO')
            """,
            (disponibilidade_id, aluno_id),
        )
        conn.commit()
        return True, None
    finally:
        cursor.close()
        conn.close()
