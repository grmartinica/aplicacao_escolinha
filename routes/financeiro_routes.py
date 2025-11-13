from flask import Blueprint, render_template
<<<<<<< HEAD
from extensions import db
from models import ContaReceber
=======
from flask_login import login_required, current_user
from extensions import db
from models import ContaReceber, AtletaResponsavel
>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')

@financeiro_bp.route('/resumo')
@login_required
def resumo():
    # ADMIN: visão geral
    total_pendente = db.session.query(db.func.sum(ContaReceber.valor))\
        .filter(ContaReceber.status != 'PAGO').scalar() or 0
    total_pago = db.session.query(db.func.sum(ContaReceber.valor))\
        .filter(ContaReceber.status == 'PAGO').scalar() or 0
    qtd_inad = ContaReceber.query.filter(ContaReceber.status.in_(("PENDENTE","ATRASADO"))).count()
    itens = ContaReceber.query.order_by(ContaReceber.vencimento.desc()).limit(50).all()
    return render_template('financeiro_resumo.html',
                           total_pendente=float(total_pendente),
                           total_pago=float(total_pago),
                           qtd_inad=qtd_inad,
                           itens=itens)

@financeiro_bp.route('/responsavel')
@login_required
def resumo_responsavel():
    # PARENT: visão do(s) filho(s)
    if current_user.role != 'PARENT':
        return render_template('financeiro_responsavel.html', itens=[])
    # acha atletas vinculados ao responsável
    links = AtletaResponsavel.query.join(AtletaResponsavel.responsavel)\
        .filter(AtletaResponsavel.responsavel.has(usuario_id=current_user.id)).all()
    atleta_ids = [l.atleta_id for l in links]
    itens = ContaReceber.query.filter(ContaReceber.atleta_id.in_(atleta_ids))\
        .order_by(ContaReceber.vencimento.desc()).all()
    return render_template('financeiro_responsavel.html', itens=itens)
