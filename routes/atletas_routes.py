from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Atleta
from datetime import datetime, date

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


@atletas_bp.route('/listar')
@login_required
def listar():
    """
    Lista atletas com filtros:
    - nome (contém)
    - status (ATIVO / INATIVO / todos)
    - idade_min / idade_max (em anos)
    """
    nome = (request.args.get('nome') or '').strip()
    status = (request.args.get('status') or '').strip()
    idade_min = request.args.get('idade_min', type=int)
    idade_max = request.args.get('idade_max', type=int)

    query = Atleta.query

    if nome:
        query = query.filter(Atleta.nome.ilike(f'%{nome}%'))

    if status in ('ATIVO', 'INATIVO'):
        query = query.filter(Atleta.status == status)

    hoje = date.today()

    # idade_min = pelo menos X anos (mais velho)
    if idade_min is not None:
        ano_max = hoje.year - idade_min
        query = query.filter(Atleta.data_nascimento <= date(ano_max, 12, 31))

    # idade_max = no máximo X anos (mais novo)
    if idade_max is not None:
        ano_min = hoje.year - idade_max
        query = query.filter(Atleta.data_nascimento >= date(ano_min, 1, 1))

    atletas = query.order_by(Atleta.nome).all()

    filtros = {
        'nome': nome,
        'status': status,
        'idade_min': idade_min if idade_min is not None else '',
        'idade_max': idade_max if idade_max is not None else '',
    }

    return render_template('atletas_listar.html', atletas=atletas, filtros=filtros)


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
