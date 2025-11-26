from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import ContaReceber, AtletaResponsavel, Atleta, Responsavel
from urllib.parse import quote

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")


@financeiro_bp.route("/resumo")
@login_required
def resumo():
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        return render_template(
            "financeiro_resumo.html",
            total_pendente=0,
            total_pago=0,
            qtd_inad=0,
            itens=[],
            filtros={},
        )

    nome = (request.args.get("nome") or "").strip()
    status = request.args.get("status") or "TODOS"
    so_inadimplentes = request.args.get("inadimplentes") == "1"

    query = ContaReceber.query.join(ContaReceber.atleta, isouter=True)

    if so_inadimplentes:
        query = query.filter(ContaReceber.status.in_(("PENDENTE", "ATRASADO")))
    elif status != "TODOS":
        query = query.filter(ContaReceber.status == status)

    if nome:
        query = query.filter(Atleta.nome.ilike(f"%{nome}%"))

    itens = query.order_by(ContaReceber.vencimento.desc()).limit(200).all()

    total_pendente = (
        db.session.query(db.func.sum(ContaReceber.valor))
        .filter(ContaReceber.status != "PAGO")
        .scalar()
        or 0
    )
    total_pago = (
        db.session.query(db.func.sum(ContaReceber.valor))
        .filter(ContaReceber.status == "PAGO")
        .scalar()
        or 0
    )
    qtd_inad = (
        ContaReceber.query.filter(
            ContaReceber.status.in_(("PENDENTE", "ATRASADO"))
        ).count()
    )

    filtros = {
        "nome": nome,
        "status": status,
        "inadimplentes": "1" if so_inadimplentes else "0",
    }

    return render_template(
        "financeiro_resumo.html",
        total_pendente=float(total_pendente),
        total_pago=float(total_pago),
        qtd_inad=qtd_inad,
        itens=itens,
        filtros=filtros,
    )


@financeiro_bp.route("/responsavel")
@login_required
def resumo_responsavel():
    if current_user.role != "PARENT":
        return render_template("financeiro_responsavel.html", itens=[])

    links = (
        AtletaResponsavel.query.join(AtletaResponsavel.responsavel)
        .filter(AtletaResponsavel.responsavel.has(usuario_id=current_user.id))
        .all()
    )
    atleta_ids = [l.atleta_id for l in links]
    itens = (
        ContaReceber.query.filter(ContaReceber.atleta_id.in_(atleta_ids))
        .order_by(ContaReceber.vencimento.desc())
        .all()
    )
    return render_template("financeiro_responsavel.html", itens=itens)


@financeiro_bp.route("/cobrar/<int:atleta_id>")
@login_required
def cobrar_whatsapp(atleta_id):
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        flash("Você não tem permissão para enviar cobranças financeiras.", "danger")
        return redirect(url_for("financeiro.resumo"))

    atleta = Atleta.query.get_or_404(atleta_id)

    pendencias = (
        ContaReceber.query.filter(
            ContaReceber.atleta_id == atleta_id,
            ContaReceber.status.in_(("PENDENTE", "ATRASADO")),
        )
        .order_by(ContaReceber.vencimento)
        .all()
    )

    if not pendencias:
        flash("Este atleta não possui pendências financeiras.", "info")
        return redirect(url_for("financeiro.resumo"))

    meses = []
    total = 0.0
    for c in pendencias:
        if c.vencimento:
            meses.append(c.vencimento.strftime("%m/%Y"))
        total += float(c.valor or 0)

    meses_str = ", ".join(sorted(set(meses)))
    nome_resp = atleta.responsavel_nome or "responsável"
    nome_atl = atleta.nome

    msg = (
        f"Olá {nome_resp}, tudo bem?\n\n"
        f"O seu filho(a) {nome_atl} está com as seguintes pendências financeiras:\n"
        f"- Mensalidades de: {meses_str}\n"
        f"- Valor total em aberto: R$ {total:,.2f}\n\n"
        "Segue abaixo o link para pagamento via Mercado Pago ou fale com a coordenação para combinar a melhor forma de quitação."
    )

    telefone = (atleta.responsavel_telefone or atleta.telefone or "").strip()
    telefone_digits = "".join(ch for ch in telefone if ch.isdigit())

    if not telefone_digits:
        flash("Não há telefone cadastrado para este responsável.", "danger")
        return redirect(url_for("financeiro.resumo"))

    url = f"https://wa.me/55{telefone_digits}?text={quote(msg)}"
    return redirect(url)
