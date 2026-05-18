from flask import Blueprint

bp = Blueprint("disciplinas", __name__, url_prefix="/disciplinas")

from disciplinas import routes  # noqa: E402,F401
