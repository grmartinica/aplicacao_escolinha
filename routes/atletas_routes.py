from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date

from extensions import db
from models import (
    Atleta,
    Grupo,
    AtletaGrupo,
    Plano,
    AtletaPlano
)

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


# LISTAR + FILTROS
@atletas_bp.route('/listar')
@login_required
def listar():
    nome = (request.args.get('nome') or '').strip()
    status = (request.args.get('status') or '').strip()
    idade_min = request.args.get('idade_min', type=int)
    idade_max = request.args.get('idade_max', type=int)

    query = Atleta.query

    if nome:
        query = query.filter(Atleta.nome.ilike(f'%{nome}%'))

    if status in ('ATIVO', 'INATIVO'):
        query = query.filter(Atleta.status == status)

    # filtro de idade (aprox) -> converte idade em faixa de datas
    hoje = date.today()
    if idade_min is not None:
        ano_max = hoje.year - idade_min
        query = query.filter(Atleta.data_nascimento <= date(ano_max, 12, 31))
    if idade_max is not None:
        ano_min = hoje.year - idade_max
        query = query.filter(Atleta.data_nascimento >= date(ano_min, 1, 1))

    atletas = query.order_by(Atleta.nome).all()

    filtros = {
        'nome': nome,
        'status': status,
        'idade_min': idade_min or '',
        'idade_max': idade_max or ''
    }

    return render_template('atletas_listar.html', atletas=atletas, filtros=filtros)


# NOVO ATLETA
@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    grupos = Grupo.query.order_by(Grupo.nome).all()
    planos = Plano.query.filter_by(ativo=True).order_by(Plano.nome).all()

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None

        rg = (request.form.get('rg') or '').strip() or None
        cpf = (request.form.get('cpf') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None
        validade_atestado = request.form.get('validade_atestado') or None
        info_adicionais = (request.form.get('informacoes_adicionais') or '').strip() or None

        plano_id = request.form.get('plano_id', type=int)
        grupo_ids = request.form.getlist('grupo_ids')

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.novo'))

        try:
            data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
        except ValueError:
            flash('Data de nascimento inválida.', 'danger')
            return redirect(url_for('atletas.novo'))

        atleta = Atleta(
            nome=nome,
            data_nascimento=data_nascimento,
            posicao=posicao,
            rg=rg,
            cpf=cpf,
            telefone=telefone,
            validade_atestado=datetime.strptime(validade_atestado, '%Y-%m-%d').date()
            if validade_atestado else None,
            informacoes_adicionais=info_adicionais,
            status='ATIVO'
        )

        db.session.add(atleta)
        db.session.flush()  # pega o ID

        # vincula grupos
        for gid in grupo_ids:
            db.session.add(AtletaGrupo(atleta_id=atleta.id, grupo_id=int(gid), ativo=True))

        # vincula plano (um ativo por enquanto)
        if plano_id:
            db.session.add(AtletaPlano(atleta_id=atleta.id, plano_id=plano_id, ativo=True))

        db.session.commit()
        flash('Atleta cadastrado com sucesso!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template(
        'atletas_novo.html',
        atleta=None,
        grupos=grupos,
        grupos_do_atleta=set(),
        planos=planos,
        plano_atual_id=None
    )


# EDITAR ATLETA
@atletas_bp.route('/<int:atleta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)
    grupos = Grupo.query.order_by(Grupo.nome).all()
    planos = Plano.query.filter_by(ativo=True).order_by(Plano.nome).all()

    grupos_do_atleta = {ag.grupo_id for ag in atleta.grupos}
    plano_atual = next((ap for ap in atleta.planos if ap.ativo), None)
    plano_atual_id = plano_atual.plano_id if plano_atual else None

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None

        rg = (request.form.get('rg') or '').strip() or None
        cpf = (request.form.get('cpf') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None
        validade_atestado = request.form.get('validade_atestado') or None
        info_adicionais = (request.form.get('informacoes_adicionais') or '').strip() or None

        status = request.form.get('status') or 'ATIVO'
        plano_id = request.form.get('plano_id', type=int)
        grupo_ids = request.form.getlist('grupo_ids')

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

        atleta.nome = nome
        try:
            atleta.data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
        except ValueError:
            flash('Data de nascimento inválida.', 'danger')
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

        atleta.posicao = posicao
        atleta.rg = rg
        atleta.cpf = cpf
        atleta.telefone = telefone
        atleta.validade_atestado = datetime.strptime(validade_atestado, '%Y-%m-%d').date() \
            if validade_atestado else None
        atleta.informacoes_adicionais = info_adicionais
        atleta.status = status

        # atualiza grupos
        AtletaGrupo.query.filter_by(atleta_id=atleta.id).delete()
        for gid in grupo_ids:
            db.session.add(AtletaGrupo(atleta_id=atleta.id, grupo_id=int(gid), ativo=True))

        # atualiza plano (mantém histórico simples)
        for ap in atleta.planos:
            ap.ativo = False
        if plano_id:
            db.session.add(AtletaPlano(atleta_id=atleta.id, plano_id=plano_id, ativo=True))

        db.session.commit()
        flash('Dados do atleta atualizados!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template(
        'atletas_novo.html',
        atleta=atleta,
        grupos=grupos,
        grupos_do_atleta=grupos_do_atleta,
        planos=planos,
        plano_atual_id=plano_atual_id
    )
