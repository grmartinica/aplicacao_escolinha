from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db, login_manager
from models import Usuario
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from extensions import db, login_manager
from models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        senha = (request.form.get('senha') or '').strip()

        user = Usuario.query.filter_by(email=email, ativo=True).first()

        if not user or not check_password_hash(user.senha_hash, senha):
            flash('E-mail ou senha inválidos.', 'danger')
            return render_template('login.html')

        login_user(user)
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))