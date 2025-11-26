from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager
from models import Usuario, Responsavel

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tipo_login = request.form.get("tipo_login") or "admin"

        # ADMIN / PROFESSOR / SUPER_ADMIN
        if tipo_login == "admin":
            email = (request.form.get("email") or "").strip()
            senha = (request.form.get("senha") or "").strip()

            if not email or not senha:
                flash("Informe e-mail e senha.", "danger")
                return render_template("login.html")

            user = (
                Usuario.query.filter(
                    Usuario.email == email,
                    Usuario.ativo.is_(True),
                    Usuario.role.in_(("ADMIN", "COACH", "SUPER_ADMIN")),
                )
                .first()
            )

            if not user or not check_password_hash(user.senha_hash, senha):
                flash("E-mail ou senha inválidos.", "danger")
                return render_template("login.html")

            login_user(user)
            return redirect(url_for("dashboard.index"))

        # RESPONSÁVEL
        elif tipo_login == "responsavel":
            cpf = (request.form.get("cpf") or "").strip()
            senha = (request.form.get("telefone") or "").strip()

            if not cpf or not senha:
                flash("Informe CPF e senha.", "danger")
                return render_template("login.html")

            resp = Responsavel.query.filter_by(cpf=cpf).first()
            if not resp or not resp.usuario or not resp.usuario.ativo:
                flash("CPF não localizado ou sem acesso configurado.", "danger")
                return render_template("login.html")

            user = resp.usuario
            if user.role != "PARENT":
                flash("Esse CPF não está configurado como responsável.", "danger")
                return render_template("login.html")

            if not check_password_hash(user.senha_hash, senha):
                flash("CPF ou senha inválidos.", "danger")
                return render_template("login.html")

            login_user(user)
            return redirect(url_for("dashboard.index"))

        else:
            flash("Tipo de login inválido.", "danger")
            return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# cadastro de responsável em 2 passos (já estava no doc):
@auth_bp.route("/cadastro_responsavel", methods=["GET", "POST"])
def cadastro_responsavel_cpf():
    if request.method == "POST":
        cpf = (request.form.get("cpf") or "").strip()

        resp = Responsavel.query.filter_by(cpf=cpf).first()
        if not resp:
            flash("CPF não localizado. Por favor, entre em contato com a coordenação.", "danger")
            return render_template("cadastro_responsavel_cpf.html")

        if resp.usuario_id:
            flash("Este responsável já possui acesso ao sistema. Utilize a tela de login.", "warning")
            return redirect(url_for("auth.login"))

        return redirect(url_for("auth.cadastro_responsavel_criar_usuario", responsavel_id=resp.id))

    return render_template("cadastro_responsavel_cpf.html")


@auth_bp.route("/cadastro_responsavel/<int:responsavel_id>", methods=["GET", "POST"])
def cadastro_responsavel_criar_usuario(responsavel_id):
    resp = Responsavel.query.get_or_404(responsavel_id)

    if resp.usuario_id:
        flash("Este responsável já possui usuário criado. Faça login.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip() or resp.nome
        email = (request.form.get("email") or "").strip()
        senha = (request.form.get("senha") or "").strip()
        confirmar = (request.form.get("confirmar_senha") or "").strip()

        if not email or not senha:
            flash("Informe e-mail e senha.", "danger")
            return render_template("cadastro_responsavel_usuario.html", responsavel=resp)

        if senha != confirmar:
            flash("As senhas não conferem.", "danger")
            return render_template("cadastro_responsavel_usuario.html", responsavel=resp)

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "danger")
            return render_template("cadastro_responsavel_usuario.html", responsavel=resp)

        user = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            telefone=resp.telefone,
            role="PARENT",
            ativo=True,
        )
        db.session.add(user)
        db.session.flush()

        resp.usuario_id = user.id
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("cadastro_responsavel_usuario.html", responsavel=resp)
