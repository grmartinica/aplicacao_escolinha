from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import Atividade, Grupo

atividade_bp = Blueprint('atividades', __name__, url_prefix='/atividades')

@atividade_bp.route('/')
def listar():
    atividades = Atividade.query.all()
    return render_template('atividades_listar.html', atividades=atividades)

@atividade_bp.route('/novo', methods=['GET', 'POST'])
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