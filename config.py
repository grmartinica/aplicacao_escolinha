import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "alguma-coisa-bem-secreta")

    DB_USER = os.getenv("mysqluser", "root")
    DB_PASSWORD = os.getenv("mysqlpassword")
    DB_HOST = os.getenv("mysqlhost", "mysql.railway.internal")
    DB_PORT = os.getenv("mysqlport", "3306")
    DB_NAME = os.getenv("mysqldatabase", "railway")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # UPLOAD_FOLDER tem que existir no app.py
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads", "atletas")
