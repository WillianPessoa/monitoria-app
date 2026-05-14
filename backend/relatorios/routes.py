from flask import render_template

from auth.decorators import login_required
from relatorios import bp


@bp.get("/")
@login_required
def index():
    return render_template("placeholder.html", section_title="Relatorios")
