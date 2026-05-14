import secrets
import string

from werkzeug.security import generate_password_hash

from usuarios import repository

VALID_ROLES = {"ALUNO", "MONITOR", "PROFESSOR", "ADMIN"}


def create_user(nome, email, papel):
    role = (papel or "").upper()
    normalized_email = (email or "").strip().lower()

    if role not in VALID_ROLES:
        return None, None, "Papel invalido."

    if not nome or not normalized_email:
        return None, None, "Nome e email sao obrigatorios."

    if repository.get_user_by_email(normalized_email):
        return None, None, "Email ja cadastrado"

    temporary_password = _generate_temp_password()
    password_hash = generate_password_hash(temporary_password)
    user_id = repository.create_user(nome.strip(), normalized_email, role, password_hash)
    return user_id, temporary_password, None


def deactivate_user(user_id):
    return repository.deactivate_user(user_id)


def reset_user_password(user_id):
    temporary_password = _generate_temp_password()
    password_hash = generate_password_hash(temporary_password)
    if not repository.reset_user_password(user_id, password_hash):
        return None
    return temporary_password


def update_monitor_profile(user_id, contato, disponibilidade):
    return repository.update_monitor_profile(user_id, contato, disponibilidade)


def _generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
