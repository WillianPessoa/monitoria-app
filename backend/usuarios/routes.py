from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
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
            flash("Usuario criado com status PENDENTE.", "success")

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
        flash("Voce nao pode desativar o proprio usuario.", "error")
        return redirect(url_for("usuarios.index"))

    if service.deactivate_user(user_id):
        flash("Usuario desativado com sucesso.", "success")
    else:
        flash("Usuario nao encontrado.", "error")
    return redirect(url_for("usuarios.index"))


@bp.post("/<int:user_id>/resetar-senha")
@login_required
@require_role("ADMIN")
def reset_password(user_id):
    if user_id == session.get("user_id"):
        flash("Voce nao pode resetar a propria senha por esta tela.", "error")
        return redirect(url_for("usuarios.index"))

    temporary_password = service.reset_user_password(user_id)
    if temporary_password:
        flash(
            f"Senha redefinida. Nova senha temporaria: {temporary_password}",
            "success",
        )
    else:
        flash("Usuario nao encontrado.", "error")

    return redirect(url_for("usuarios.index"))


@bp.route("/meu-perfil", methods=["GET", "POST"])
@login_required
@require_role("MONITOR")
def my_profile():
    user_id = session.get("user_id")
    user = repository.get_user_by_id(user_id)

    if request.method == "POST":
        contato = request.form.get("contato", "").strip()
        disponibilidade = request.form.get("disponibilidade", "").strip()

        if service.update_monitor_profile(user_id, contato, disponibilidade):
            flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("usuarios.my_profile"))

        flash("Nao foi possivel atualizar o perfil.", "error")

    return render_template("usuarios/my_profile.html", user=user)
