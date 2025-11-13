from app import create_app
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1) Pedro (ADMIN)
    pedro = Usuario.query.filter_by(email="pedrohenrique0806@gmail.com").first()
    if pedro:
        pedro.senha_hash = generate_password_hash("Phlgbabi@10")
        print("Senha atualizada: Pedro (ADMIN)")
    else:
        print("Usuario Pedro não encontrado.")

    # 2) Professores
    prof1 = Usuario.query.filter_by(email="professor1@escolinha.com").first()
    if prof1:
        prof1.senha_hash = generate_password_hash("senha123")
        print("Senha atualizada: professor1")

    prof2 = Usuario.query.filter_by(email="professor2@escolinha.com").first()
    if prof2:
        prof2.senha_hash = generate_password_hash("senha123")
        print("Senha atualizada: professor2")

    # 3) Responsáveis (todos com a mesma senha de teste)
    responsaveis_emails = [
        "resp1@familia.com",
        "resp2@familia.com",
        "resp3@familia.com",
        "resp4@familia.com",
        "resp5@familia.com",
    ]

    for email in responsaveis_emails:
        u = Usuario.query.filter_by(email=email).first()
        if u:
            u.senha_hash = generate_password_hash("responsavel123")
            print(f"Senha atualizada: {email}")

    db.session.commit()
    print("Todas as senhas foram atualizadas com sucesso.")