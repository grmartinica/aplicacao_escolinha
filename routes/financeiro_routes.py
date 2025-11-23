# routes/financeiro_routes.py
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from extensions import db
from models import ContaReceber, AtletaResponsavel, Atleta

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@financeiro_bp.route('/resumo')
@login_required
def resumo():
    """
    Visão ADMIN com filtros:
    - nome do atleta
    - status (PENDENTE, ATRASADO, PAGO, CANCELADO, TODOS)
    - filtro rápido de inadimplentes (PENDENTE + ATRASADO)
    """
    nome = (request.args.get('nome') or '').strip()
    status = request.args.get('status') or 'TODOS'
    so_inadimplentes = request.args.get('inadimplentes') == '1'

    query = ContaReceber.query.join(ContaReceber.atleta, isouter=True)

    if so_inadimplentes:
        query = query.filter(ContaReceber.status.in_(('PENDENTE', 'ATRASADO')))
    elif status != 'TODOS':
        query = query.filter(ContaReceber.status == status)

    if nome:
        query = query.filter(Atleta.nome.ilike(f'%{nome}%'))

    itens = query.order_by(ContaReceber.vencimento.desc()).limit(100).all()

    total_pendente = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.status != 'PAGO').scalar() or 0
    total_pago = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.status == 'PAGO').scalar() or 0
    qtd_inad = ContaReceber.query.filter(
        ContaReceber.status.in_(("PENDENTE", "ATRASADO"))
    ).count()

    filtros = {
        'nome': nome,
        'status': status,
        'inadimplentes': '1' if so_inadimplentes else '0'
    }

    return render_template(
        'financeiro_resumo.html',
        total_pendente=float(total_pendente),
        total_pago=float(total_pago),
        qtd_inad=qtd_inad,
        itens=itens,
        filtros=filtros
    )


@financeiro_bp.route('/responsavel')
@login_required
def resumo_responsavel():
    if current_user.role != 'PARENT':
        return render_template('financeiro_responsavel.html', itens=[])

    links = AtletaResponsavel.query.join(AtletaResponsavel.responsavel) \
        .filter(AtletaResponsavel.responsavel.has(usuario_id=current_user.id)).all()
    atleta_ids = [l.atleta_id for l in links]
    itens = ContaReceber.query.filter(ContaReceber.atleta_id.in_(atleta_ids)) \
        .order_by(ContaReceber.vencimento.desc()).all()
    return render_template('financeiro_responsavel.html', itens=itens)
