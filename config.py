import os

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "alguma-coisa-bem-secreta")

    DB_USER = os.getenv("mysqluser", "root")
    DB_PASSWORD = os.getenv("mysqlpassword")
    DB_HOST = os.getenv("mysqlhost", "mysql.railway.internal")
    DB_PORT = os.getenv("mysqlport", "3306")
    DB_NAME = os.getenv("mysqldatabase", "railway")

    SECRET_KEY = os.getenv("SECRET_KEY", "chave_super_secreta_escolinha")

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Phlgbabi@10")
    DB_HOST = os.getenv("DB_HOST", "191.36.128.157")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "escolinha")


    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # UPLOAD_FOLDER tem que existir no app.py
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads", "atletas")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "atletas")