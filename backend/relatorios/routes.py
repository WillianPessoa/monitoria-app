from flask import render_template, request

from auth.decorators import login_required, require_role
from disciplinas import repository as disciplinas_repository
from relatorios import bp, service


@bp.get("/")
@login_required
@require_role("ADMIN")
def index():
    disciplina_id_raw = request.args.get("disciplina_id", "")
    disciplina_id = None
    if disciplina_id_raw:
        try:
            disciplina_id = int(disciplina_id_raw)
        except (TypeError, ValueError):
            disciplina_id = None

    painel = service.get_painel_horas(disciplina_id)
    disciplinas = disciplinas_repository.list_disciplinas()

    return render_template(
        "relatorios/horas.html",
        painel=painel,
        disciplinas=disciplinas,
        filtro_disciplina_id=disciplina_id,
    )
