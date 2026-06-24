import datetime

from agenda import repository
from monitorias import service as monitoria_service
from utils.time import hours_until, now_sp_naive


def get_active_monitoria_for_user(user_id):
    return monitoria_service.get_active_by_aluno(user_id)


def get_slot_info(slot_id):
    return repository.get_slot_with_monitor(slot_id)


def list_available_slots_for_aluno(aluno_id):
    return repository.list_available_slots_for_aluno(aluno_id)


def list_slots_for_monitor(monitor_id):
    return repository.list_slots_for_monitor(monitor_id)


def create_slot(monitor_id, data_inicio, duracao_minutes, local=None):
    monitoria = monitoria_service.get_active_by_aluno(monitor_id)
    if not monitoria:
        return False, "Você não tem monitoria ativa para criar horários."

    if data_inicio <= now_sp_naive():
        return False, "A data e hora devem estar no futuro."

    if duracao_minutes <= 0:
        return False, "Duração inválida."

    data_fim = data_inicio + datetime.timedelta(minutes=duracao_minutes)

    if repository.monitor_has_overlap(monitor_id, data_inicio, data_fim):
        return False, "Já existe um horário que se sobrepõe a este período."

    repository.create_disponibilidade(monitor_id, monitoria["disciplina_id"], data_inicio, data_fim, local)
    return True, None


def book_slot(slot_id, aluno_id):
    slot = repository.get_disponibilidade_by_id(slot_id)
    if not slot or slot["status"] != "DISPONIVEL":
        return False, "Horário indisponível."

    now = now_sp_naive()
    if slot["data_inicio"] <= now:
        return False, "Não é possível agendar horários no passado."

    if repository.student_has_conflict(aluno_id, slot["data_inicio"], slot["data_fim"]):
        return False, "Você já possui um agendamento no mesmo período."

    success, error = repository.reserve_slot(slot_id, aluno_id)
    if not success:
        return False, error or "Falha ao agendar o horário."

    return True, None


def list_weekly_sessions_for_aluno(aluno_id):
    return repository.list_weekly_sessions_for_aluno(aluno_id, now_sp_naive())


def list_past_sessions_for_aluno(aluno_id):
    return repository.list_past_sessions_for_aluno(aluno_id, now_sp_naive())


def list_past_sessions_for_aluno_in_disciplina(aluno_id, disciplina_id):
    return repository.list_past_sessions_for_aluno(aluno_id, now_sp_naive(), disciplina_id)


def list_agendamentos_for_aluno(aluno_id):
    return repository.list_agendamentos_for_aluno(aluno_id, now_sp_naive())


def cancel_agendamento(agendamento_id, aluno_id):
    agendamento = repository.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        return False, "Agendamento não encontrado."
    if agendamento["aluno_id"] != aluno_id:
        return False, "Você não tem permissão para cancelar este agendamento."
    if agendamento["status"] != "CONFIRMADO":
        return False, "Agendamento já cancelado."
    if hours_until(agendamento["data_inicio"], now_sp_naive()) < 6:
        return False, "Cancelamento permitido somente com mais de 6 horas de antecedência."
    if repository.cancel_agendamento_db(agendamento_id):
        return True, None
    return False, "Não foi possível cancelar o agendamento."


def block_slot(slot_id, monitor_id):
    monitoria = monitoria_service.get_active_by_aluno(monitor_id)
    if not monitoria:
        return False, "Você não tem monitoria ativa."
    return repository.block_slot(slot_id, monitor_id)


def unblock_slot(slot_id, monitor_id):
    if repository.unblock_slot(slot_id, monitor_id):
        return True, None
    return False, "Não foi possível desbloquear o horário."
