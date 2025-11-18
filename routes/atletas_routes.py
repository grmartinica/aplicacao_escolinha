from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Atleta
from datetime import datetime

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


@atletas_bp.route('/listar')
@login_required
def listar():
    atletas = Atleta.query.order_by(Atleta.nome).all()
    return render_template('atletas_listar.html', atletas=atletas)


@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None
        documento = (request.form.get('documento') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.novo'))

        atleta = Atleta(
            nome=nome,
            data_nascimento=datetime.strptime(dn, '%Y-%m-%d').date(),
            posicao=posicao,
            documento=documento,
            telefone_residencial=telefone,
            status='ATIVO'
        )
        db.session.add(atleta)
        db.session.commit()
        flash('Atleta cadastrado com sucesso!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', atleta=None)


@atletas_bp.route('/<int:atleta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None
        documento = (request.form.get('documento') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None
        status = request.form.get('status') or 'ATIVO'

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

        atleta.nome = nome
        atleta.data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
        atleta.posicao = posicao
        atleta.documento = documento
        atleta.telefone_residencial = telefone
        atleta.status = status

        db.session.commit()
        flash('Dados do atleta atualizados!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', atleta=atleta)
