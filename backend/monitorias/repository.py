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


def get_active_monitor_for_disciplina(disciplina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT m.aluno_id AS monitor_id,
                   u.nome AS monitor_nome
            FROM monitorias m
            JOIN usuarios u ON u.id = m.aluno_id
            WHERE m.disciplina_id = %s
              AND m.status = 'ATIVO'
            LIMIT 1
            """,
            (disciplina_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def list_monitor_disponibilidade_slots(monitor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT weekday, hora_inicio
            FROM monitor_disponibilidade
            WHERE monitor_id = %s
              AND status = 'LIVRE'
            ORDER BY weekday ASC, hora_inicio ASC
            """,
            (monitor_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_open_votacao(disciplina_id, semana_inicio, semana_fim):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
                        SELECT id,
                                     disciplina_id,
                                     semana_inicio,
                                     semana_fim,
                                     status,
                                     carga_horaria_semanal,
                                     modo_2h
            FROM votacoes
            WHERE disciplina_id = %s
              AND semana_inicio = %s
              AND semana_fim = %s
              AND status = 'ABERTA'
            LIMIT 1
            """,
            (disciplina_id, semana_inicio, semana_fim),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_votacao_by_id(votacao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id,
                   disciplina_id,
                   semana_inicio,
                   semana_fim,
                   status,
                   carga_horaria_semanal,
                   modo_2h
            FROM votacoes
            WHERE id = %s
            """,
            (votacao_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_votacao(disciplina_id, semana_inicio, semana_fim, carga_horaria=1, modo_2h="CONSECUTIVAS"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO votacoes (
                disciplina_id,
                semana_inicio,
                semana_fim,
                status,
                carga_horaria_semanal,
                modo_2h
            )
            VALUES (%s, %s, %s, 'ABERTA', %s, %s)
            """,
            (disciplina_id, semana_inicio, semana_fim, carga_horaria, modo_2h),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_votacao_config(votacao_id, carga_horaria, modo_2h):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE votacoes
            SET carga_horaria_semanal = %s,
                modo_2h = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (carga_horaria, modo_2h, votacao_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def create_votacao_opcoes(votacao_id, opcoes):
    if not opcoes:
        return 0
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO votacao_opcoes (
                votacao_id,
                modo,
                slot1_weekday,
                slot1_hora_inicio,
                slot2_weekday,
                slot2_hora_inicio
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            opcoes,
        )
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def replace_votacao_opcoes(votacao_id, opcoes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM votacao_opcoes
            WHERE votacao_id = %s
            """,
            (votacao_id,),
        )

        if opcoes:
            cursor.executemany(
                """
                INSERT INTO votacao_opcoes (
                    votacao_id,
                    modo,
                    slot1_weekday,
                    slot1_hora_inicio,
                    slot2_weekday,
                    slot2_hora_inicio
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                opcoes,
            )

        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def list_votacao_opcoes(votacao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, modo, slot1_weekday, slot1_hora_inicio, slot2_weekday, slot2_hora_inicio
            FROM votacao_opcoes
            WHERE votacao_id = %s
            ORDER BY modo ASC, slot1_weekday ASC, slot1_hora_inicio ASC
            """,
            (votacao_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_voto_by_aluno(votacao_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT opcao_id
            FROM votos
            WHERE votacao_id = %s AND aluno_id = %s
            """,
            (votacao_id, aluno_id),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def upsert_voto(votacao_id, opcao_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO votos (votacao_id, opcao_id, aluno_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                opcao_id = VALUES(opcao_id),
                criado_em = CURRENT_TIMESTAMP
            """,
            (votacao_id, opcao_id, aluno_id),
        )
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def replace_votos(votacao_id, aluno_id, opcao_ids):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM votos
            WHERE votacao_id = %s AND aluno_id = %s
            """,
            (votacao_id, aluno_id),
        )

        if opcao_ids:
            payload = [(votacao_id, opcao_id, aluno_id) for opcao_id in opcao_ids]
            cursor.executemany(
                """
                INSERT INTO votos (votacao_id, opcao_id, aluno_id)
                VALUES (%s, %s, %s)
                """,
                payload,
            )

        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def list_votacao_resultados(votacao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT o.id AS opcao_id,
                   o.modo,
                   o.slot1_weekday,
                   o.slot1_hora_inicio,
                   o.slot2_weekday,
                   o.slot2_hora_inicio,
                   COUNT(v.id) AS votos
            FROM votacao_opcoes o
            LEFT JOIN votos v ON v.opcao_id = o.id
            WHERE o.votacao_id = %s
            GROUP BY o.id, o.modo, o.slot1_weekday, o.slot1_hora_inicio, o.slot2_weekday, o.slot2_hora_inicio
            ORDER BY votos DESC, o.id ASC
            """,
            (votacao_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def close_votacao(votacao_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE votacoes
            SET status = 'FECHADA', atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (votacao_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def list_sessoes_disciplina_semana(disciplina_id, semana_inicio, semana_fim):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, disciplina_id, monitor_id, data_inicio, data_fim, status
            FROM monitoria_sessoes
            WHERE disciplina_id = %s
              AND data_inicio >= %s
              AND data_inicio <= %s
              AND status = 'AGENDADA'
            ORDER BY data_inicio ASC
            """,
            (disciplina_id, f"{semana_inicio} 00:00:00", f"{semana_fim} 23:59:59"),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_next_sessao_disciplina(disciplina_id, now_value):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, disciplina_id, monitor_id, data_inicio, data_fim, status
            FROM monitoria_sessoes
            WHERE disciplina_id = %s
              AND data_inicio >= %s
              AND status = 'AGENDADA'
            ORDER BY data_inicio ASC
            LIMIT 1
            """,
            (disciplina_id, now_value),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_sessao_by_id(sessao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, disciplina_id, monitor_id, data_inicio, data_fim, status
            FROM monitoria_sessoes
            WHERE id = %s
            """,
            (sessao_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def list_sessoes_monitor(monitor_id, now_value):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT s.id,
                   s.disciplina_id,
                   d.codigo AS disciplina_codigo,
                   d.nome AS disciplina_nome,
                   s.data_inicio,
                   s.data_fim,
                   s.status,
                   s.assunto
            FROM monitoria_sessoes s
            JOIN disciplinas d ON d.id = s.disciplina_id
            WHERE s.monitor_id = %s
              AND s.status IN ('AGENDADA', 'CONCLUIDA')
            ORDER BY s.data_inicio ASC
            """,
            (monitor_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_monitor_hours_count(monitor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COALESCE(
                ROUND(
                    SUM(TIMESTAMPDIFF(MINUTE, s.data_inicio, s.data_fim)) / 60,
                    2
                ),
                0
            ) AS total_horas
            FROM monitoria_sessoes s
            WHERE s.monitor_id = %s
              AND s.status = 'CONCLUIDA'
              AND EXISTS (
                  SELECT 1
                  FROM presencas p
                  WHERE p.sessao_id = s.id
                    AND p.status = 'CONFIRMADA'
              )
            """,
            (monitor_id,),
        )
        row = cursor.fetchone()
        return float(row["total_horas"]) if row and row["total_horas"] is not None else 0.0
    finally:
        cursor.close()
        conn.close()


def list_session_participants(sessao_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.aluno_id,
                   u.nome AS aluno_nome,
                   p.status
            FROM presencas p
            JOIN usuarios u ON u.id = p.aluno_id
            WHERE p.sessao_id = %s
              AND p.status IN ('CONFIRMADA', 'AUSENTE')
            ORDER BY u.nome ASC
            """,
            (sessao_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def save_session_report(sessao_id, assunto):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE monitoria_sessoes
            SET assunto = %s,
                status = 'CONCLUIDA',
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (assunto, sessao_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def create_sessoes(disciplina_id, monitor_id, sessoes):
    if not sessoes:
        return 0
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO monitoria_sessoes (disciplina_id, monitor_id, data_inicio, data_fim, status)
            VALUES (%s, %s, %s, %s, 'AGENDADA')
            """,
            sessoes,
        )
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def cancel_sessao(sessao_id, motivo):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE monitoria_sessoes
            SET status = 'CANCELADA',
                motivo_cancelamento = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
              AND status = 'AGENDADA'
            """,
            (motivo, sessao_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def upsert_presenca(sessao_id, aluno_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO presencas (sessao_id, aluno_id, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (sessao_id, aluno_id, status),
        )
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def get_presenca(sessao_id, aluno_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT status
            FROM presencas
            WHERE sessao_id = %s AND aluno_id = %s
            """,
            (sessao_id, aluno_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def list_presencas_for_aluno(aluno_id, sessao_ids):
    if not sessao_ids:
        return []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ", ".join(["%s"] * len(sessao_ids))
        cursor.execute(
            f"""
            SELECT sessao_id, status
            FROM presencas
            WHERE aluno_id = %s
              AND sessao_id IN ({placeholders})
            """,
            (aluno_id, *sessao_ids),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
