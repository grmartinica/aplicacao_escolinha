from flask import Flask
from config import Config
from extensions import db, login_manager
from routes.auth_routes import auth_bp
from routes.atletas_routes import atletas_bp
from routes.grupos_routes import grupos_bp
from routes.atividades_routes import atividades_bp
from routes.financeiro_routes import financeiro_bp
from routes.dashboard_routes import dashboard_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Manter a pasta de upload 
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

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