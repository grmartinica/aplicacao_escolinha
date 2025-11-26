from flask import Flask
from config import Config
from extensions import db, login_manager

from routes.auth_routes import auth_bp
from routes.atletas_routes import atletas_bp
from routes.grupos_routes import grupos_bp
from routes.atividades_routes import atividades_bp
from routes.financeiro_routes import financeiro_bp
from routes.dashboard_routes import dashboard_bp
from routes.planos_routes import planos_bp
from routes.ia_routes import ia_bp
from routes.usuarios_sistema_routes import usuarios_bp

import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Pasta de uploads (fotos de atletas, etc.)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(atletas_bp)
    app.register_blueprint(grupos_bp)
    app.register_blueprint(atividades_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(planos_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(usuarios_bp)

    # Cria tabelas (se não existirem)
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
