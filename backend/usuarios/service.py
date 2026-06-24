import re
import secrets
import string

from werkzeug.security import generate_password_hash

from monitorias import service as monitoria_service
from utils.time import now_sp_naive, week_bounds_for_votacao

from usuarios import repository

VALID_ROLES = {"ALUNO", "PROFESSOR", "ADMIN"}


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


def reactivate_user(user_id):
    return repository.reactivate_user(user_id)


def update_monitor_profile(
    user_id,
    contato_tipo,
    contato_valor,
    disponibilidade_slots,
    carga_horaria,
    modo_2h,
):
    normalized_tipo = (contato_tipo or "").strip().lower()
    normalized_valor = (contato_valor or "").strip()

    if normalized_valor:
        if normalized_tipo == "email":
            if not _is_valid_email(normalized_valor):
                return False, "E-mail inválido. Verifique o endereço informado."
        elif normalized_tipo == "celular":
            if not _is_valid_br_phone(normalized_valor):
                return False, "Celular inválido. Use o formato (XX) XXXXX-XXXX."
        else:
            return False, "Tipo de contato inválido."

    if carga_horaria not in {1, 2}:
        carga_horaria = 1
    if modo_2h not in {"CONSECUTIVAS", "SEPARADAS"}:
        modo_2h = "CONSECUTIVAS"
    if carga_horaria == 1:
        modo_2h = "CONSECUTIVAS"

    if not repository.update_monitor_profile(
        user_id,
        normalized_valor or None,
        carga_horaria,
        modo_2h,
    ):
        return False, "Não foi possível salvar o perfil."

    slots_payload = []
    for slot in disponibilidade_slots or []:
        slots_payload.append((user_id, slot["weekday"], slot["hora_inicio"]))

    repository.replace_monitor_disponibilidade(user_id, slots_payload)

    monitoria = monitoria_service.get_active_by_aluno(user_id)
    if monitoria:
        now_value = now_sp_naive()
        semana_inicio, semana_fim = week_bounds_for_votacao(now_value)
        votacao = monitoria_service.get_open_votacao(
            monitoria["disciplina_id"],
            semana_inicio,
            semana_fim,
        )
        if votacao:
            monitoria_service.update_votacao_config(
                votacao["id"],
                carga_horaria,
                modo_2h,
            )
        monitoria_service.sync_open_votacao_opcoes_for_monitor(
            monitoria["disciplina_id"],
            user_id,
            semana_inicio,
            semana_fim,
        )
    return True, None


def _generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _is_valid_email(value):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value) is not None


def _is_valid_br_phone(value):
    return re.match(r"^\(\d{2}\) \d{5}-\d{4}$", value) is not None
