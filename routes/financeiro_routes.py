from flask import Blueprint, render_template
from extensions import db
from models import ContaReceber

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')

@financeiro_bp.route('/contas_receber')
def resumo():
    contas = ContaReceber.query.all()
    total_receber = sum([float(c.valor) for c in contas if c.status != 'PAGo'])
    total_pago = sum([float(c.valor) for c in contas if c.status == 'PAGO'])
    return render_template('financeiro_resumo.html', contas=contas, total_receber=total_receber, total_pago=total_pago)