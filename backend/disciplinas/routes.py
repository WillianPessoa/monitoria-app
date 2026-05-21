from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
from disciplinas import bp, service
from monitorias import service as monitoria_service
from usuarios import repository as usuarios_repository


@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("ADMIN")
def index():
    if request.method == "POST":
        codigo = request.form.get("codigo", "")
        nome = request.form.get("nome", "")
        professor_id_raw = request.form.get("professor_id", "")

        try:
            professor_id = int(professor_id_raw)
        except (TypeError, ValueError):
            professor_id = None

        disciplina_id, error = service.create_disciplina(codigo, nome, professor_id)
        if error:
            flash(error, "error")
        else:
            flash("Disciplina criada com sucesso.", "success")
            return redirect(url_for("disciplinas.index"))

    disciplinas = service.list_disciplinas()
    professores = usuarios_repository.list_active_professors()
    alunos = usuarios_repository.list_active_students()
    monitorias_ativas = monitoria_service.list_active_monitorias()
    disciplinas_admin = service.list_disciplinas_admin()
    return render_template(
        "disciplinas/index.html",
        disciplinas=disciplinas,
        disciplinas_admin=disciplinas_admin,
        professores=professores,
        alunos=alunos,
        monitorias_ativas=monitorias_ativas,
    )


@bp.post("/<int:disciplina_id>/editar")
@login_required
@require_role("ADMIN")
def editar(disciplina_id):
    codigo = request.form.get("codigo", "")
    nome = request.form.get("nome", "")
    professor_id_raw = request.form.get("professor_id", "")
    monitor_id_raw = request.form.get("monitor_id", "")

    try:
        professor_id = int(professor_id_raw)
    except (TypeError, ValueError):
        professor_id = None

    monitor_id = None
    if monitor_id_raw:
        try:
            monitor_id = int(monitor_id_raw)
        except (TypeError, ValueError):
            monitor_id = None

    if not professor_id:
        flash("Professor inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.update_disciplina(disciplina_id, codigo, nome, professor_id, monitor_id)
    if error:
        flash(error, "error")
    else:
        flash("Disciplina atualizada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/desativar")
@login_required
@require_role("ADMIN")
def desativar(disciplina_id):
    error = service.set_disciplina_status(disciplina_id, "INATIVA")
    if error:
        flash(error, "error")
    else:
        flash("Disciplina desativada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/ativar")
@login_required
@require_role("ADMIN")
def ativar(disciplina_id):
    error = service.set_disciplina_status(disciplina_id, "ATIVA")
    if error:
        flash(error, "error")
    else:
        flash("Disciplina reativada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/matricular")
@login_required
@require_role("ADMIN")
def matricular(disciplina_id):
    emails_raw = request.form.get("alunos_emails", "")
    if emails_raw.strip():
        normalized = emails_raw.replace(";", ",").replace("\n", ",")
        emails = [item.strip() for item in normalized.split(",")]
        error, count = service.bulk_add_alunos_to_disciplina(disciplina_id, emails)
        if error:
            flash(error, "error")
        else:
            flash(f"{count} alunos adicionados à disciplina.", "success")
        return redirect(url_for("disciplinas.index"))

    aluno_id_raw = request.form.get("aluno_id", "")
    try:
        aluno_id = int(aluno_id_raw)
    except (TypeError, ValueError):
        aluno_id = None

    if not aluno_id:
        flash("Aluno inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.add_aluno_to_disciplina(disciplina_id, aluno_id)
    if error:
        flash(error, "error")
    else:
        flash("Aluno adicionado à disciplina.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/remover-aluno")
@login_required
@require_role("ADMIN")
def remover_aluno(disciplina_id):
    aluno_ids_raw = request.form.getlist("alunos_ids")
    if aluno_ids_raw:
        try:
            aluno_ids = [int(aluno_id) for aluno_id in aluno_ids_raw]
        except (TypeError, ValueError):
            aluno_ids = []

        if not aluno_ids:
            flash("Alunos inválidos.", "error")
            return redirect(url_for("disciplinas.index"))

        error, removed = service.bulk_remove_alunos_from_disciplina(disciplina_id, aluno_ids)
        if error:
            flash(error, "error")
        else:
            flash(f"{removed} alunos removidos da disciplina.", "success")
        return redirect(url_for("disciplinas.index"))

    aluno_id_raw = request.form.get("aluno_id", "")
    try:
        aluno_id = int(aluno_id_raw)
    except (TypeError, ValueError):
        aluno_id = None

    if not aluno_id:
        flash("Aluno inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.remove_aluno_from_disciplina(disciplina_id, aluno_id)
    if error:
        flash(error, "error")
    else:
        flash("Aluno removido da disciplina.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.get("/<int:disciplina_id>")
@login_required
def detalhe(disciplina_id):
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("home"))

    title = f"Disciplina: {disciplina['codigo']} - {disciplina['nome']}"
    return render_template("placeholder.html", section_title=title)


@bp.get("/<int:disciplina_id>/alunos")
@login_required
def alunos(disciplina_id):
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("disciplinas.index"))

    role = session.get("papel")
    read_only = True
    if role == "ADMIN":
        read_only = False
    elif role == "PROFESSOR":
        if disciplina["professor_id"] != session.get("user_id"):
            flash("Você não tem permissão para acessar esta disciplina.", "error")
            return redirect(url_for("home"))
    else:
        flash("Você não tem permissão para acessar esta disciplina.", "error")
        return redirect(url_for("home"))

    term = request.args.get("q", "").strip()
    alunos, error = service.list_alunos_by_disciplina(disciplina_id, term or None)
    if error:
        flash(error, "error")
        return redirect(url_for("disciplinas.index"))

    return render_template(
        "disciplinas/alunos.html",
        disciplina=disciplina,
        alunos=alunos,
        search_term=term,
        read_only=read_only,
    )


@bp.post("/<int:disciplina_id>/alunos/adicionar")
@login_required
@require_role("ADMIN")
def adicionar_alunos(disciplina_id):
    emails_raw = request.form.get("alunos_emails", "")
    normalized = emails_raw.replace(";", ",").replace("\n", ",")
    emails = [item.strip() for item in normalized.split(",")]

    error, count = service.bulk_add_alunos_to_disciplina(disciplina_id, emails)
    if error:
        flash(error, "error")
    else:
        flash(f"{count} alunos adicionados à disciplina.", "success")
    return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))


@bp.post("/<int:disciplina_id>/alunos/remover")
@login_required
@require_role("ADMIN")
def remover_alunos(disciplina_id):
    aluno_ids_raw = request.form.getlist("alunos_ids")
    try:
        aluno_ids = [int(aluno_id) for aluno_id in aluno_ids_raw]
    except (TypeError, ValueError):
        aluno_ids = []

    if not aluno_ids:
        flash("Selecione ao menos um aluno.", "error")
        return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))

    error, removed = service.bulk_remove_alunos_from_disciplina(disciplina_id, aluno_ids)
    if error:
        flash(error, "error")
    else:
        flash(f"{removed} alunos removidos da disciplina.", "success")
    return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))
