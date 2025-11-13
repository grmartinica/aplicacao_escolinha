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
<<<<<<< HEAD

=======
>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

<<<<<<< HEAD
    # Garante que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Extensões
=======
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

<<<<<<< HEAD
    # Blueprints
=======
>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612
    app.register_blueprint(auth_bp)
    app.register_blueprint(atletas_bp)
    app.register_blueprint(grupos_bp)
    app.register_blueprint(atividades_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(dashboard_bp)

    
    with app.app_context():
        db.create_all()

    return app

<<<<<<< HEAD


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
=======
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612
