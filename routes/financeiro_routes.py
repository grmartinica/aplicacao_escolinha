from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
)
from flask_login import login_required, current_user

from extensions import db
from models import ContaReceber, AtletaResponsavel, Atleta, Responsavel, ContaPagar
from urllib.parse import quote
from datetime import datetime
import os

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")


def _require_admin():
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        flash("Você não tem permissão para essa operação financeira.", "danger")
        return False
    return True


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


# --------- Exportar financeiro (Excel/CSV/PDF/Word) ---------


@financeiro_bp.route("/exportar")
@login_required
def exportar():
    if not _require_admin():
        return redirect(url_for("financeiro.resumo"))

    formato = (request.args.get("formato") or "csv").lower()
    ext_map = {"csv": "csv", "excel": "xlsx", "pdf": "pdf", "word": "docx"}
    ext = ext_map.get(formato, "csv")

    itens = (
        ContaReceber.query.join(ContaReceber.atleta, isouter=True)
        .order_by(ContaReceber.vencimento.desc())
        .all()
    )

    linhas = ["aluno;vencimento;valor;status"]
    for c in itens:
        nome = c.atleta.nome if c.atleta else ""
        ven = c.vencimento.strftime("%d/%m/%Y") if c.vencimento else ""
        linha = ";".join(
            [
                nome,
                ven,
                f"{float(c.valor or 0):.2f}",
                c.status or "",
            ]
        )
        linhas.append(linha)

    csv_data = "\n".join(linhas)
    resp = make_response(csv_data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f'attachment; filename="financeiro.{ext}"'
    return resp


# --------- Cobrança via WhatsApp ---------


@financeiro_bp.route("/cobrar/<int:atleta_id>")
@login_required
def cobrar_whatsapp(atleta_id):
    if not _require_admin():
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
        "Segue abaixo o link para pagamento via Mercado Pago ou fale com a coordenação "
        "para combinar a melhor forma de quitação."
    )

    telefone = (atleta.responsavel_telefone or atleta.telefone or "").strip()
    telefone_digits = "".join(ch for ch in telefone if ch.isdigit())

    if not telefone_digits:
        flash("Não há telefone cadastrado para este responsável.", "danger")
        return redirect(url_for("financeiro.resumo"))

    url = f"https://wa.me/55{telefone_digits}?text={quote(msg)}"
    return redirect(url)


# --------- Mercado Pago PIX (QR Code + link) ---------


@financeiro_bp.route("/gerar-pix/<int:conta_id>")
@login_required
def gerar_pix(conta_id):
    if not _require_admin():
        return redirect(url_for("financeiro.resumo"))

    try:
        import mercadopago
    except ImportError:
        flash("Biblioteca 'mercadopago' não encontrada. Adicione ao requirements.txt.", "danger")
        return redirect(url_for("financeiro.resumo"))

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not access_token:
        flash("MERCADOPAGO_ACCESS_TOKEN não configurado nas variáveis de ambiente.", "danger")
        return redirect(url_for("financeiro.resumo"))

    conta = ContaReceber.query.get_or_404(conta_id)
    if conta.status == "PAGO":
        flash("Esta cobrança já está marcada como PAGA.", "info")
        return redirect(url_for("financeiro.resumo"))

    sdk = mercadopago.SDK(access_token)

    description = conta.descricao or f"Mensalidade {conta.id}"
    value = float(conta.valor or 0)

    payment_data = {
        "transaction_amount": value,
        "description": description,
        "payment_method_id": "pix",
        "payer": {
            "email": "pagador@example.com",
        },
    }

    result = sdk.payment().create(payment_data)
    response = result.get("response", {})

    if response.get("status") != "pending" or "point_of_interaction" not in response:
        flash("Não foi possível gerar o Pix no momento.", "danger")
        return redirect(url_for("financeiro.resumo"))

    data = response["point_of_interaction"]["transaction_data"]
    qr_code = data.get("qr_code")
    qr_base64 = data.get("qr_code_base64")
    ticket_url = data.get("ticket_url")

    return render_template(
        "financeiro_pix.html",
        conta=conta,
        qr_code=qr_code,
        qr_base64=qr_base64,
        ticket_url=ticket_url,
    )


# --------- Despesas (contas a pagar simples) ---------


@financeiro_bp.route("/despesa/nova", methods=["GET", "POST"])
@login_required
def nova_despesa():
    if not _require_admin():
        return redirect(url_for("financeiro.resumo"))

    if request.method == "POST":
        fornecedor = (request.form.get("fornecedor") or "").strip()
        descricao = (request.form.get("descricao") or "").strip()
        venc_str = request.form.get("vencimento") or ""
        valor_str = request.form.get("valor") or "0"

        if not fornecedor or not venc_str:
            flash("Fornecedor e vencimento são obrigatórios.", "danger")
            return redirect(url_for("financeiro.nova_despesa"))

        try:
            vencimento = datetime.strptime(venc_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Data de vencimento inválida.", "danger")
            return redirect(url_for("financeiro.nova_despesa"))

        try:
            valor = float(valor_str.replace(",", "."))
        except ValueError:
            flash("Valor inválido.", "danger")
            return redirect(url_for("financeiro.nova_despesa"))

        conta = ContaPagar(
            fornecedor=fornecedor,
            descricao=descricao,
            vencimento=vencimento,
            valor=valor,
            status="PENDENTE",
        )
        db.session.add(conta)
        db.session.commit()

        flash("Despesa registrada com sucesso.", "success")
        return redirect(url_for("financeiro.resumo"))

    return render_template("financeiro_despesa_form.html")
