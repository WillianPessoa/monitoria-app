from flask import Blueprint

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

from usuarios import routes  # noqa: E402,F401
