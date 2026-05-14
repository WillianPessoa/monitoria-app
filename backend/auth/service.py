from werkzeug.security import check_password_hash, generate_password_hash

from auth import repository


def authenticate_user(email, password):
    user = repository.get_user_by_email(email)
    if not user:
        return None, "Credenciais invalidas."

    if user["status"] == "INATIVO":
        return None, "Sua conta esta inativa."

    if not check_password_hash(user["senha_hash"], password):
        return None, "Credenciais invalidas."

    return user, None


def change_first_access_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    repository.update_user_password(user_id, password_hash, status="ATIVO")
