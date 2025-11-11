import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "projetomartinica")

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Phlgbabi@10")
    DB_HOST = os.getenv("DB_HOST", "191.36.128.157")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "escolinha")

    # Escapando os caracteres especiais na senha do banco de dados
    DB_PASSWORD_ENC = quote_plus(DB_PASSWORD)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_ENC}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', "atletas")
