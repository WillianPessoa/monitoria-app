from db.connection import get_connection


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, nome, email, senha_hash, papel, status
            FROM usuarios
            WHERE email = %s
            """,
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_user_password(user_id, password_hash, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if status:
            cursor.execute(
                """
                UPDATE usuarios
                SET senha_hash = %s, status = %s, senha_temporaria = FALSE, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (password_hash, status, user_id),
            )
        else:
            cursor.execute(
                """
                UPDATE usuarios
                SET senha_hash = %s, senha_temporaria = FALSE, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (password_hash, user_id),
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def create_password_reset_token(user_id, token, expires_at):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO password_reset_tokens (usuario_id, token, expira_em)
            VALUES (%s, %s, %s)
            """,
            (user_id, token, expires_at),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_valid_password_reset_token(token):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, usuario_id, token, expira_em, usado
            FROM password_reset_tokens
            WHERE token = %s
              AND usado = FALSE
              AND expira_em >= CURRENT_TIMESTAMP
            """,
            (token,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def mark_password_reset_token_used(token_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE password_reset_tokens SET usado = TRUE WHERE id = %s",
            (token_id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
