import datetime

from agenda import repository
from monitorias import service as monitoria_service


def get_active_monitoria_for_user(user_id):
    return monitoria_service.get_active_by_aluno(user_id)


def list_available_slots_for_aluno(aluno_id):
    return repository.list_available_slots_for_aluno(aluno_id)


def list_slots_for_monitor(monitor_id):
    return repository.list_slots_for_monitor(monitor_id)


def create_slot(monitor_id, data_inicio, duracao_minutes):
    monitoria = monitoria_service.get_active_by_aluno(monitor_id)
    if not monitoria:
        return False, "Você não tem monitoria ativa para criar horários."

    if data_inicio <= datetime.datetime.now():
        return False, "A data e hora devem estar no futuro."

    if duracao_minutes <= 0:
        return False, "Duração inválida."

    data_fim = data_inicio + datetime.timedelta(minutes=duracao_minutes)
    repository.create_disponibilidade(monitor_id, monitoria["disciplina_id"], data_inicio, data_fim)
    return True, None


def book_slot(slot_id, aluno_id):
    slot = repository.get_disponibilidade_by_id(slot_id)
    if not slot or slot["status"] != "DISPONIVEL":
        return False, "Horário indisponível."

    now = datetime.datetime.now()
    if slot["data_inicio"] <= now:
        return False, "Não é possível agendar horários no passado."

    if repository.student_has_conflict(aluno_id, slot["data_inicio"], slot["data_fim"]):
        return False, "Você já possui um agendamento no mesmo período."

    success, error = repository.reserve_slot(slot_id, aluno_id)
    if not success:
        return False, error or "Falha ao agendar o horário."

    return True, None
