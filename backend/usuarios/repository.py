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
          AND papel = 'MONITOR'
        """,
        (contato, disponibilidade, user_id),
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0
