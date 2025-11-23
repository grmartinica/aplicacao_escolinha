# routes/atividades_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from calendar import Calendar

from extensions import db
from models import Atividade, Grupo, Presenca, AtletaGrupo, Atleta

atividades_bp = Blueprint('atividades', __name__, url_prefix='/atividades')


@atividades_bp.route('/listar')
@login_required
def listar():
    # mês/ano atuais ou vindos por querystring
    hoje = date.today()
    ano = request.args.get('ano', type=int) or hoje.year
    mes = request.args.get('mes', type=int) or hoje.month

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    atividades_mes = Atividade.query.filter(
        Atividade.data >= primeiro_dia,
        Atividade.data <= ultimo_dia
    ).order_by(Atividade.data, Atividade.hora_inicio).all()

    eventos_por_dia = {}
    for a in atividades_mes:
        dia = a.data.day
        eventos_por_dia.setdefault(dia, []).append(a)

    cal = Calendar(firstweekday=0)  # 0 = segunda
    semanas = cal.monthdayscalendar(ano, mes)  # lista de semanas com 7 dias (0 = vazio)

    return render_template(
        'atividades_listar.html',
        ano=ano,
        mes=mes,
        semanas=semanas,
        eventos_por_dia=eventos_por_dia
    )


@atividades_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    grupos = Grupo.query.order_by(Grupo.nome).all()

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        grupo_id = request.form.get('grupo_id', type=int)
        data_str = request.form.get('data')
        hora_inicio_str = request.form.get('hora_inicio')
        local = request.form.get('local') or None
        descricao = request.form.get('descricao') or None

        repetir = request.form.get('repetir') == 'on'
        repeticoes = request.form.get('repeticoes', type=int) or 1  # número de semanas

        if not all([titulo, grupo_id, data_str, hora_inicio_str]):
            flash('Preencha título, grupo, data e hora inicial.', 'danger')
            return redirect(url_for('atividades.nova'))

        data_base = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()

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
                descricao=descricao
            )
            db.session.add(atividade)
        db.session.commit()

        flash('Atividade criada!', 'success')
        return redirect(url_for('atividades.listar'))

    return render_template('atividades_nova.html', grupos=grupos)


@atividades_bp.route('/<int:atividade_id>/presencas', methods=['GET', 'POST'])
@login_required
def presencas(atividade_id):
    atividade = Atividade.query.get_or_404(atividade_id)
    atletas_ids = [ag.atleta_id for ag in AtletaGrupo.query.filter_by(grupo_id=atividade.grupo_id, ativo=True)]
    atletas = Atleta.query.filter(Atleta.id.in_(atletas_ids)).order_by(Atleta.nome).all()

    if request.method == 'POST':
        Presenca.query.filter_by(atividade_id=atividade.id).delete()

        for atleta in atletas:
            status = request.form.get(f'status_{atleta.id}')
            obs = request.form.get(f'observacao_{atleta.id}')
            if not status:
                continue
            p = Presenca(
                atividade_id=atividade.id,
                atleta_id=atleta.id,
                status=status,
                observacao=obs or None
            )
            db.session.add(p)
        db.session.commit()
        flash('Presenças registradas com sucesso!', 'success')
        return redirect(url_for('atividades.listar'))

    presencas_existentes = {
        p.atleta_id: p for p in Presenca.query.filter_by(atividade_id=atividade.id).all()
    }

    return render_template(
        'atividades_presencas.html',
        atividade=atividade,
        atletas=atletas,
        presencas=presencas_existentes
    )
