from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Voce precisa fazer login.", "error")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped


def require_role(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            role = session.get("papel")
            if role not in allowed_roles:
                flash("Voce nao tem permissao para acessar esta pagina.", "error")
                return redirect(url_for("home"))
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
