from urllib.parse import quote

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models import ContaReceber, AtletaResponsavel, Atleta

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@financeiro_bp.route('/resumo')
@login_required
def resumo():
    """
    Visão ADMIN com filtros + botão de cobrança por WhatsApp.
    """
    status_filtro = (request.args.get('status') or '').upper()
    nome_atleta = (request.args.get('nome') or '').strip()

    query = ContaReceber.query.join(ContaReceber.atleta, isouter=True)

    if status_filtro == 'INADIMPLENTE':
        query = query.filter(ContaReceber.status.in_(('PENDENTE', 'ATRASADO')))
    elif status_filtro:
        query = query.filter(ContaReceber.status == status_filtro)

    if nome_atleta:
        query = query.filter(Atleta.nome.ilike(f"%{nome_atleta}%"))

    query = query.order_by(ContaReceber.vencimento.desc())
    itens = query.all()

    # totais baseados no filtro atual
    total_pendente = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.id.in_([c.id for c in itens]),
                ContaReceber.status != 'PAGO') \
        .scalar() or 0

    total_pago = db.session.query(db.func.sum(ContaReceber.valor)) \
        .filter(ContaReceber.id.in_([c.id for c in itens]),
                ContaReceber.status == 'PAGO') \
        .scalar() or 0

    qtd_inad = len([c for c in itens if c.status in ('PENDENTE', 'ATRASADO')])

    filtros = {
        "status": status_filtro,
        "nome": nome_atleta
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
    """
    Visão do responsável: mensalidades dos atletas vinculados.
    """
    if current_user.role != 'PARENT':
        return render_template('financeiro_responsavel.html', itens=[])

    links = AtletaResponsavel.query.join(AtletaResponsavel.responsavel) \
        .filter(AtletaResponsavel.responsavel.has(usuario_id=current_user.id)).all()
    atleta_ids = [l.atleta_id for l in links]

    itens = ContaReceber.query.filter(ContaReceber.atleta_id.in_(atleta_ids)) \
        .order_by(ContaReceber.vencimento.desc()).all()

    return render_template('financeiro_responsavel.html', itens=itens)


@financeiro_bp.route('/cobrar/<int:atleta_id>')
@login_required
def cobrar_whatsapp(atleta_id):
    """
    Monta mensagem de cobrança resumida e redireciona para o WhatsApp (web/app).
    """
    atleta = Atleta.query.get_or_404(atleta_id)

    telefone = (atleta.responsavel_telefone or '').strip()
    if not telefone:
        # sem telefone, volta para o financeiro
        return redirect(url_for('financeiro.resumo'))

    # deixa só números
    telefone_digits = ''.join(ch for ch in telefone if ch.isdigit())

    pendentes = ContaReceber.query.filter(
        ContaReceber.atleta_id == atleta.id,
        ContaReceber.status.in_(('PENDENTE', 'ATRASADO'))
    ).order_by(ContaReceber.vencimento.asc()).all()

    if not pendentes:
        return redirect(url_for('financeiro.resumo'))

    meses = []
    total = 0
    for c in pendentes:
        meses.append(c.vencimento.strftime('%m/%Y'))
        total += float(c.valor)

    meses_str = ', '.join(sorted(set(meses)))

    msg = (
        f"Olá! Aqui é da escolinha.\n\n"
        f"As mensalidades dos meses {meses_str} estão pendentes de pagamento "
        f"para o atleta {atleta.nome}.\n"
        f"Valor total em aberto: R$ {total:,.2f}.\n\n"
        f"PIX para pagamento: 11987019721\n"
        f"Qualquer dúvida, estamos à disposição."
    )

    url = f"https://wa.me/55{telefone_digits}?text={quote(msg)}"
    return redirect(url)
