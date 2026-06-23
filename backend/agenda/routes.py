from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required
from agenda import bp, service
from disciplinas import service as disciplinas_service
from monitorias import service as monitoria_service
from utils.time import now_sp_naive, week_bounds_for_votacao


@bp.get("/")
@login_required
def index():
    user_id = session.get("user_id")
    monitoria = service.get_active_monitoria_for_user(user_id)
    available_slots = service.list_available_slots_for_aluno(user_id)
    weekly_sessions = service.list_weekly_sessions_for_aluno(user_id)
    student_agendamentos = service.list_agendamentos_for_aluno(user_id)
    own_slots = []
    votacao = None
    votacao_resultados = []
    monitor_sessions = []
    session_participants_map = {}
    monitor_hours_total = 0.0
    total_alunos = 0
    required_votes = 0
    votacao_weekdays = []
    votacao_hours = []
    votacao_cells = {}
    votacao_slot_duration = 1
    votacao_max_select = 1
    now_value = now_sp_naive()
    if monitoria:
        own_slots = service.list_slots_for_monitor(user_id)
        monitor_hours_total = monitoria_service.get_monitor_hours_count(user_id)
        semana_inicio, semana_fim = week_bounds_for_votacao(now_value)
        sessoes_semana = monitoria_service.get_weekly_sessions(
            monitoria["disciplina_id"],
            semana_inicio,
            semana_fim,
        )
        sessoes_futuras = [
            sessao for sessao in sessoes_semana if sessao["data_inicio"] >= now_value
        ]
        if not sessoes_futuras:
            votacao = monitoria_service.get_open_or_create_votacao(
                monitoria["disciplina_id"],
                semana_inicio,
                semana_fim,
                user_id,
            )
            if votacao:
                weekly_hours, split_mode = monitoria_service.get_votacao_config(votacao)
                votacao_slot_duration = 2 if weekly_hours == 2 and split_mode == "CONSECUTIVAS" else 1
                votacao_max_select = 1 if weekly_hours == 1 or split_mode == "CONSECUTIVAS" else 2
                votacao_resultados = monitoria_service.list_votacao_resultados(votacao["id"])
                total_alunos = disciplinas_service.count_alunos_disciplina(monitoria["disciplina_id"])
                required_votes = max(1, (total_alunos + 1) // 2)
                for opcao in votacao_resultados:
                    modo = opcao.get("modo")
                    if modo != "SLOT_1H" and modo != "BLOCO_2H":
                        continue

                    if opcao["votos"] <= 0:
                        continue

                    slot1_hour = int(str(opcao["slot1_hora_inicio"]).split(":")[0])
                    slot1_key = (opcao["slot1_weekday"], slot1_hour)
                    current = votacao_cells.get(slot1_key)
                    if not current or opcao["votos"] > current["votos"]:
                        votacao_cells[slot1_key] = {
                            "opcao_id": opcao["opcao_id"],
                            "votos": opcao["votos"],
                        }

                votacao_weekdays = sorted({key[0] for key in votacao_cells.keys()})
                votacao_hours = sorted({key[1] for key in votacao_cells.keys()})

        monitor_sessions = monitoria_service.list_monitor_sessions(user_id, now_value)
        for sessao in monitor_sessions:
            participantes = monitoria_service.list_session_participants(sessao["id"])
            session_participants_map[sessao["id"]] = participantes
    return render_template(
        "agenda/index.html",
        monitoria=monitoria,
        available_slots=available_slots,
        weekly_sessions=weekly_sessions,
        votacao=votacao,
        votacao_resultados=votacao_resultados,
        monitor_sessions=monitor_sessions,
        session_participants_map=session_participants_map,
        monitor_hours_total=monitor_hours_total,
        total_alunos=total_alunos,
        required_votes=required_votes,
        votacao_weekdays=votacao_weekdays,
        votacao_hours=votacao_hours,
        votacao_cells=votacao_cells,
        votacao_slot_duration=votacao_slot_duration,
        votacao_max_select=votacao_max_select,
        own_slots=own_slots,
        now_value=now_value,
        student_agendamentos=student_agendamentos,
    )


@bp.post("/slots/create")
@login_required
def create_slot():
    user_id = session.get("user_id")
    data_inicio_raw = request.form.get("data_inicio", "").strip()
    duracao_raw = request.form.get("duracao", "60").strip()
    local = request.form.get("local", "").strip() or None

    try:
        data_inicio = datetime.fromisoformat(data_inicio_raw)
    except (TypeError, ValueError):
        flash("Data e hora inválidas.", "error")
        return redirect(url_for("agenda.index"))

    try:
        duracao_minutes = int(duracao_raw)
    except (TypeError, ValueError):
        flash("Duração inválida.", "error")
        return redirect(url_for("agenda.index"))

    success, error = service.create_slot(user_id, data_inicio, duracao_minutes, local)
    if success:
        flash("Horário disponível criado com sucesso.", "success")
    else:
        flash(error, "error")
    return redirect(url_for("agenda.index"))


@bp.post("/slots/<int:slot_id>/book")
@login_required
def book_slot(slot_id):
    user_id = session.get("user_id")
    success, error = service.book_slot(slot_id, user_id)
    if success:
        flash("Horário agendado com sucesso.", "success")
    else:
        flash(error, "error")
    return redirect(url_for("agenda.index"))


@bp.post("/agendamentos/<int:agendamento_id>/cancelar")
@login_required
def cancel_agendamento(agendamento_id):
    user_id = session.get("user_id")
    success, error = service.cancel_agendamento(agendamento_id, user_id)
    if success:
        flash("Agendamento cancelado. O horário voltou a estar disponível.", "success")
    else:
        flash(error, "error")
    return redirect(url_for("agenda.index"))


@bp.post("/slots/<int:slot_id>/bloquear")
@login_required
def block_slot(slot_id):
    user_id = session.get("user_id")
    success, error = service.block_slot(slot_id, user_id)
    if success:
        flash("Horário bloqueado.", "success")
    else:
        if error == "INDISPONIVEL":
            flash("Só é possível bloquear horários disponíveis (sem agendamento ativo).", "error")
        else:
            flash(error or "Não foi possível bloquear o horário.", "error")
    return redirect(url_for("agenda.index"))


@bp.post("/slots/<int:slot_id>/desbloquear")
@login_required
def unblock_slot(slot_id):
    user_id = session.get("user_id")
    success, error = service.unblock_slot(slot_id, user_id)
    if success:
        flash("Horário desbloqueado.", "success")
    else:
        flash(error or "Não foi possível desbloquear o horário.", "error")
    return redirect(url_for("agenda.index"))
