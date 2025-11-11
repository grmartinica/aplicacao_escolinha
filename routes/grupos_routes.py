from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import Grupo

grupos_bp = Blueprint('grupos', __name__, url_prefix='/grupos')

@grupos_bp.route('/')
def listar():
    grupos = Grupo.query.all()
    return render_template('grupos_listar.html', grupos=grupos)

@grupos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form['nome']
        min_idade = request.form.get['faixa_etaria_min']
        max_idade = request.form.get['faixa_etaria_max']
        grupo = Grupo(nome=nome, faixa_etaria_min=min_idade, faixa_etaria_max=max_idade)
        db.session.add(grupo)
        db.session.commit()
        flash('Grupo criado com sucesso!', 'success')
        return redirect(url_for('grupos.listar'))
    return render_template('grupos_novo.html')