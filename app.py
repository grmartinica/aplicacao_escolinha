from flask import Flask
from aplicacao_escolhinha.config import Config
from aplicacao_escolhinha.extensions import db, login_manager
from aplicacao_escolhinha.routes.auth_routes import auth_bp
from aplicacao_escolhinha.routes.atletas_routes import atletas_bp
from aplicacao_escolhinha.routes.grupos_routes import grupos_bp
from aplicacao_escolhinha.routes.atividades_routes import atividades_bp
from aplicacao_escolhinha.routes.financeiro_routes import financeiro_bp
from aplicacao_escolhinha.routes.dashboard_routes import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(atletas_bp, url_prefix='/atletas')
    app.register_blueprint(grupos_bp, url_prefix='/grupos')
    app.register_blueprint(atividades_bp, url_prefix='/atividades')
    app.register_blueprint(financeiro_bp, url_prefix='/financeiro')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)