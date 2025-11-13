import os
import os.path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Chave de sessão
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Caminho para uploads de atletas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "atletas")

    # Flask-SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- DADOS DO BANCO (VINDOS DO RAILWAY) ----
    # Railway normalmente cria essas variáveis em minúsculo
    DB_USER = os.getenv("mysqluser") or os.getenv("MYSQLUSER") or "root"
    DB_PASSWORD = os.getenv("mysqlpassword") or os.getenv("MYSQLPASSWORD") or ""
    DB_HOST = os.getenv("mysqlhost") or os.getenv("MYSQLHOST") or "mysql.railway.internal"
    DB_PORT = os.getenv("mysqlport") or os.getenv("MYSQLPORT") or "3306"
    DB_NAME = (
        os.getenv("mysqldatabase")
        or os.getenv("mysql_database")
        or os.getenv("MYSQLDATABASE")
        or "railway"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Logzinho para conferência no Railway (sem senha)
    print(
        ">> SQLALCHEMY_DATABASE_URI (sem senha): "
        f"mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )