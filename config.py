import os
import os.path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Chave de sessão
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Pasta de uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "atletas")

    # Flask-SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==== DADOS DO BANCO ====
    # 1º tenta as variáveis DB_* (as que você tem na tela do Railway)
    # 2º tenta as mysql* adicionadas automaticamente pelo serviço de banco
    DB_USER = (
        os.getenv("DB_USER")
        or os.getenv("mysqluser")
        or os.getenv("MYSQLUSER")
        or "root"
    )

    DB_PASSWORD = (
        os.getenv("DB_PASSWORD")
        or os.getenv("mysqlpassword")
        or os.getenv("MYSQLPASSWORD")
        or os.getenv("mysql_root_password")
        or os.getenv("MYSQL_ROOT_PASSWORD")
        or ""
    )

    DB_HOST = (
        os.getenv("DB_HOST")
        or os.getenv("mysqlhost")
        or os.getenv("MYSQLHOST")
        or "mysql.railway.internal"
    )

    DB_PORT = (
        os.getenv("DB_PORT")
        or os.getenv("mysqlport")
        or os.getenv("MYSQLPORT")
        or "3306"
    )

    DB_NAME = (
        os.getenv("DB_NAME")
        or os.getenv("mysqldatabase")
        or os.getenv("mysql_database")
        or os.getenv("MYSQLDATABASE")
        or "railway"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Logs pra conferir no Railway (sem expor senha)
    print(
        ">> SQLALCHEMY_DATABASE_URI (sem senha): "
        f"mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    print(f">> DB_PASSWORD está vazio? {DB_PASSWORD == ''}")
