from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Plano

planos_bp = Blueprint('planos', __name__, url_prefix='/planos')


@planos_bp.route('/')
@login_required
def listar():
    planos = Plano.query.order_by(Plano.ativo.desc(), Plano.nome).all()
    return render_template('planos_listar.html', planos=planos)


@planos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        valor = request.form.get('valor_mensal', type=float)
        descricao = (request.form.get('descricao') or '').strip()

        if not nome or valor is None:
            flash('Informe ao menos nome e valor mensal do plano.', 'danger')
            return redirect(url_for('planos.novo'))

        plano = Plano(
            nome=nome,
            valor_mensal=valor,
            descricao=descricao or None,
            ativo=True
        )
        db.session.add(plano)
        db.session.commit()
        flash('Plano criado com sucesso!', 'success')
        return redirect(url_for('planos.listar'))

    return render_template('planos_novo.html')


@planos_bp.route('/<int:plano_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(plano_id):
    plano = Plano.query.get_or_404(plano_id)

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        valor = request.form.get('valor_mensal', type=float)
        descricao = (request.form.get('descricao') or '').strip()
        ativo = True if request.form.get('ativo') == 'on' else False

        if not nome or valor is None:
            flash('Informe ao menos nome e valor mensal do plano.', 'danger')
            return redirect(url_for('planos.editar', plano_id=plano.id))

        plano.nome = nome
        plano.valor_mensal = valor
        plano.descricao = descricao or None
        plano.ativo = ativo

        db.session.commit()
        flash('Plano atualizado com sucesso!', 'success')
        return redirect(url_for('planos.listar'))

    return render_template('planos_editar.html', plano=plano)
