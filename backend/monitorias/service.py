from datetime import datetime, time, timedelta

from monitorias import repository
from utils.time import add_hours, combine_date_time


def list_pending_monitorias():
    return repository.list_pending_monitorias()


def approve_monitoria(monitoria_id):
    return repository.approve_monitoria(monitoria_id)


def reject_monitoria(monitoria_id, motivo=None):
    return repository.reject_monitoria(monitoria_id, motivo)


def list_active_monitorias():
    return repository.list_active_monitorias()


def create_indicacao(disciplina_id, professor_id, aluno_id):
    return repository.create_indicacao(disciplina_id, professor_id, aluno_id)


def has_active_monitoria(aluno_id):
    return repository.has_active_monitoria(aluno_id)


def list_by_professor(professor_id):
    return repository.list_by_professor(professor_id)


def get_active_by_aluno(aluno_id):
    return repository.get_active_by_aluno(aluno_id)


def deactivate_monitorias_by_disciplina(disciplina_id, motivo):
    return repository.deactivate_monitorias_by_disciplina(disciplina_id, motivo)


def deactivate_monitoria(disciplina_id, aluno_id, motivo):
    return repository.deactivate_monitoria(disciplina_id, aluno_id, motivo)


def set_monitor_for_disciplina(disciplina_id, professor_id, aluno_id):
    return repository.set_monitor_for_disciplina(disciplina_id, professor_id, aluno_id)


def get_active_monitor_for_disciplina(disciplina_id):
    return repository.get_active_monitor_for_disciplina(disciplina_id)


def get_weekly_sessions(disciplina_id, semana_inicio, semana_fim):
    return repository.list_sessoes_disciplina_semana(disciplina_id, semana_inicio, semana_fim)


def get_next_session(disciplina_id, now_value):
    return repository.get_next_sessao_disciplina(disciplina_id, now_value)


def get_session_by_id(sessao_id):
    return repository.get_sessao_by_id(sessao_id)


def get_open_or_create_votacao(disciplina_id, semana_inicio, semana_fim, monitor_id):
    votacao = repository.get_open_votacao(disciplina_id, semana_inicio, semana_fim)
    if votacao:
        if monitor_id:
            existing_opcoes = repository.list_votacao_opcoes(votacao["id"])
            if not existing_opcoes:
                opcoes = _build_votacao_opcoes(monitor_id)
                if opcoes:
                    payload = [(votacao["id"], *opcao) for opcao in opcoes]
                    repository.replace_votacao_opcoes(votacao["id"], payload)
        return votacao

    if not monitor_id:
        return None

    votacao_id = repository.create_votacao(disciplina_id, semana_inicio, semana_fim)
    opcoes = _build_votacao_opcoes(monitor_id)
    payload = [(votacao_id, *opcao) for opcao in opcoes]
    repository.create_votacao_opcoes(votacao_id, payload)
    return {"id": votacao_id, "disciplina_id": disciplina_id}


def list_votacao_opcoes(votacao_id):
    return repository.list_votacao_opcoes(votacao_id)


def get_open_votacao(disciplina_id, semana_inicio, semana_fim):
    return repository.get_open_votacao(disciplina_id, semana_inicio, semana_fim)


def get_votacao_by_id(votacao_id):
    return repository.get_votacao_by_id(votacao_id)


def get_voto_by_aluno(votacao_id, aluno_id):
    return repository.get_voto_by_aluno(votacao_id, aluno_id)


def cast_vote(votacao_id, opcao_ids, aluno_id):
    return repository.replace_votos(votacao_id, aluno_id, opcao_ids)


def list_votacao_resultados(votacao_id):
    return repository.list_votacao_resultados(votacao_id)


def confirm_votacao(votacao_id, opcao_id, disciplina_id, monitor_id, semana_inicio):
    opcoes = repository.list_votacao_opcoes(votacao_id)
    opcao = next((item for item in opcoes if item["id"] == opcao_id), None)
    if not opcao:
        return False

    sessoes = _build_sessoes_from_opcao(disciplina_id, monitor_id, opcao, semana_inicio)
    repository.create_sessoes(disciplina_id, monitor_id, sessoes)
    repository.close_votacao(votacao_id)
    return True


