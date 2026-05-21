from flask import render_template

from auth.decorators import login_required, require_role
from disciplinas import bp, service


@bp.get("/")
@login_required
@require_role("ADMIN")
def index():
    monitorias = service.list_monitorias_ativas()
    return render_template("disciplinas/index.html", monitorias=monitorias)
