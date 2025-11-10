import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
        "mysql+mysqlconnector://root:senha@localhost:3306/aplicacao_escolhinha"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "aplicacao_escolhinha", "static", "uploads")