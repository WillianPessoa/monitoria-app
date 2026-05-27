from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required
from agenda import bp, service


@bp.get("/")
@login_required
def index():
    user_id = session.get("user_id")
    monitoria = service.get_active_monitoria_for_user(user_id)
    available_slots = service.list_available_slots_for_aluno(user_id)
    own_slots = []
    if monitoria:
        own_slots = service.list_slots_for_monitor(user_id)
    return render_template(
        "agenda/index.html",
        monitoria=monitoria,
        available_slots=available_slots,
        own_slots=own_slots,
    )


@bp.post("/slots/create")
@login_required
def create_slot():
    user_id = session.get("user_id")
    data_inicio_raw = request.form.get("data_inicio", "").strip()
    duracao_raw = request.form.get("duracao", "60").strip()

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

    success, error = service.create_slot(user_id, data_inicio, duracao_minutes)
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
