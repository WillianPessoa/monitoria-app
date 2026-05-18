from flask import Blueprint

bp = Blueprint("registros", __name__, url_prefix="/registros")

from registros import routes  # noqa: E402,F401
