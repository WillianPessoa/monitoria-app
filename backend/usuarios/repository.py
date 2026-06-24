from db.connection import get_connection


def list_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id,
                   nome,
                   email,
                   papel,
                   status,
                   contato,
                   disponibilidade,
                   carga_horaria_semanal,
                   modo_2h,
                   criado_em
            FROM usuarios
            ORDER BY criado_em DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
             SELECT id,
                 nome,
                 email,
                 papel,
                 status,
                 contato,
                 disponibilidade,
                 carga_horaria_semanal,
                 modo_2h
            FROM usuarios
            WHERE id = %s
            """,
            (user_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, email FROM usuarios WHERE email = %s",
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_user(nome, email, papel, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, papel, status, senha_hash, senha_temporaria)
            VALUES (%s, %s, %s, 'PENDENTE', %s, TRUE)
            """,
            (nome, email, papel, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def deactivate_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def reactivate_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def reset_user_password(user_id, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
        return affected > 0
    finally:
        cursor.close()
        conn.close()


def update_monitor_profile(user_id, contato, carga_horaria, modo_2h):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE usuarios
            SET contato = %s,
                carga_horaria_semanal = %s,
                modo_2h = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
              AND papel IN ('MONITOR', 'ALUNO')
            """,
            (contato, carga_horaria, modo_2h, user_id),
        )
        conn.commit()
        # Não usa rowcount > 0 porque MySQL reporta rowcount = 0 quando
        # os valores enviados são idênticos aos já armazenados.
        return True
    finally:
        cursor.close()
        conn.close()


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


def get_monitor_preferences(monitor_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT carga_horaria_semanal, modo_2h
            FROM usuarios
            WHERE id = %s
            """,
            (monitor_id,),
        )
        return cursor.fetchone()
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
    try:
        cursor.execute(
            """
            SELECT id, nome, email
            FROM usuarios
            WHERE papel = 'ALUNO'
              AND status = 'ATIVO'
            ORDER BY nome ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_active_students_by_emails(emails):
    if not emails:
        return []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
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
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def list_active_professors():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, nome, email
            FROM usuarios
            WHERE papel = 'PROFESSOR'
              AND status = 'ATIVO'
            ORDER BY nome ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
