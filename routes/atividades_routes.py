# routes/atividades_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from extensions import db
from models import Atividade, Grupo, Presenca, AtletaGrupo, Atleta

atividades_bp = Blueprint("atividades", __name__, url_prefix="/atividades")


def _require_staff():
    """
    Apenas ADMIN, COACH e SUPER_ADMIN podem criar/editar atividades
    e registrar presenças.
    """
    return current_user.role in ("ADMIN", "COACH", "SUPER_ADMIN")


@atividades_bp.route("/listar")
@login_required
def listar():
    """
    Lista todas as atividades cadastradas, agrupando por dia.
    - Ordena da mais recente para a mais antiga.
    - Envia 'atividades' e 'atividades_por_dia' para o template.
    """
    atividades = (
        Atividade.query.order_by(Atividade.data.desc(), Atividade.hora_inicio.desc()).all()
    )

    atividades_por_dia = {}
    for a in atividades:
        atividades_por_dia.setdefault(a.data, []).append(a)

    return render_template(
        "atividades_listar.html",
        atividades=atividades,
        atividades_por_dia=atividades_por_dia,
    )


@atividades_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    """
    Cadastro de nova atividade:
    - título, grupo, data, hora de início, local, descrição
    - opção de repetir semanalmente por N semanas
    """
    if not _require_staff():
        flash("Você não tem permissão para cadastrar atividades.", "danger")
        return redirect(url_for("atividades.listar"))

    grupos = Grupo.query.order_by(Grupo.nome).all()

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        grupo_id = request.form.get("grupo_id", type=int)
        data_str = request.form.get("data")
        hora_inicio_str = request.form.get("hora_inicio")
        local = (request.form.get("local") or "").strip() or None
        descricao = (request.form.get("descricao") or "").strip() or None

        repetir = request.form.get("repetir") == "on"
        repeticoes = 12 if repetir else 1

        if not all([titulo, grupo_id, data_str, hora_inicio_str]):
            flash("Preencha título, grupo, data e hora inicial.", "danger")
            return redirect(url_for("atividades.nova"))

        try:
            data_base = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Data da atividade inválida.", "danger")
            return redirect(url_for("atividades.nova"))

        try:
            hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        except ValueError:
            flash("Hora de início inválida.", "danger")
            return redirect(url_for("atividades.nova"))

        if repeticoes < 1:
            repeticoes = 1

        # cria a(s) atividade(s)
        for i in range(repeticoes):
            data_atividade = data_base + timedelta(weeks=i) if repetir else data_base
            atividade = Atividade(
                titulo=titulo,
                grupo_id=grupo_id,
                coach_id=current_user.id,
                data=data_atividade,
                hora_inicio=hora_inicio,
                local=local,
                descricao=descricao,
            )
            db.session.add(atividade)

        db.session.commit()

        flash("Atividade criada com sucesso!", "success")
        return redirect(url_for("atividades.listar"))

    # importante: mandar atividade=None pro template
    return render_template("atividades_nova.html", grupos=grupos, atividade=None)


@atividades_bp.route("/<int:atividade_id>/editar", methods=["GET", "POST"])
@login_required
def editar(atividade_id):
    """
    Edição de uma atividade já existente.
    Reaproveita o mesmo formulário de criação.
    """
    if not _require_staff():
        flash("Você não tem permissão para editar atividades.", "danger")
        return redirect(url_for("atividades.listar"))

    atividade = Atividade.query.get_or_404(atividade_id)
    grupos = Grupo.query.order_by(Grupo.nome).all()

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        grupo_id = request.form.get("grupo_id", type=int)
        data_str = request.form.get("data")
        hora_inicio_str = request.form.get("hora_inicio")
        local = (request.form.get("local") or "").strip() or None
        descricao = (request.form.get("descricao") or "").strip() or None

        if not all([titulo, grupo_id, data_str, hora_inicio_str]):
            flash("Preencha título, grupo, data e hora inicial.", "danger")
            return redirect(url_for("atividades.editar", atividade_id=atividade.id))

        try:
            data_atividade = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Data da atividade inválida.", "danger")
            return redirect(url_for("atividades.editar", atividade_id=atividade.id))

        try:
            hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        except ValueError:
            flash("Hora de início inválida.", "danger")
            return redirect(url_for("atividades.editar", atividade_id=atividade.id))

        atividade.titulo = titulo
        atividade.grupo_id = grupo_id
        atividade.data = data_atividade
        atividade.hora_inicio = hora_inicio
        atividade.local = local
        atividade.descricao = descricao

        db.session.commit()
        flash("Atividade atualizada com sucesso!", "success")
        return redirect(url_for("atividades.listar"))

    # reaproveita o mesmo template da criação
    return render_template("atividades_nova.html", grupos=grupos, atividade=atividade)


@atividades_bp.route("/<int:atividade_id>/presencas", methods=["GET", "POST"])
@login_required
def presencas(atividade_id):
    """
    Registro de presença por atividade:
    - Lista atletas do grupo vinculado à atividade
    - Permite marcar status + observação
    """
    if not _require_staff():
        flash("Você não tem permissão para registrar presenças.", "danger")
        return redirect(url_for("atividades.listar"))

    atividade = Atividade.query.get_or_404(atividade_id)

    # Atletas vinculados ao grupo da atividade
    atletas_ids = [
        ag.atleta_id
        for ag in AtletaGrupo.query.filter_by(grupo_id=atividade.grupo_id, ativo=True)
    ]
    atletas = (
        Atleta.query.filter(Atleta.id.in_(atletas_ids)).order_by(Atleta.nome).all()
        if atletas_ids
        else []
    )

    if request.method == "POST":
        # Remove presenças antigas para recriar o registro do dia
        Presenca.query.filter_by(atividade_id=atividade.id).delete()

        for atleta in atletas:
            status = request.form.get(f"status_{atleta.id}")
            obs = request.form.get(f"observacao_{atleta.id}")
            if not status:
                continue
            p = Presenca(
                atividade_id=atividade.id,
                atleta_id=atleta.id,
                status=status,
                observacao=(obs or "").strip() or None,
            )
            db.session.add(p)

        db.session.commit()
        flash("Presenças registradas com sucesso!", "success")
        return redirect(url_for("atividades.listar"))

    presencas_existentes = {
        p.atleta_id: p for p in Presenca.query.filter_by(atividade_id=atividade.id).all()
    }

    return render_template(
        "atividades_presencas.html",
        atividade=atividade,
        atletas=atletas,
        presencas=presencas_existentes,
    )
