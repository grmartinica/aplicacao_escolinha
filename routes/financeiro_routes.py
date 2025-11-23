from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import db
from models import ContaReceber, AtletaResponsavel, Atleta

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@financeiro_bp.route('/resumo')
@login_required
def resumo():
    # Filtros
    status = request.args.get('status', 'TODOS')  # TODOS, INADIMPLENTE, PAGO, PENDENTE, ATRASADO, CANCELADO
    nome = (request.args.get('nome') or '').strip()
    metodo = request.args.get('metodo', 'TODOS')  # TODOS, PIX, CREDITO, DEBITO, DINHEIRO, ISENTO

    query = ContaReceber.query.join(Atleta, isouter=True)

    if nome:
        query = query.filter(Atleta.nome.ilike(f"%{nome}%"))

    if metodo != 'TODOS':
        query = query.filter(ContaReceber.metodo_pagamento == metodo)

    if status == 'INADIMPLENTE':
        query = query.filter(ContaReceber.status.in_(('PENDENTE', 'ATRASADO')))
    elif status != 'TODOS':
        query = query.filter(ContaReceber.status == status)

    # Totais baseados na query filtrada
    total_pendente = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.status != 'PAGO') \
        .scalar() or 0

    total_pago = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.status == 'PAGO') \
        .scalar() or 0

    qtd_inad = query.filter(ContaReceber.status.in_(("PENDENTE", "ATRASADO"))).count()

    itens = query.order_by(ContaReceber.vencimento.desc()).limit(100).all()

    return render_template(
        'financeiro_resumo.html',
        total_pendente=float(total_pendente),
        total_pago=float(total_pago),
        qtd_inad=qtd_inad,
        itens=itens,
        filtro_status=status,
        filtro_nome=nome,
        filtro_metodo=metodo
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
