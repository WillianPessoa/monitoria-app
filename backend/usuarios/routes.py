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

    if request.method == "POST":
        contato = request.form.get("contato", "").strip()
        disponibilidade = request.form.get("disponibilidade", "").strip()

        if service.update_monitor_profile(user_id, contato, disponibilidade):
            flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("usuarios.my_profile"))

        flash("Não foi possível atualizar o perfil.", "error")

    return render_template("usuarios/my_profile.html", user=user)
