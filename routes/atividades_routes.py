from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Atividade, Grupo
from datetime import datetime

atividades_bp = Blueprint('atividades', __name__, url_prefix='/atividades')

@atividades_bp.route('/listar')
@login_required
def listar():
    atividades = Atividade.query.order_by(Atividade.data.desc(), Atividade.hora_inicio.desc()).all()
    return render_template('atividades_listar.html', atividades=atividades)

@atividades_bp.route('/nova', methods=['GET','POST'])
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
