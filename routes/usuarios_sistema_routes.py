from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from extensions import db
from models import Usuario

usuarios_bp = Blueprint("usuarios_sistema", __name__, url_prefix="/usuarios-sistema")


def _require_admin():
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        flash("Você não tem permissão para gerenciar usuários do sistema.", "danger")
        return False
    return True


@usuarios_bp.route("/")
@login_required
def listar():
    if not _require_admin():
        return redirect(url_for("dashboard.index"))

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios_listar.html", usuarios=usuarios)


@usuarios_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if not _require_admin():
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip()
        telefone = (request.form.get("telefone") or "").strip()
        role = request.form.get("role") or "COACH"
        senha = (request.form.get("senha") or "").strip()

        if not nome or not email or not senha:
            flash("Nome, e-mail e senha são obrigatórios.", "danger")
            return redirect(url_for("usuarios_sistema.novo"))

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "danger")
            return redirect(url_for("usuarios_sistema.novo"))

        user = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            role=role,
            senha_hash=generate_password_hash(senha),
            ativo=True,
        )
        db.session.add(user)
        db.session.commit()

        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for("usuarios_sistema.listar"))

    return render_template("usuarios_form.html", usuario=None)


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
def editar(usuario_id):
    if not _require_admin():
        return redirect(url_for("dashboard.index"))

    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip()
        telefone = (request.form.get("telefone") or "").strip()
        role = request.form.get("role") or usuario.role
        ativo = request.form.get("ativo") == "1"

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return redirect(url_for("usuarios_sistema.editar", usuario_id=usuario.id))

        if usuario.role == "SUPER_ADMIN" and current_user.role != "SUPER_ADMIN":
            flash("Apenas o SUPER_ADMIN pode alterar outro SUPER_ADMIN.", "danger")
            return redirect(url_for("usuarios_sistema.listar"))

        usuario.nome = nome
        usuario.email = email
        usuario.telefone = telefone
        usuario.role = role
        usuario.ativo = ativo

        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("usuarios_sistema.listar"))

    return render_template("usuarios_form.html", usuario=usuario)


@usuarios_bp.route("/<int:usuario_id>/reset-senha")
@login_required
def reset_senha(usuario_id):
    if not _require_admin():
        return redirect(url_for("dashboard.index"))

    usuario = Usuario.query.get_or_404(usuario_id)

    nova_senha = "Aurora123"
    usuario.senha_hash = generate_password_hash(nova_senha)
    db.session.commit()

    flash(f"Senha de {usuario.nome} redefinida para: {nova_senha}", "info")
    return redirect(url_for("usuarios_sistema.listar"))
