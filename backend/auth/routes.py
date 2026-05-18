from flask import flash, redirect, render_template, request, session, url_for

from auth import bp, service


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("senha", "")

        user, error = service.authenticate_user(email, password)
        if error:
            flash(error, "error")
            return render_template("auth/login.html")

        if user["status"] == "PENDENTE":
            session.clear()
            session["first_access_user_id"] = user["id"]
            session["first_access_nome"] = user["nome"]
            return redirect(url_for("auth.first_access"))

        session.clear()
        session["user_id"] = user["id"]
        session["nome"] = user["nome"]
        session["papel"] = user["papel"]
        destination = {
            "ADMIN": "usuarios.index",
            "MONITOR": "usuarios.my_profile",
            "PROFESSOR": "home",
            "ALUNO": "home",
        }.get(user["papel"], "home")
        return redirect(url_for(destination))

    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("Sessao encerrada.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/primeiro-acesso", methods=["GET", "POST"])
def first_access():
    user_id = session.get("first_access_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        if len(senha) < 8:
            flash("A nova senha deve ter ao menos 8 caracteres.", "error")
            return render_template("auth/first_access.html")

        if senha != confirmar:
            flash("As senhas nao conferem.", "error")
            return render_template("auth/first_access.html")

        service.change_first_access_password(user_id, senha)
        session.clear()
        flash("Senha definida com sucesso. Faca login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/first_access.html")
