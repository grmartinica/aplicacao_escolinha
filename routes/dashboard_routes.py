from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from extensions import db
from models import Atleta, ContaReceber, Atividade

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    # Redireciona com base no perfil
    if current_user.role in ("ADMIN", "SUPER_ADMIN"):
        return admin_dashboard()
    elif current_user.role == "COACH":
        return render_template("dashboard_coach.html")
    elif current_user.role == "PARENT":
        return render_template("dashboard_parent.html")
    else:
        return redirect(url_for("auth.login"))


def admin_dashboard():
    hoje = date.today()

    total_atletas_ativos = Atleta.query.filter_by(status="ATIVO").count()

    # Receita total paga
    receita_paga = (
        db.session.query(db.func.coalesce(db.func.sum(ContaReceber.valor), 0))
        .filter(ContaReceber.status == "PAGO")
        .scalar()
    )
    receita_paga = float(receita_paga or 0)

    # Documentos pendentes (critério simples: atestado sem validade ou vencido)
    documentos_pendentes = (
        Atleta.query.filter(
            (Atleta.validade_atestado.is_(None))
            | (Atleta.validade_atestado < hoje)
        ).count()
    )

    # Quantidade de alunos inadimplentes (contas pendentes/atrasadas, distintos por atleta)
    qtd_inadimplentes = (
        db.session.query(db.func.count(db.func.distinct(ContaReceber.atleta_id)))
        .filter(ContaReceber.status.in_(("PENDENTE", "ATRASADO")))
        .scalar()
        or 0
    )

    # Próximo treino
    proxima_atividade = (
        Atividade.query.filter(Atividade.data >= hoje)
        .order_by(Atividade.data, Atividade.hora_inicio)
        .first()
    )

    return render_template(
        "dashboard_admin.html",
        total_atletas_ativos=total_atletas_ativos,
        receita_paga=receita_paga,
        documentos_pendentes=documentos_pendentes,
        qtd_inadimplentes=qtd_inadimplentes,
        proxima_atividade=proxima_atividade,
    )
