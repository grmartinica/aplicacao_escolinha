from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Usuario

usuarios_bp = Blueprint("usuarios_sistema", __name__, url_prefix="/usuarios-sistema")


@usuarios_bp.route("/")
@login_required
def listar():
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        flash("Você não tem permissão para gerenciar usuários do sistema.", "danger")
        return redirect(url_for("dashboard.index"))

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios_listar.html", usuarios=usuarios)
