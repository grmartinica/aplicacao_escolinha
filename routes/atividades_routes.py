from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Atividade, Grupo, Presenca, AtletaGrupo
from datetime import datetime, date
import calendar

atividades_bp = Blueprint('atividades', __name__, url_prefix='/atividades')


@atividades_bp.route('/listar')
@login_required
def listar():
    hoje = date.today()
    ano = request.args.get('ano', type=int) or hoje.year
    mes = request.args.get('mes', type=int) or hoje.month

    first_day = date(ano, mes, 1)
    last_day = date(ano, mes, calendar.monthrange(ano, mes)[1])

    atividades = Atividade.query \
        .filter(Atividade.data >= first_day, Atividade.data <= last_day) \
        .order_by(Atividade.data.asc(), Atividade.hora_inicio.asc()) \
        .all()

    atividades_por_dia = {}
    for a in atividades:
        dia = a.data.day
        atividades_por_dia.setdefault(dia, []).append(a)

    first_weekday, num_days = calendar.monthrange(ano, mes)  # first_weekday: 0 = segunda

    # Cálculo do mês anterior / próximo
    if mes == 1:
        prev_mes, prev_ano = 12, ano - 1
    else:
        prev_mes, prev_ano = mes - 1, ano

    if mes == 12:
        next_mes, next_ano = 1, ano + 1
    else:
        next_mes, next_ano = mes + 1, ano

    return render_template(
        'atividades_listar.html',
        ano=ano,
        mes=mes,
        num_days=num_days,
        first_weekday=first_weekday,
        atividades_por_dia=atividades_por_dia,
        prev_mes=prev_mes,
        prev_ano=prev_ano,
        next_mes=next_mes,
        next_ano=next_ano
    )


@atividades_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    grupos = Grupo.query.order_by(Grupo.nome).all()
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        grupo_id = request.form.get('grupo_id', type=int)
        data = request.form.get('data')
        hora_inicio = request.form.get('hora_inicio')
        if not all([titulo, grupo_id, data, hora_inicio]):
            flash('Preencha título, grupo, data e hora inicial.', 'danger')
            return redirect(url_for('atividades.nova'))
        atividade = Atividade(
            titulo=titulo,
            grupo_id=grupo_id,
            coach_id=current_user.id,
            data=datetime.strptime(data, '%Y-%m-%d').date(),
            hora_inicio=datetime.strptime(hora_inicio, '%H:%M').time(),
            local=request.form.get('local') or None,
            descricao=request.form.get('descricao') or None
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
    from models import Atleta
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

    presencas_existentes = {p.atleta_id: p for p in Presenca.query.filter_by(atividade_id=atividade.id).all()}

    return render_template(
        'atividades_presencas.html',
        atividade=atividade,
        atletas=atletas,
        presencas=presencas_existentes
    )
