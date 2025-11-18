from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Plano

planos_bp = Blueprint("planos", __name__, url_prefix="/planos")


@planos_bp.route("/")
@login_required
def listar():
    planos = Plano.query.order_by(Plano.ativo.desc(), Plano.nome).all()
    return render_template("planos_listar.html", planos=planos)


@planos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        valor_str = (request.form.get("valor_mensal") or "0").replace(",", ".")
        dia_vencimento = request.form.get("dia_vencimento", type=int)
        forma_pagamento_padrao = request.form.get("forma_pagamento_padrao") or "PIX"
        periodicidade_cobranca = request.form.get("periodicidade_cobranca") or "MENSAL"
        descricao = (request.form.get("descricao") or "").strip()
        ativo = bool(request.form.get("ativo"))

        if not nome or not dia_vencimento:
            flash("Preencha nome e dia de vencimento.", "danger")
            return redirect(url_for("planos.novo"))

        try:
            valor_mensal = float(valor_str)
        except ValueError:
            flash("Valor mensal inválido.", "danger")
            return redirect(url_for("planos.novo"))

        plano = Plano(
            nome=nome,
            valor_mensal=valor_mensal,
            dia_vencimento=dia_vencimento,
            forma_pagamento_padrao=forma_pagamento_padrao,
            periodicidade_cobranca=periodicidade_cobranca,
            descricao=descricao or None,
            ativo=ativo,
        )
        db.session.add(plano)
        db.session.commit()
        flash("Plano criado com sucesso!", "success")
        return redirect(url_for("planos.listar"))

    return render_template("planos_novo.html")
