from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db
from models import Atividade, Grupo

atividades_bp = Blueprint('atividades', __name__, url_prefix='/atividades')

@atividades_bp.route('/')
def listar():
    atividades = Atividade.query.all()
    return render_template('atividades_listar.html', atividades=atividades)

@atividades_bp.route('/novo', methods=['GET', 'POST'])
def nova():
    grupos = Grupo.query.all()
    if request.method == 'POST':
        atividade = Atividade (
            titulo=request.form['titulo'],
            grupo_id=request.form['grupo_id'],
            data=request.form['data'],
            hora_inicio=request.form['hora_inicio'],
            hora_fim=request.form['hora_fim'],
            local=request.form['local']
        )
        db.session.add(atividade)
        db.session.commit()
        flash('Atividade criada com sucesso!', 'success')
        return redirect(url_for('atividades.listar'))
    return render_template('atividades_nova.html', grupos=grupos)