from db.connection import get_connection


def list_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nome, email, papel, status, contato, disponibilidade, criado_em
        FROM usuarios
        ORDER BY criado_em DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nome, email, papel, status, contato, disponibilidade
        FROM usuarios
        WHERE id = %s
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, email FROM usuarios WHERE email = %s",
        (email,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_user(nome, email, papel, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, papel, status, senha_hash, senha_temporaria)
        VALUES (%s, %s, %s, 'PENDENTE', %s, TRUE)
        """,
        (nome, email, papel, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def deactivate_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios
        SET status = 'INATIVO', atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (user_id,),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


def reactivate_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios
        SET status = 'ATIVO', atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (user_id,),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


def reset_user_password(user_id, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios
        SET senha_hash = %s,
            status = 'PENDENTE',
            senha_temporaria = TRUE,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (password_hash, user_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


def update_monitor_profile(user_id, contato, disponibilidade):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE usuarios
        SET contato = %s,
            disponibilidade = %s,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = %s
          AND papel IN ('MONITOR', 'ALUNO')
        """,
        (contato, disponibilidade, user_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0


def list_monitor_disponibilidade(monitor_id):
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


def replace_monitor_disponibilidade(monitor_id, slots):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM monitor_disponibilidade
            WHERE monitor_id = %s
            """,
            (monitor_id,),
        )

        if slots:
            cursor.executemany(
                """
                INSERT INTO monitor_disponibilidade (monitor_id, weekday, hora_inicio, status)
                VALUES (%s, %s, %s, 'LIVRE')
                """,
                slots,
            )

        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def list_active_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nome, email
        FROM usuarios
        WHERE papel = 'ALUNO'
          AND status = 'ATIVO'
        ORDER BY nome ASC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_active_students_by_emails(emails):
    if not emails:
        return []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    placeholders = ", ".join(["%s"] * len(emails))
    cursor.execute(
        f"""
        SELECT id, nome, email
        FROM usuarios
        WHERE papel = 'ALUNO'
          AND status = 'ATIVO'
          AND email IN ({placeholders})
        """,
        tuple(emails),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_active_professors():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, nome, email
        FROM usuarios
        WHERE papel = 'PROFESSOR'
          AND status = 'ATIVO'
        ORDER BY nome ASC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
