from flask import Blueprint

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

from relatorios import routes  # noqa: E402,F401
