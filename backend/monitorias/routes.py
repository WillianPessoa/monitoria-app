from flask import render_template, flash, redirect, url_for, request, session

from auth.decorators import login_required, require_role
from disciplinas import service as disciplinas_service
from monitorias import bp, service
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
