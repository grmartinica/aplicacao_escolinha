from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Plano

planos_bp = Blueprint('planos', __name__, url_prefix='/planos')


@planos_bp.route('/')
@login_required
def listar():
    planos = Plano.query.order_by(Plano.nome).all()
    return render_template('planos_listar.html', planos=planos)


@planos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        valor = request.form.get('valor', type=float)
        dia_venc = request.form.get('dia_vencimento', type=int)
        forma = request.form.get('forma_pagamento_padrao')
        periodicidade = request.form.get('periodicidade')
        descricao = request.form.get('descricao')

        if not nome or not valor or not dia_venc:
            flash('Preencha nome, valor e dia de vencimento.', 'danger')
            return redirect(url_for('planos.novo'))

        plano = Plano(
            nome=nome,
            valor_mensal=valor,
            dia_vencimento=dia_venc,
            forma_pagamento_padrao=forma or 'PIX',
            periodicidade=periodicidade or 'MENSAL',
            descricao=descricao or None
        )
        db.session.add(plano)
        db.session.commit()
        flash('Plano cadastrado com sucesso!', 'success')
        return redirect(url_for('planos.listar'))

    return render_template('planos_novo.html')


@planos_bp.route('/<int:plano_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(plano_id):
    plano = Plano.query.get_or_404(plano_id)

    if request.method == 'POST':
        plano.nome = request.form.get('nome')
        plano.valor_mensal = request.form.get('valor', type=float)
        plano.dia_vencimento = request.form.get('dia_vencimento', type=int)
        plano.forma_pagamento_padrao = request.form.get('forma_pagamento_padrao') or 'PIX'
        plano.periodicidade = request.form.get('periodicidade') or 'MENSAL'
        plano.descricao = request.form.get('descricao') or None
        plano.ativo = bool(request.form.get('ativo'))

        db.session.commit()
        flash('Plano atualizado com sucesso!', 'success')
        return redirect(url_for('planos.listar'))

    return render_template('planos_editar.html', plano=plano)