def confirm_votacao_slots(votacao_id, disciplina_id, monitor_id, semana_inicio, slots, required_votes):
    resultados = repository.list_votacao_resultados(votacao_id)
    votos_map = {}
    for opcao in resultados:
        slot1_hour = int(str(opcao["slot1_hora_inicio"]).split(":")[0])
        key1 = (opcao["slot1_weekday"], slot1_hour)
        votos_map[key1] = max(votos_map.get(key1, 0), opcao["votos"])
        if opcao.get("slot2_weekday") and opcao.get("slot2_hora_inicio"):
            slot2_hour = int(str(opcao["slot2_hora_inicio"]).split(":")[0])
            key2 = (opcao["slot2_weekday"], slot2_hour)
            votos_map[key2] = max(votos_map.get(key2, 0), opcao["votos"])

    if not slots:
        return False, "OPCAO_INVALIDA"

    if len(slots) == 1:
        weekday, hour = slots[0]
        next_key = (weekday, hour + 1)
        if (weekday, hour) not in votos_map or next_key not in votos_map:
            return False, "OPCAO_INVALIDA"
        if votos_map[(weekday, hour)] < required_votes or votos_map[next_key] < required_votes:
            return False, "VOTOS_INSUFICIENTES"

        slot_date = semana_inicio + timedelta(days=weekday - 1)
        start_dt = combine_date_time(slot_date, time(hour=hour))
        sessoes = [(disciplina_id, monitor_id, start_dt, add_hours(start_dt, 2))]
    elif len(slots) == 2:
        slots_sorted = sorted(slots)
        for weekday, hour in slots_sorted:
            if (weekday, hour) not in votos_map:
                return False, "OPCAO_INVALIDA"
            if votos_map[(weekday, hour)] < required_votes:
                return False, "VOTOS_INSUFICIENTES"

        (w1, h1), (w2, h2) = slots_sorted
        if w1 == w2 and h2 - h1 == 1:
            slot_date = semana_inicio + timedelta(days=w1 - 1)
            start_dt = combine_date_time(slot_date, time(hour=h1))
            sessoes = [(disciplina_id, monitor_id, start_dt, add_hours(start_dt, 2))]
        else:
            sessoes = []
            for weekday, hour in slots_sorted:
                slot_date = semana_inicio + timedelta(days=weekday - 1)
                start_dt = combine_date_time(slot_date, time(hour=hour))
                sessoes.append((disciplina_id, monitor_id, start_dt, add_hours(start_dt, 1)))
    else:
        return False, "OPCAO_INVALIDA"

    repository.create_sessoes(disciplina_id, monitor_id, sessoes)
    repository.close_votacao(votacao_id)
    return True, None


def list_monitor_sessions(monitor_id, now_value):
    return repository.list_sessoes_monitor(monitor_id, now_value)


def cancel_session(sessao_id, motivo):
    return repository.cancel_sessao(sessao_id, motivo)


def set_presenca(sessao_id, aluno_id, status):
    return repository.upsert_presenca(sessao_id, aluno_id, status)


def get_presenca(sessao_id, aluno_id):
    return repository.get_presenca(sessao_id, aluno_id)


def list_presencas_for_aluno(aluno_id, sessao_ids):
    return repository.list_presencas_for_aluno(aluno_id, sessao_ids)


def _build_votacao_opcoes(monitor_id):
    disponibilidade = repository.list_monitor_disponibilidade_slots(monitor_id)
    by_weekday = {}
    for slot in disponibilidade:
        weekday = slot["weekday"]
        hora_inicio = _time_to_str(slot["hora_inicio"])
        by_weekday.setdefault(weekday, []).append(hora_inicio)

    opcoes = []

    # 2h consecutivas
    for weekday, horas in by_weekday.items():
        sorted_horas = sorted(horas)
        for idx in range(len(sorted_horas) - 1):
            h1 = sorted_horas[idx]
            h2 = sorted_horas[idx + 1]
            if _hora_is_consecutive(h1, h2):
                opcoes.append(("BLOCO_2H", weekday, h1, None, None))

    # dois dias diferentes (1h cada)
    weekdays = sorted(by_weekday.keys())
    for i, day_a in enumerate(weekdays):
        for day_b in weekdays[i + 1:]:
            for hora_a in by_weekday[day_a]:
                for hora_b in by_weekday[day_b]:
                    opcoes.append(("DOIS_1H", day_a, hora_a, day_b, hora_b))

    return opcoes


def _build_sessoes_from_opcao(disciplina_id, monitor_id, opcao, semana_inicio):
    sessoes = []
    slot1_date = semana_inicio + timedelta(days=opcao["slot1_weekday"] - 1)
    slot1_dt = combine_date_time(slot1_date, _parse_time(opcao["slot1_hora_inicio"]))
    if opcao["modo"] == "BLOCO_2H":
        sessoes.append((disciplina_id, monitor_id, slot1_dt, add_hours(slot1_dt, 2)))
    else:
        slot2_date = semana_inicio + timedelta(days=opcao["slot2_weekday"] - 1)
        slot2_dt = combine_date_time(slot2_date, _parse_time(opcao["slot2_hora_inicio"]))
        sessoes.append((disciplina_id, monitor_id, slot1_dt, add_hours(slot1_dt, 1)))
        sessoes.append((disciplina_id, monitor_id, slot2_dt, add_hours(slot2_dt, 1)))
    return sessoes


def _hora_is_consecutive(h1, h2):
    h1_hour = _time_to_hour(h1)
    h2_hour = _time_to_hour(h2)
    return h2_hour - h1_hour == 1


def _time_to_hour(value):
    if hasattr(value, "seconds"):
        return int(value.seconds / 3600)
    return int(str(value).split(":")[0])


def _time_to_str(value):
    if hasattr(value, "seconds"):
        hour = int(value.seconds / 3600)
        return f"{hour:02d}:00:00"
    parts = str(value).split(":")
    return f"{int(parts[0]):02d}:{int(parts[1]):02d}:00"


def _parse_time(value):
    if hasattr(value, "hour"):
        return value
    parts = str(value).split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))
