from flask import Flask, render_template, session
import os

from agenda import bp as agenda_bp
from auth import bp as auth_bp
from config import Config
from db.connection import init_db
from disciplinas import bp as disciplinas_bp
from relatorios import bp as relatorios_bp
from registros import bp as registros_bp
from usuarios import bp as usuarios_bp


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
    app.register_blueprint(agenda_bp)
    app.register_blueprint(registros_bp)
    app.register_blueprint(relatorios_bp)

    @app.context_processor
    def inject_current_user():
        return {
            "current_user": {
                "id": session.get("user_id"),
                "nome": session.get("nome"),
                "papel": session.get("papel"),
            }
        }

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
