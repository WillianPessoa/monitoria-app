from flask import render_template, flash, redirect, url_for, request, session

from auth.decorators import login_required, require_role
from disciplinas import service as disciplinas_service
from monitorias import bp, service
from disciplinas import service as disciplinas_service
from utils.time import hours_until, now_sp_naive, week_bounds_sp
from usuarios import repository as usuarios_repository


@bp.get("/pendentes")
@login_required
@require_role("ADMIN")
def pendentes():
    monitorias = service.list_pending_monitorias()
    return render_template("monitorias/pending.html", monitorias=monitorias)


@bp.post("/<int:monitoria_id>/aprovar")
@login_required
@require_role("ADMIN")
def aprovar(monitoria_id):
    approved, error = service.approve_monitoria(monitoria_id)
    if approved:
        flash("Indicação aprovada.", "success")
    elif error == "ALUNO_JA_MONITOR":
        flash("Aluno já possui monitoria ativa.", "error")
    else:
        flash("Monitoria não encontrada ou já processada.", "error")
    return redirect(url_for("monitorias.pendentes"))


@bp.post("/<int:monitoria_id>/rejeitar")
@login_required
@require_role("ADMIN")
def rejeitar(monitoria_id):
    motivo = request.form.get("motivo", "").strip()
    if service.reject_monitoria(monitoria_id, motivo):
        flash("Indicação rejeitada.", "success")
    else:
        flash("Monitoria não encontrada ou já processada.", "error")
    return redirect(url_for("monitorias.pendentes"))


@bp.route("/indicar", methods=["GET", "POST"])
@login_required
@require_role("PROFESSOR")
def indicar():
    professor_id = session.get("user_id")
    disciplinas = disciplinas_service.list_by_professor(professor_id)
    alunos = usuarios_repository.list_active_students()
    indicacoes = service.list_by_professor(professor_id)

    if request.method == "POST":
        disciplina_id_raw = request.form.get("disciplina_id", "")
        aluno_id_raw = request.form.get("aluno_id", "")

        try:
            disciplina_id = int(disciplina_id_raw)
        except (TypeError, ValueError):
            disciplina_id = None

        try:
            aluno_id = int(aluno_id_raw)
        except (TypeError, ValueError):
            aluno_id = None

        allowed_disciplinas = {disciplina["id"] for disciplina in disciplinas}
        allowed_alunos = {aluno["id"] for aluno in alunos}

        if not disciplina_id or disciplina_id not in allowed_disciplinas:
            flash("Disciplina inválida.", "error")
        elif not aluno_id or aluno_id not in allowed_alunos:
            flash("Aluno inválido.", "error")
        else:
            service.create_indicacao(disciplina_id, professor_id, aluno_id)
            flash("Indicação enviada para aprovação.", "success")
            return redirect(url_for("monitorias.indicar"))

    return render_template(
        "monitorias/indicar.html",
        disciplinas=disciplinas,
        alunos=alunos,
        indicacoes=indicacoes,
    )


@bp.post("/votacao/<int:votacao_id>/confirmar")
@login_required
def confirmar_votacao(votacao_id):
    user_id = session.get("user_id")
    slots_raw = request.form.getlist("monitor_slots")
    slots = []
    for raw in slots_raw:
        try:
            weekday_str, hour_str = raw.split("|")
            slots.append((int(weekday_str), int(hour_str)))
        except (TypeError, ValueError):
            continue

    votacao = service.get_votacao_by_id(votacao_id)
    if not votacao or votacao["status"] != "ABERTA":
        flash("Votação inválida.", "error")
        return redirect(url_for("agenda.index"))

    monitor = service.get_active_monitor_for_disciplina(votacao["disciplina_id"])
    if not monitor or monitor["monitor_id"] != user_id:
        flash("Você não tem permissão para confirmar esta votação.", "error")
        return redirect(url_for("agenda.index"))

    total_alunos = disciplinas_service.count_alunos_disciplina(votacao["disciplina_id"])
    required_votes = max(1, (total_alunos + 1) // 2)

    if not slots:
        flash("Selecione uma ou duas opções de horário.", "error")
        return redirect(url_for("agenda.index"))

    if len(slots) > 2:
        flash("Selecione no máximo duas opções de horário.", "error")
        return redirect(url_for("agenda.index"))

    success, error = service.confirm_votacao_slots(
        votacao_id,
        votacao["disciplina_id"],
        user_id,
        votacao["semana_inicio"],
        slots,
        required_votes,
    )
    if success:
        flash("Monitoria confirmada para a semana.", "success")
    else:
        if error == "VOTOS_INSUFICIENTES":
            flash("Confirmação disponível somente após 50% dos alunos votarem.", "error")
        elif error == "OPCAO_INVALIDA":
            flash("Seleção inválida. Escolha horários válidos na grade.", "error")
        else:
            flash("Não foi possível confirmar a votação.", "error")
    return redirect(url_for("agenda.index"))


@bp.post("/sessoes/<int:sessao_id>/cancelar")
@login_required
def cancelar_sessao(sessao_id):
    user_id = session.get("user_id")
    sessao = service.get_session_by_id(sessao_id)
    if not sessao:
        flash("Sessão não encontrada.", "error")
        return redirect(url_for("agenda.index"))

    if sessao["monitor_id"] != user_id:
        flash("Você não tem permissão para cancelar esta sessão.", "error")
        return redirect(url_for("agenda.index"))

    if hours_until(sessao["data_inicio"], now_sp_naive()) <= 6:
        flash("Cancelamento permitido somente com mais de 6 horas de antecedência.", "error")
        return redirect(url_for("agenda.index"))

    if service.cancel_session(sessao_id, "Cancelado pelo monitor."):
        semana_inicio, semana_fim = week_bounds_sp(sessao["data_inicio"])
        service.get_open_or_create_votacao(
            sessao["disciplina_id"],
            semana_inicio,
            semana_fim,
            user_id,
        )
        flash("Sessão cancelada e nova votação aberta.", "success")
    else:
        flash("Não foi possível cancelar a sessão.", "error")
    return redirect(url_for("agenda.index"))
