from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import db
from models import ContaReceber, AtletaResponsavel

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@financeiro_bp.route('/resumo')
@login_required
def resumo():
    """
    Visão financeira do ADMIN.
    Suporta ?status=pendentes para mostrar apenas PENDENTE/ATRASADO
    """
    status_filter = request.args.get('status')  # ex: "pendentes"

    base_query = ContaReceber.query

    if status_filter == 'pendentes':
        base_query = base_query.filter(ContaReceber.status.in_(("PENDENTE", "ATRASADO")))

    total_pendente = db.session.query(db.func.coalesce(db.func.sum(ContaReceber.valor), 0)) \
        .filter(ContaReceber.status != 'PAGO').scalar() or 0
    total_pago = db.session.query(db.func.coalesce(db.func.sum(ContaReceber.valor), 0)) \
        .filter(ContaReceber.status == 'PAGO').scalar() or 0

    qtd_inad = ContaReceber.query.filter(
        ContaReceber.status.in_(("PENDENTE", "ATRASADO"))
    ).count()

    itens = base_query.order_by(ContaReceber.vencimento.desc()).limit(50).all()

    return render_template(
        'financeiro_resumo.html',
        total_pendente=float(total_pendente),
        total_pago=float(total_pago),
        qtd_inad=qtd_inad,
        itens=itens,
        status_filter=status_filter,
    )


@financeiro_bp.route('/responsavel')
@login_required
def resumo_responsavel():
    # PARENT: visão do(s) filho(s)
    if current_user.role != 'PARENT':
        return render_template('financeiro_responsavel.html', itens=[])

    links = AtletaResponsavel.query.join(AtletaResponsavel.responsavel) \
        .filter(AtletaResponsavel.responsavel.has(usuario_id=current_user.id)).all()
    atleta_ids = [l.atleta_id for l in links]

    itens = ContaReceber.query.filter(ContaReceber.atleta_id.in_(atleta_ids)) \
        .order_by(ContaReceber.vencimento.desc()).all()

    return render_template('financeiro_responsavel.html', itens=itens)
