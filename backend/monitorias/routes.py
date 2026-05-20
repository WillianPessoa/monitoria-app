from flask import render_template, flash, redirect, url_for, request

from auth.decorators import login_required, require_role
from monitorias import bp, service


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
    if service.approve_monitoria(monitoria_id):
        flash("Indicacao aprovada.", "success")
    else:
        flash("Monitoria nao encontrada ou ja processada.", "error")
    return redirect(url_for("monitorias.pendentes"))


@bp.post("/<int:monitoria_id>/rejeitar")
@login_required
@require_role("ADMIN")
def rejeitar(monitoria_id):
    motivo = request.form.get("motivo", "").strip()
    if service.reject_monitoria(monitoria_id, motivo):
        flash("Indicacao rejeitada.", "success")
    else:
        flash("Monitoria nao encontrada ou ja processada.", "error")
    return redirect(url_for("monitorias.pendentes"))
