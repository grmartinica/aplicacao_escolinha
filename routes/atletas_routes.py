# routes/atletas_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date

from extensions import db
from models import Atleta, Grupo, Plano, AtletaGrupo, AtletaPlano

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


@atletas_bp.route('/listar')
@login_required
def listar():
    """
    Lista de atletas com filtros:
    - nome (contém)
    - idade mínima / máxima
    - status (ATIVO / INATIVO / TODOS)
    """
    nome = (request.args.get('nome') or '').strip()
    idade_min = request.args.get('idade_min', type=int)
    idade_max = request.args.get('idade_max', type=int)
    status = request.args.get('status') or 'TODOS'

    query = Atleta.query

    if status in ('ATIVO', 'INATIVO'):
        query = query.filter(Atleta.status == status)

    if nome:
        query = query.filter(Atleta.nome.ilike(f'%{nome}%'))

    hoje = date.today()

    # filtro por idade -> convertemos idade para intervalo de datas
    if idade_min is not None:
        ano_max = hoje.year - idade_min
        data_max = date(ano_max, 12, 31)
        query = query.filter(Atleta.data_nascimento <= data_max)

    if idade_max is not None:
        ano_min = hoje.year - idade_max
        data_min = date(ano_min, 1, 1)
        query = query.filter(Atleta.data_nascimento >= data_min)

    atletas = query.order_by(Atleta.nome).all()

    # calcula idade em Python e anexa no objeto
    for a in atletas:
        if a.data_nascimento:
            idade = hoje.year - a.data_nascimento.year
            if (hoje.month, hoje.day) < (a.data_nascimento.month, a.data_nascimento.day):
                idade -= 1
            a.idade = idade
        else:
            a.idade = None

    filtros = {
        'nome': nome,
        'idade_min': idade_min if idade_min is not None else '',
        'idade_max': idade_max if idade_max is not None else '',
        'status': status,
    }

    return render_template('atletas_listar.html', atletas=atletas, filtros=filtros)


@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    grupos = Grupo.query.order_by(Grupo.nome).all()
    planos = Plano.query.order_by(Plano.nome).all()

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None
        rg = (request.form.get('rg') or '').strip() or None
        cpf = (request.form.get('cpf') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None
        validade_atestado = request.form.get('validade_atestado') or None
        info_adicionais = (request.form.get('informacoes_adicionais') or '').strip() or None

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.novo'))

        atleta = Atleta(
            nome=nome,
            data_nascimento=datetime.strptime(dn, '%Y-%m-%d').date(),
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
        db.session.flush()  # para pegar atleta.id

        # vínculos com grupos
        grupos_ids = request.form.getlist('grupos_ids')
        for gid in grupos_ids:
            if gid:
                db.session.add(AtletaGrupo(atleta_id=atleta.id, grupo_id=int(gid), ativo=True))

        # vínculo com plano
        plano_id = request.form.get('plano_id', type=int)
        if plano_id:
            db.session.add(AtletaPlano(atleta_id=atleta.id, plano_id=plano_id, ativo=True))

        db.session.commit()
        flash('Atleta cadastrado com sucesso!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', atleta=None, grupos=grupos, planos=planos)


@atletas_bp.route('/<int:atleta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)
    grupos = Grupo.query.order_by(Grupo.nome).all()
    planos = Plano.query.order_by(Plano.nome).all()

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

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

        atleta.nome = nome
        atleta.data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
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
        grupos_ids = request.form.getlist('grupos_ids')
        for gid in grupos_ids:
            if gid:
                db.session.add(AtletaGrupo(atleta_id=atleta.id, grupo_id=int(gid), ativo=True))

        # atualiza plano (mantendo um plano ativo só para simplificar)
        AtletaPlano.query.filter_by(atleta_id=atleta.id).delete()
        plano_id = request.form.get('plano_id', type=int)
        if plano_id:
            db.session.add(AtletaPlano(atleta_id=atleta.id, plano_id=plano_id, ativo=True))

        db.session.commit()
        flash('Dados do atleta atualizados!', 'success')
        return redirect(url_for('atletas.listar'))

    # pré-seleção de grupos e plano
    grupos_ids_do_atleta = {ag.grupo_id for ag in atleta.grupos}
    plano_atual = atleta.planos[0].plano_id if atleta.planos else None

    return render_template(
        'atletas_novo.html',
        atleta=atleta,
        grupos=grupos,
        planos=planos,
        grupos_ids_do_atleta=grupos_ids_do_atleta,
        plano_atual=plano_atual
    )
