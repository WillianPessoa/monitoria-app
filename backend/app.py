from flask import Flask, redirect, render_template, session, url_for
import os

from agenda import bp as agenda_bp
from auth import bp as auth_bp
from config import Config
from db.connection import init_db
from disciplinas import bp as disciplinas_bp
from relatorios import bp as relatorios_bp
from registros import bp as registros_bp
from usuarios import bp as usuarios_bp
from monitorias import bp as monitorias_bp


def create_app():
    # Serve templates and static files from the top-level `frontend/` folder (absolute paths)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    frontend_root = os.path.join(project_root, "frontend")
    template_folder = os.path.join(frontend_root, "templates")
    static_folder = os.path.join(frontend_root, "static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(Config)

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(disciplinas_bp)
    app.register_blueprint(monitorias_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(registros_bp)
    app.register_blueprint(relatorios_bp)

    @app.context_processor
    def inject_current_user():
        user_id = session.get("user_id")
        role = session.get("papel")
        is_monitor = False
        if user_id:
            from monitorias import service as monitoria_service

            is_monitor = role == "MONITOR" or monitoria_service.has_active_monitoria(user_id)
        return {
            "current_user": {
                "id": user_id,
                "nome": session.get("nome"),
                "papel": role,
                "is_monitor": is_monitor,
            }
        }

    @app.get("/")
    def home():
        user_id = session.get("user_id")
        role = session.get("papel")
        if not user_id:
            return redirect(url_for("auth.login"))

        if role == "PROFESSOR":
            from disciplinas import service as disciplinas_service

            professor_disciplinas = disciplinas_service.list_by_professor_with_stats(user_id)
            return render_template(
                "home.html",
                role=role,
                professor_disciplinas=professor_disciplinas,
            )

        if role == "ADMIN":
            return render_template("home.html", role=role)

        from disciplinas import service as disciplinas_service
        from monitorias import service as monitoria_service

        aluno_disciplinas = disciplinas_service.list_disciplinas_by_aluno(user_id)
        monitoria = monitoria_service.get_active_by_aluno(user_id)
        return render_template(
            "home.html",
            role=role,
            aluno_disciplinas=aluno_disciplinas,
            monitoria=monitoria,
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
