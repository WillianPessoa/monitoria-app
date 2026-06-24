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


def get_slot_with_monitor(disponibilidade_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT ds.id, ds.data_inicio, ds.data_fim, ds.local, ds.status,
                   u.nome AS monitor_nome
            FROM disponibilidades ds
            JOIN usuarios u ON u.id = ds.monitor_id
            WHERE ds.id = %s
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
            conn.rollback()
            return False, "Horário não encontrado."

        status, data_inicio, data_fim = row
        if status != 'DISPONIVEL':
            conn.rollback()
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
            conn.rollback()
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
            conn.rollback()
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


def list_agendamentos_for_aluno(aluno_id, now_value):
    """Agendamentos futuros confirmados do aluno em disponibilidades individuais (US14)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT a.id AS agendamento_id,
                   ds.id AS disponibilidade_id,
                   ds.data_inicio,
                   ds.data_fim,
                   ds.local,
                   di.id AS disciplina_id,
                   di.codigo AS disciplina_codigo,
                   di.nome AS disciplina_nome,
                   u.nome AS monitor_nome
            FROM agendamentos a
            JOIN disponibilidades ds ON ds.id = a.disponibilidade_id
            JOIN disciplinas di ON di.id = ds.disciplina_id
            JOIN usuarios u ON u.id = ds.monitor_id
            WHERE a.aluno_id = %s
              AND a.status = 'CONFIRMADO'
              AND ds.data_inicio > %s
            ORDER BY ds.data_inicio ASC
            """,
            (aluno_id, now_value),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_agendamento_by_id(agendamento_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT a.id, a.aluno_id, a.disponibilidade_id, a.status,
                   ds.data_inicio, ds.data_fim
            FROM agendamentos a
            JOIN disponibilidades ds ON ds.id = a.disponibilidade_id
            WHERE a.id = %s
            """,
            (agendamento_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def cancel_agendamento_db(agendamento_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT disponibilidade_id FROM agendamentos
            WHERE id = %s AND status = 'CONFIRMADO'
            FOR UPDATE
            """,
            (agendamento_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return False
        disponibilidade_id = row[0]
        cursor.execute(
            "UPDATE agendamentos SET status = 'CANCELADO', atualizado_em = CURRENT_TIMESTAMP WHERE id = %s",
            (agendamento_id,),
        )
        cursor.execute(
            "UPDATE disponibilidades SET status = 'DISPONIVEL', atualizado_em = CURRENT_TIMESTAMP WHERE id = %s AND status = 'AGENDADO'",
            (disponibilidade_id,),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def block_slot(disponibilidade_id, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT status FROM disponibilidades WHERE id = %s AND monitor_id = %s FOR UPDATE",
            (disponibilidade_id, monitor_id),
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return False, "NAO_ENCONTRADO"
        if row[0] != "DISPONIVEL":
            conn.rollback()
            return False, "INDISPONIVEL"
        cursor.execute(
            "UPDATE disponibilidades SET status = 'BLOQUEADO', atualizado_em = CURRENT_TIMESTAMP WHERE id = %s",
            (disponibilidade_id,),
        )
        conn.commit()
        return True, None
    except Exception:
        conn.rollback()
        return False, "ERRO"
    finally:
        cursor.close()
        conn.close()


def unblock_slot(disponibilidade_id, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT status FROM disponibilidades WHERE id = %s AND monitor_id = %s FOR UPDATE",
            (disponibilidade_id, monitor_id),
        )
        row = cursor.fetchone()
        if not row or row[0] != "BLOQUEADO":
            conn.rollback()
            return False
        cursor.execute(
            "UPDATE disponibilidades SET status = 'DISPONIVEL', atualizado_em = CURRENT_TIMESTAMP WHERE id = %s",
            (disponibilidade_id,),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def list_past_sessions_for_aluno(aluno_id, now_value, disciplina_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        extra = "AND d.id = %s" if disciplina_id else ""
        params = [aluno_id, aluno_id, now_value]
        if disciplina_id:
            params.append(disciplina_id)
        cursor.execute(
            f"""
            SELECT s.id AS sessao_id,
                   s.data_inicio,
                   s.data_fim,
                   s.assunto,
                   d.codigo AS disciplina_codigo,
                   d.nome AS disciplina_nome,
                   u.nome AS monitor_nome,
                   p.status AS presenca_status
            FROM monitoria_sessoes s
            JOIN disciplinas d ON d.id = s.disciplina_id
            JOIN usuarios u ON u.id = s.monitor_id
            JOIN disciplina_alunos da ON da.disciplina_id = d.id AND da.aluno_id = %s
            LEFT JOIN presencas p ON p.sessao_id = s.id AND p.aluno_id = %s
            WHERE s.data_fim < %s
              AND s.status = 'CONCLUIDA'
              {extra}
            ORDER BY s.data_inicio DESC
            LIMIT 30
            """,
            params,
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_weekly_sessions_for_aluno(aluno_id, now_value):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT s.id AS sessao_id,
                   s.data_inicio,
                   s.data_fim,
                   s.status AS sessao_status,
                   d.codigo AS disciplina_codigo,
                   d.nome AS disciplina_nome,
                   u.nome AS monitor_nome,
                   p.status AS presenca_status
            FROM monitoria_sessoes s
            JOIN disciplinas d ON d.id = s.disciplina_id
            JOIN usuarios u ON u.id = s.monitor_id
            JOIN disciplina_alunos da ON da.disciplina_id = d.id AND da.aluno_id = %s
            LEFT JOIN presencas p ON p.sessao_id = s.id AND p.aluno_id = %s
            WHERE s.data_inicio >= %s
              AND s.status = 'AGENDADA'
            ORDER BY s.data_inicio ASC
            """,
            (aluno_id, aluno_id, now_value),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
