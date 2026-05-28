from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
from monitorias import service as monitoria_service
from usuarios import bp, repository, service


@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("ADMIN")
def index():
    generated_password = None

    if request.method == "POST":
        nome = request.form.get("nome", "")
        email = request.form.get("email", "")
        papel = request.form.get("papel", "")

        _, generated_password, error = service.create_user(nome, email, papel)
        if error:
            flash(error, "error")
        else:
            flash("Usuário criado com status PENDENTE.", "success")

    users = repository.list_users()
    return render_template(
        "usuarios/index.html",
        users=users,
        generated_password=generated_password,
    )


@bp.post("/<int:user_id>/desativar")
@login_required
@require_role("ADMIN")
def deactivate(user_id):
    if user_id == session.get("user_id"):
        flash("Você não pode desativar o próprio usuário.", "error")
        return redirect(url_for("usuarios.index"))

    if service.deactivate_user(user_id):
        flash("Usuário desativado com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")
    return redirect(url_for("usuarios.index"))


@bp.post("/<int:user_id>/reativar")
@login_required
@require_role("ADMIN")
def reactivate(user_id):
    if service.reactivate_user(user_id):
        flash("Usuário reativado com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")
    return redirect(url_for("usuarios.index"))


@bp.post("/<int:user_id>/resetar-senha")
@login_required
@require_role("ADMIN")
def reset_password(user_id):
    if user_id == session.get("user_id"):
        flash("Você não pode resetar a própria senha por esta tela.", "error")
        return redirect(url_for("usuarios.index"))

    temporary_password = service.reset_user_password(user_id)
    if temporary_password:
        flash(
            f"Senha redefinida. Nova senha temporária: {temporary_password}",
            "success",
        )
    else:
        flash("Usuário não encontrado.", "error")

    return redirect(url_for("usuarios.index"))


@bp.route("/meu-perfil", methods=["GET", "POST"])
@login_required
def my_profile():
    user_id = session.get("user_id")
    user = repository.get_user_by_id(user_id)

    role = session.get("papel")
    is_monitor = role == "MONITOR" or (
        role == "ALUNO" and monitoria_service.has_active_monitoria(user_id)
    )
    if not is_monitor:
        flash("Você não tem permissão para acessar esta página.", "error")
        return redirect(url_for("home"))

    disponibilidade_slots = repository.list_monitor_disponibilidade(user_id)
    selected_keys = set()
    for slot in disponibilidade_slots:
        hora_inicio = slot.get("hora_inicio")
        if hasattr(hora_inicio, "seconds"):
            hour_value = int(hora_inicio.seconds / 3600)
        else:
            hour_value = int(str(hora_inicio).split(":")[0])
        selected_keys.add(f"{slot['weekday']}|{hour_value}")

    if request.method == "POST":
        contato_tipo = request.form.get("contato_tipo", "").strip()
        contato_valor = request.form.get("contato_valor", "").strip()
        slots_raw = request.form.getlist("slots")

        slots_payload = []
        for raw in slots_raw:
            try:
                weekday_str, hour_str = raw.split("|")
                weekday = int(weekday_str)
                hour = int(hour_str)
            except (ValueError, TypeError):
                continue

            slots_payload.append({"weekday": weekday, "hora_inicio": f"{hour:02d}:00:00"})

        if service.update_monitor_profile(user_id, contato_tipo, contato_valor, slots_payload):
            flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("usuarios.my_profile"))

        flash("Contato inválido. Informe e-mail ou celular BR válido.", "error")

    contato_tipo = ""
    contato_valor = user.get("contato") or ""
    if "@" in contato_valor:
        contato_tipo = "email"
    elif contato_valor:
        contato_tipo = "celular"

    return render_template(
        "usuarios/my_profile.html",
        user=user,
        disponibilidade_slots=disponibilidade_slots,
        selected_keys=selected_keys,
        contato_tipo=contato_tipo,
        contato_valor=contato_valor,
    )
