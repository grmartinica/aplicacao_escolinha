from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from extensions import db
from models import Grupo

grupos_bp = Blueprint("grupos", __name__, url_prefix="/grupos")


def _require_staff():
    return current_user.role in ("ADMIN", "COACH", "SUPER_ADMIN")


@grupos_bp.route("/listar")
@login_required
def listar():
    if not _require_staff():
        flash("Você não tem permissão para acessar os grupos.", "danger")
        return redirect(url_for("dashboard.index"))

    grupos = Grupo.query.order_by(Grupo.nome).all()
    return render_template("grupos_listar.html", grupos=grupos)


@grupos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if not _require_staff():
        flash("Você não tem permissão para criar grupos.", "danger")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        faixa_min = request.form.get("faixa_etaria_min") or None
        faixa_max = request.form.get("faixa_etaria_max") or None
        descricao = (request.form.get("descricao") or "").strip()

        if not nome:
            flash("Informe o nome do grupo.", "danger")
            return redirect(url_for("grupos.novo"))

        grupo = Grupo(
            nome=nome,
            faixa_etaria_min=int(faixa_min) if faixa_min else None,
            faixa_etaria_max=int(faixa_max) if faixa_max else None,
            descricao=descricao,
        )
        db.session.add(grupo)
        db.session.commit()

        flash("Grupo criado com sucesso.", "success")
        return redirect(url_for("grupos.listar"))

    return render_template("grupos_form.html", grupo=None)


@grupos_bp.route("/<int:grupo_id>/editar", methods=["GET", "POST"])
@login_required
def editar(grupo_id):
    if not _require_staff():
        flash("Você não tem permissão para editar grupos.", "danger")
        return redirect(url_for("dashboard.index"))

    grupo = Grupo.query.get_or_404(grupo_id)

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        faixa_min = request.form.get("faixa_etaria_min") or None
        faixa_max = request.form.get("faixa_etaria_max") or None
        descricao = (request.form.get("descricao") or "").strip()

        if not nome:
            flash("Informe o nome do grupo.", "danger")
            return redirect(url_for("grupos.editar", grupo_id=grupo.id))

        grupo.nome = nome
        grupo.faixa_etaria_min = int(faixa_min) if faixa_min else None
        grupo.faixa_etaria_max = int(faixa_max) if faixa_max else None
        grupo.descricao = descricao

        db.session.commit()
        flash("Grupo atualizado com sucesso.", "success")
        return redirect(url_for("grupos.listar"))

    return render_template("grupos_form.html", grupo=grupo)


@grupos_bp.route("/exportar")
@login_required
def exportar():
    if not _require_staff():
        flash("Você não tem permissão para exportar grupos.", "danger")
        return redirect(url_for("dashboard.index"))

    formato = (request.args.get("formato") or "csv").lower()
    ext_map = {"csv": "csv", "excel": "xlsx", "pdf": "pdf", "word": "docx"}
    ext = ext_map.get(formato, "csv")

    grupos = Grupo.query.order_by(Grupo.nome).all()
    linhas = ["nome;faixa_etaria_min;faixa_etaria_max;descricao"]

    for g in grupos:
        linha = ";".join(
            [
                g.nome or "",
                str(g.faixa_etaria_min or ""),
                str(g.faixa_etaria_max or ""),
                (g.descricao or "").replace("\n", " "),
            ]
        )
        linhas.append(linha)

    csv_data = "\n".join(linhas)
    resp = make_response(csv_data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f'attachment; filename="grupos.{ext}"'
    return resp
