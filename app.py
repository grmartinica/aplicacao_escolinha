from flask import Flask
from config import Config
from extensions import db, login_manager

from routes.auth_routes import auth_bp
from routes.atletas_routes import atletas_bp
from routes.grupos_routes import grupos_bp
from routes.atividades_routes import atividades_bp
from routes.financeiro_routes import financeiro_bp
from routes.dashboard_routes import dashboard_bp
from routes.planos_routes import planos_bp
from routes.ia_routes import ia_bp
from routes.usuarios_sistema_routes import usuarios_bp

import os

from werkzeug.security import generate_password_hash
from datetime import date
from models import Usuario, Responsavel, Atleta, AtletaResponsavel, Grupo, Plano, AtletaPlano


def seed_default_data():
    """
    Cria usuários, responsáveis, atletas, grupos e planos padrão
    SOMENTE se o banco estiver vazio (sem nenhum usuário).
    """
    if Usuario.query.first():
        # já tem dado, não faz nada
        print(">> Seed: já existem usuários, não vou recriar os dados padrão.")
        return

    print(">> Seed: criando dados iniciais...")

    # =========================
    # Usuários do sistema
    # =========================
    senha_admin_hash = generate_password_hash("Phlgbabi@10")

    super_admin = Usuario(
        nome="Pedro Santos",
        email="pedro_santos@auroratech.com",
        senha_hash=senha_admin_hash,
        telefone="11999999999",
        role="SUPER_ADMIN",
        ativo=True,
    )

    admin_barbara = Usuario(
        nome="Bárbara (Admin Martinica)",
        email="barbara@martinica.com",
        senha_hash=senha_admin_hash,
        telefone="11988888888",
        role="ADMIN",
        ativo=True,
    )

    admin_ivaldo = Usuario(
        nome="Ivaldo (Admin Martinica)",
        email="ivaldo@martinica.com",
        senha_hash=senha_admin_hash,
        telefone="11977777777",
        role="ADMIN",
        ativo=True,
    )

    db.session.add_all([super_admin, admin_barbara, admin_ivaldo])
    db.session.flush()  # garante ids

    # =========================
    # Responsáveis (pais)
    # Login: CPF / Senha: telefone
    # =========================
    responsaveis_dados = [
        {
            "nome": "Felipe Rodrigues",
            "cpf": "52629121844",
            "telefone": "11992835438",
            "email": "felipe.rodrigues@teste.com",
        },
        {
            "nome": "Marcelo Almeida",
            "cpf": "38476125901",
            "telefone": "11991195202",
            "email": "marcelo.almeida@teste.com",
        },
        {
            "nome": "Mariana Ferraz",
            "cpf": "07549862137",
            "telefone": "11987654321",
            "email": "mariana.ferraz@teste.com",
        },
        {
            "nome": "Ana Souza",
            "cpf": "43928765109",
            "telefone": "11990001122",
            "email": "ana.souza@teste.com",
        },
        {
            "nome": "Carlos Pereira",
            "cpf": "29184765032",
            "telefone": "11998887766",
            "email": "carlos.pereira@teste.com",
        },
    ]

    responsaveis_objs = []

    for r in responsaveis_dados:
        user_parent = Usuario(
            nome=r["nome"],
            email=r["email"],
            senha_hash=generate_password_hash(r["telefone"]),  # senha = telefone
            telefone=r["telefone"],
            role="PARENT",
            ativo=True,
        )
        resp = Responsavel(
            usuario=user_parent,  # seta usuario_id automaticamente
            nome=r["nome"],
            cpf=r["cpf"],
            telefone=r["telefone"],
            observacoes=None,
        )
        db.session.add(user_parent)
        db.session.add(resp)
        responsaveis_objs.append(resp)

    db.session.flush()  # garante ids dos responsáveis

    # =========================
    # Grupos básicos (Sub-09, Sub-11, etc.)
    # =========================
    grupos_dados = [
        {"nome": "Sub-09", "faixa_etaria_min": 6, "faixa_etaria_max": 9},
        {"nome": "Sub-11", "faixa_etaria_min": 10, "faixa_etaria_max": 11},
        {"nome": "Sub-13", "faixa_etaria_min": 12, "faixa_etaria_max": 13},
        {"nome": "Sub-15", "faixa_etaria_min": 14, "faixa_etaria_max": 15},
        {"nome": "Sub-17", "faixa_etaria_min": 16, "faixa_etaria_max": 17},
    ]

    grupos_objs = {}
    for gd in grupos_dados:
        g = Grupo(
            nome=gd["nome"],
            faixa_etaria_min=gd["faixa_etaria_min"],
            faixa_etaria_max=gd["faixa_etaria_max"],
            descricao=None,
        )
        db.session.add(g)
        grupos_objs[gd["nome"]] = g

    db.session.flush()

    # =========================
    # Planos básicos
    # =========================
    plano_basico = Plano(
        nome="Mensalidade Básica",
        valor_mensal=100.00,
        dia_vencimento=10,
        forma_pagamento_padrao="PIX",
        periodicidade_cobranca="MENSAL",
        descricao="Treinos 2x por semana",
        ativo=True,
    )

    plano_avancado = Plano(
        nome="Mensalidade Avançada",
        valor_mensal=150.00,
        dia_vencimento=5,
        forma_pagamento_padrao="PIX",
        periodicidade_cobranca="MENSAL",
        descricao="Treinos 3x por semana + amistosos",
        ativo=True,
    )

    db.session.add_all([plano_basico, plano_avancado])
    db.session.flush()

    # =========================
    # Atletas (20) vinculados aos 5 responsáveis
    # =========================
    # Índices: 0=Felipe, 1=Marcelo, 2=Mariana, 3=Ana, 4=Carlos
    atletas_dados = [
        # Resp 0 - Felipe
        ("João Silva",        date(2012, 3, 15),  "10110110110", 0, "Sub-13"),
        ("Maria Oliveira",    date(2013, 7, 20),  "10110110111", 0, "Sub-13"),
        ("Pedro Costa",       date(2014, 11, 5),  "10110110112", 0, "Sub-11"),
        ("Ana Lima",          date(2015, 2, 28),  "10110110113", 0, "Sub-11"),

        # Resp 1 - Marcelo
        ("Lucas Souza",       date(2011, 6, 10),  "20220220220", 1, "Sub-15"),
        ("Julia Rocha",       date(2012, 9, 25),  "20220220221", 1, "Sub-13"),
        ("Gabriel Santos",    date(2013, 1, 18),  "20220220222", 1, "Sub-13"),
        ("Beatriz Alves",     date(2014, 4, 30),  "20220220223", 1, "Sub-11"),

        # Resp 2 - Mariana
        ("Rafael Gomes",      date(2010, 8, 12),  "30330330330", 2, "Sub-17"),
        ("Larissa Melo",      date(2011, 12, 3),  "30330330331", 2, "Sub-15"),
        ("Matheus Nunes",     date(2012, 5, 27),  "30330330332", 2, "Sub-13"),
        ("Sofia Cardoso",     date(2013, 10, 14), "30330330333", 2, "Sub-13"),

        # Resp 3 - Ana
        ("Enzo Ribeiro",      date(2014, 1, 9),   "40440440440", 3, "Sub-11"),
        ("Helena Fernandes",  date(2015, 3, 22),  "40440440441", 3, "Sub-09"),
        ("Davi Araújo",       date(2016, 7, 19),  "40440440442", 3, "Sub-09"),
        ("Isabela Martins",   date(2012, 11, 11), "40440440443", 3, "Sub-13"),

        # Resp 4 - Carlos
        ("Guilherme Barbosa", date(2011, 2, 6),   "50550550550", 4, "Sub-15"),
        ("Laura Freitas",     date(2013, 9, 29),  "50550550551", 4, "Sub-13"),
        ("Bernardo Teixeira", date(2014, 6, 17),  "50550550552", 4, "Sub-11"),
        ("Luiza Moraes",      date(2015, 8, 25),  "50550550553", 4, "Sub-09"),
    ]

    for nome, nasc, cpf, idx_resp, categoria in atletas_dados:
        resp = responsaveis_objs[idx_resp]
        grupo = grupos_objs.get(categoria)

        atleta = Atleta(
            nome=nome,
            rg=None,
            cpf=cpf,
            data_nascimento=nasc,
            posicao=None,
            documento=None,
            telefone_residencial=None,
            telefone=resp.telefone,
            validade_atestado=None,
            informacoes_adicionais=None,
            responsavel_nome=resp.nome,
            responsavel_cpf=resp.cpf,
            responsavel_telefone=resp.telefone,
            responsavel_parentesco="Responsável",
            status="ATIVO",
        )
        db.session.add(atleta)
        db.session.flush()

        # vínculo formal atleta-responsável
        ar = AtletaResponsavel(
            atleta_id=atleta.id,
            responsavel_id=resp.id,
            parentesco="Responsável",
        )
        db.session.add(ar)

        # vínculo atleta-grupo
        if grupo:
            ap = AtletaPlano(
                atleta_id=atleta.id,
                plano_id=plano_basico.id if categoria in ("Sub-11", "Sub-09") else plano_avancado.id,
                ativo=True,
            )
            db.session.add(ap)

    db.session.commit()
    print(">> Seed: dados iniciais criados com sucesso.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Pasta de uploads (fotos de atletas, etc.)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(atletas_bp)
    app.register_blueprint(grupos_bp)
    app.register_blueprint(atividades_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(planos_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(usuarios_bp)

    # Cria tabelas (se não existirem) e seeds
    with app.app_context():
        db.create_all()
        seed_default_data()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
