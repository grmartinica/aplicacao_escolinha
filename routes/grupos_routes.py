from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db
from models import Grupo, Atleta, AtletaGrupo
from datetime import date

grupos_bp = Blueprint('grupos', __name__, url_prefix='/grupos')


@grupos_bp.route('/')
@login_required
def listar():
    grupos = Grupo.query.all()
    return render_template('grupos_listar.html', grupos=grupos)


@grupos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        min_idade = request.form.get('faixa_etaria_min', type=int)
        max_idade = request.form.get('faixa_etaria_max', type=int)

        if not nome:
            flash('Informe o nome do grupo.', 'danger')
            return redirect(url_for('grupos.novo'))

        grupo = Grupo(
            nome=nome,
            faixa_etaria_min=min_idade,
            faixa_etaria_max=max_idade
        )
        db.session.add(grupo)
        db.session.commit()
        flash('Grupo criado com sucesso!', 'success')
        return redirect(url_for('grupos.listar'))

    return render_template('grupos_novo.html')


@grupos_bp.route('/<int:grupo_id>/gerenciar', methods=['GET', 'POST'])
@login_required
def gerenciar(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)

    if request.method == 'POST':
        # adicionar/remover atletas via checkboxes
        atletas_ids = request.form.getlist('atletas_ids')
        # zera relações atuais
        AtletaGrupo.query.filter_by(grupo_id=grupo.id).delete()
        for aid in atletas_ids:
            ag = AtletaGrupo(atleta_id=int(aid), grupo_id=grupo.id, ativo=True)
            db.session.add(ag)
        db.session.commit()
        flash('Grupo atualizado com sucesso!', 'success')
        return redirect(url_for('grupos.gerenciar', grupo_id=grupo.id))

    # filtros
    nome = (request.args.get('nome') or '').strip()
    idade_min = request.args.get('idade_min', type=int)
    idade_max = request.args.get('idade_max', type=int)

    query = Atleta.query.filter_by(status='ATIVO')

    hoje = date.today()
    if idade_min is not None:
        ano_max = hoje.year - idade_min
        query = query.filter(Atleta.data_nascimento <= date(ano_max, 12, 31))
    if idade_max is not None:
        ano_min = hoje.year - idade_max
        query = query.filter(Atleta.data_nascimento >= date(ano_min, 1, 1))
    if nome:
        query = query.filter(Atleta.nome.ilike(f'%{nome}%'))

    atletas = query.order_by(Atleta.nome).all()
    atletas_do_grupo = {ag.atleta_id for ag in grupo.atletas}

    return render_template(
        'grupos_gerenciar.html',
        grupo=grupo,
        atletas=atletas,
        atletas_do_grupo=atletas_do_grupo
    )