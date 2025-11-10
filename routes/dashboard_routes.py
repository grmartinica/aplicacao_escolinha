from flask import Blueprint, render_template
from aplicacao_escolhinha.models import Atleta, ContaReceber

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    total_atletas = Atleta.query.count()
    inadimplentes = ContaReceber.query.filter(ContaReceber.status != 'PAGO').count()
    saldo = sum([float(c.valor) for c in ContaReceber.query.all()])
    return render_template('dashboard_admin.html',
                           total_atletas=total_atletas,
                           inadimplentes=inadimplentes,
                           saldo=saldo)