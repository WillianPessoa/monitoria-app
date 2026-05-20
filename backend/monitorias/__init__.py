from flask import Blueprint

bp = Blueprint("monitorias", __name__, url_prefix="/monitorias")

from monitorias import routes  # noqa: E402,F401
