from datetime import datetime, time, timedelta

from monitorias import repository
from usuarios import repository as usuarios_repository
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
            _sync_votacao_opcoes(votacao, monitor_id)
        return votacao

    if not monitor_id:
        return None

    carga_horaria = 1
    modo_2h = "CONSECUTIVAS"
    preferences = usuarios_repository.get_monitor_preferences(monitor_id)
    if preferences:
        carga_horaria = int(preferences.get("carga_horaria_semanal") or 1)
        modo_2h = preferences.get("modo_2h") or "CONSECUTIVAS"

    votacao_id = repository.create_votacao(
        disciplina_id,
        semana_inicio,
        semana_fim,
        carga_horaria,
        modo_2h,
    )
    votacao = repository.get_votacao_by_id(votacao_id)
    _sync_votacao_opcoes(votacao, monitor_id)
    return votacao


def list_votacao_opcoes(votacao_id):
    return repository.list_votacao_opcoes(votacao_id)


def get_open_votacao(disciplina_id, semana_inicio, semana_fim):
    return repository.get_open_votacao(disciplina_id, semana_inicio, semana_fim)


def get_votacao_by_id(votacao_id):
    return repository.get_votacao_by_id(votacao_id)


def get_votacao_config(votacao):
    return _get_votacao_config(votacao)


def update_votacao_config(votacao_id, carga_horaria, modo_2h):
    return repository.update_votacao_config(votacao_id, carga_horaria, modo_2h)


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


def confirm_votacao_slots(
    votacao_id,
    disciplina_id,
    monitor_id,
    semana_inicio,
    slots,
    required_votes,
    weekly_hours,
    split_mode,
):
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

    if weekly_hours == 1:
        if len(slots) != 1:
            return False, "OPCAO_INVALIDA"
        weekday, hour = slots[0]
        if (weekday, hour) not in votos_map:
            return False, "OPCAO_INVALIDA"
        if votos_map[(weekday, hour)] < required_votes:
            return False, "VOTOS_INSUFICIENTES"

        slot_date = semana_inicio + timedelta(days=weekday - 1)
        start_dt = combine_date_time(slot_date, time(hour=hour))
        sessoes = [(disciplina_id, monitor_id, start_dt, add_hours(start_dt, 1))]
    elif split_mode == "CONSECUTIVAS":
        if len(slots) != 1:
            return False, "OPCAO_INVALIDA"
        weekday, hour = slots[0]
        if (weekday, hour) not in votos_map:
            return False, "OPCAO_INVALIDA"
        if votos_map[(weekday, hour)] < required_votes:
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


def sync_open_votacao_opcoes_for_monitor(disciplina_id, monitor_id, semana_inicio, semana_fim):
    votacao = repository.get_open_votacao(disciplina_id, semana_inicio, semana_fim)
    if not votacao:
        return 0
    return _sync_votacao_opcoes(votacao, monitor_id)


def _build_votacao_opcoes(monitor_id, weekly_hours, split_mode):
    disponibilidade = repository.list_monitor_disponibilidade_slots(monitor_id)
    by_weekday = {}
    for slot in disponibilidade:
        weekday = slot["weekday"]
        hora_inicio = _time_to_str(slot["hora_inicio"])
        by_weekday.setdefault(weekday, []).append(hora_inicio)

    opcoes = []

    if weekly_hours == 1 or split_mode == "SEPARADAS":
        for weekday, horas in by_weekday.items():
            for hora in sorted(horas):
                opcoes.append(("SLOT_1H", weekday, hora, None, None))
    else:
        for weekday, horas in by_weekday.items():
            sorted_horas = sorted(horas)
            for idx in range(len(sorted_horas) - 1):
                h1 = sorted_horas[idx]
                h2 = sorted_horas[idx + 1]
                if _hora_is_consecutive(h1, h2):
                    opcoes.append(("BLOCO_2H", weekday, h1, None, None))

    return opcoes


def _build_sessoes_from_opcao(disciplina_id, monitor_id, opcao, semana_inicio):
    sessoes = []
    slot1_date = semana_inicio + timedelta(days=opcao["slot1_weekday"] - 1)
    slot1_dt = combine_date_time(slot1_date, _parse_time(opcao["slot1_hora_inicio"]))
    if opcao["modo"] == "BLOCO_2H":
        sessoes.append((disciplina_id, monitor_id, slot1_dt, add_hours(slot1_dt, 2)))
    elif opcao["modo"] == "SLOT_1H":
        sessoes.append((disciplina_id, monitor_id, slot1_dt, add_hours(slot1_dt, 1)))
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


def _opcao_key(modo, slot1_weekday, slot1_hora_inicio, slot2_weekday, slot2_hora_inicio):
    slot1 = _time_to_str(slot1_hora_inicio) if slot1_hora_inicio else None
    slot2 = _time_to_str(slot2_hora_inicio) if slot2_hora_inicio else None
    return (modo, slot1_weekday, slot1, slot2_weekday, slot2)


def _get_votacao_config(votacao):
    weekly_hours = int(votacao.get("carga_horaria_semanal") or 1)
    split_mode = votacao.get("modo_2h") or "CONSECUTIVAS"
    if split_mode not in {"CONSECUTIVAS", "SEPARADAS"}:
        split_mode = "CONSECUTIVAS"
    return weekly_hours, split_mode


def _sync_votacao_opcoes(votacao, monitor_id):
    weekly_hours, split_mode = _get_votacao_config(votacao)
    opcoes = _build_votacao_opcoes(monitor_id, weekly_hours, split_mode)
    if not opcoes:
        return 0

    existentes = repository.list_votacao_opcoes(votacao["id"])
    existentes_keys = {
        _opcao_key(
            item["modo"],
            item["slot1_weekday"],
            item["slot1_hora_inicio"],
            item.get("slot2_weekday"),
            item.get("slot2_hora_inicio"),
        )
        for item in existentes
    }

    novos = []
    for modo, slot1_weekday, slot1_hora_inicio, slot2_weekday, slot2_hora_inicio in opcoes:
        key = _opcao_key(modo, slot1_weekday, slot1_hora_inicio, slot2_weekday, slot2_hora_inicio)
        if key in existentes_keys:
            continue
        novos.append(
            (
                votacao["id"],
                modo,
                slot1_weekday,
                slot1_hora_inicio,
                slot2_weekday,
                slot2_hora_inicio,
            )
        )

    if not novos:
        return 0

    repository.create_votacao_opcoes(votacao["id"], novos)
    return len(novos)
