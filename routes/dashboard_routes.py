from flask import Blueprint, render_template
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from extensions import db
from models import Atleta, ContaReceber

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Redireciona com base no perfil
    if current_user.role == 'ADMIN':
        return admin_dashboard()
    elif current_user.role == 'COACH':
        return render_template('dashboard_coach.html')
    elif current_user.role == 'PARENT':
        return redirect(url_for('financeiro.resumo_responsavel'))
    else:
        return redirect(url_for('auth.login'))


def admin_dashboard():
    total_atletas = Atleta.query.filter_by(status='ATIVO').count()

    inadimplentes = ContaReceber.query.filter(
        ContaReceber.status != 'PAGO'
    ).count()

    saldo_a_receber = float(sum(
        [c.valor for c in ContaReceber.query.filter(ContaReceber.status != 'PAGO')]
    ))

    hoje = date.today()
    aniversariantes = Atleta.query.filter(
        db.extract('month', Atleta.data_nascimento) == hoje.month
    ).count()

    return render_template(
        'dashboard_admin.html',
        total_atletas=total_atletas,
        inadimplentes=inadimplentes,
        saldo=saldo_a_receber,
        aniversariantes=aniversariantes
    )