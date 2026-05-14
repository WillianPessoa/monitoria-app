import getpass
import os

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash


def load_dotenv_if_exists():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_path = os.path.abspath(env_path)
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def main():
    load_dotenv_if_exists()

    nome = input("Nome do admin: ").strip()
    email = input("Email do admin: ").strip().lower()
    senha = getpass.getpass("Senha do admin: ")

    if not nome or not email or len(senha) < 8:
        print("Dados invalidos. Nome/email obrigatorios e senha >= 8 caracteres.")
        return

    mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_database = os.getenv("MYSQL_DATABASE", "monitoria_app")

    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
        )
    except Error as exc:
        print("Falha ao conectar no MySQL.")
        print(
            f"Conexao atual -> host={mysql_host} port={mysql_port} user={mysql_user} db={mysql_database}"
        )
        print(f"Detalhe: {exc}")
        print(
            "Dica: confira MYSQL_PASSWORD no backend/.env e, se estiver usando Docker, "
            "recrie o container com volume limpo para aplicar a senha do docker-sql.yaml."
        )
        return

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        print("Ja existe usuario com esse email.")
        cursor.close()
        conn.close()
        return

    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, 'ADMIN', 'ATIVO', FALSE)
        """,
        (nome, email, generate_password_hash(senha)),
    )
    conn.commit()
    cursor.close()
    conn.close()

    print("Admin criado com sucesso.")


if __name__ == "__main__":
    main()
