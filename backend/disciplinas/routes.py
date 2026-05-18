from flask import render_template

from auth.decorators import login_required
from disciplinas import bp


@bp.get("/")
@login_required
def index():
    return render_template("placeholder.html", section_title="Disciplinas")
