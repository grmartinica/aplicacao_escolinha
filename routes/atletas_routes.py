from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import and_

from extensions import db
from models import Atleta, Plano, Grupo, AtletaGrupo, AtletaPlano

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


def _aplicar_filtros(query):
    """Aplica filtros de nome, idade e status na listagem de atletas."""
    nome = (request.args.get('nome') or '').strip()
    idade = request.args.get('idade', type=int)
    status = (request.args.get('status') or '').strip()

    if nome:
        query = query.filter(Atleta.nome.ilike(f"%{nome}%"))

    if status:
        query = query.filter(Atleta.status == status)

    # Idade aproximada: filtra pelo ano de nascimento
    if idade is not None:
        hoje = date.today()
        ano_nascimento = hoje.year - idade
        query = query.filter(
            and_(
                db.extract('year', Atleta.data_nascimento) == ano_nascimento
            )
        )

    return query


@atletas_bp.route('/listar')
@login_required
def listar():
    query = Atleta.query.order_by(Atleta.nome)
    query = _aplicar_filtros(query)
    atletas = query.all()

    # para manter os filtros na tela
    filtros = {
        "nome": (request.args.get('nome') or '').strip(),
        "idade": request.args.get('idade') or '',
        "status": (request.args.get('status') or '').strip()
    }

    return render_template('atletas_listar.html', atletas=atletas, filtros=filtros)


@atletas_bp.route('/<int:atleta_id>')
@login_required
def detalhe(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)

    plano_ativo = (
        AtletaPlano.query
        .filter_by(atleta_id=atleta.id, ativo=True)
        .first()
    )

    grupos = (
        db.session.query(Grupo)
        .join(AtletaGrupo, AtletaGrupo.grupo_id == Grupo.id)
        .filter(AtletaGrupo.atleta_id == atleta.id, AtletaGrupo.ativo == True)
        .all()
    )

    return render_template(
        'atletas_detalhe.html',
        atleta=atleta,
        plano_ativo=plano_ativo.plano if plano_ativo else None,
        grupos=grupos
    )


@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    planos = Plano.query.filter_by(ativo=True).order_by(Plano.nome).all()
    grupos = Grupo.query.order_by(Grupo.nome).all()

    if request.method == 'POST':
        return _salvar_atleta()

    return render_template(
        'atletas_novo.html',
        atleta=None,
        planos=planos,
        grupos=grupos
    )


@atletas_bp.route('/<int:atleta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)
    planos = Plano.query.filter_by(ativo=True).order_by(Plano.nome).all()
    grupos = Grupo.query.order_by(Grupo.nome).all()

    plano_ativo = (
        AtletaPlano.query
        .filter_by(atleta_id=atleta.id, ativo=True)
        .first()
    )
    plano_id_atual = plano_ativo.plano_id if plano_ativo else None

    grupos_ids_atuais = {
        ag.grupo_id for ag in AtletaGrupo.query.filter_by(atleta_id=atleta.id, ativo=True)
    }

    if request.method == 'POST':
        return _salvar_atleta(atleta=atleta)

    return render_template(
        'atletas_novo.html',
        atleta=atleta,
        planos=planos,
        grupos=grupos,
        plano_id_atual=plano_id_atual,
        grupos_ids_atuais=grupos_ids_atuais
    )


def _salvar_atleta(atleta=None):
    """Cria ou atualiza um atleta com todos os novos campos."""
    is_new = atleta is None

    nome = (request.form.get('nome') or '').strip()
    dn = request.form.get('data_nascimento')
    posicao = (request.form.get('posicao') or '').strip() or None

    # documento
    rg = (request.form.get('rg') or '').strip() or None
    cpf = (request.form.get('cpf') or '').strip() or None

    # endereço
    cep = (request.form.get('cep') or '').strip() or None
    logradouro = (request.form.get('logradouro') or '').strip() or None
    numero = (request.form.get('numero') or '').strip() or None
    complemento = (request.form.get('complemento') or '').strip() or None
    bairro = (request.form.get('bairro') or '').strip() or None
    cidade = (request.form.get('cidade') or '').strip() or None
    estado = (request.form.get('estado') or '').strip() or None

    validade_atestado_str = request.form.get('validade_atestado') or None

    # documentos entregues (checkbox)
    doc_rg_ok = bool(request.form.get('doc_rg_ok'))
    doc_cpf_ok = bool(request.form.get('doc_cpf_ok'))
    doc_comprov_endereco_ok = bool(request.form.get('doc_comprov_endereco_ok'))
    doc_decl_escolar_ok = bool(request.form.get('doc_decl_escolar_ok'))
    doc_atestado_medico_ok = bool(request.form.get('doc_atestado_medico_ok'))

    # responsável
    responsavel_nome = (request.form.get('responsavel_nome') or '').strip() or None
    responsavel_cpf = (request.form.get('responsavel_cpf') or '').strip() or None
    responsavel_telefone = (request.form.get('responsavel_telefone') or '').strip() or None

    plano_id = request.form.get('plano_id', type=int)
    grupos_ids = [int(gid) for gid in request.form.getlist('grupos_ids')]

    status = request.form.get('status') or 'ATIVO'

    if not nome or not dn:
        flash('Preencha nome e data de nascimento.', 'danger')
        if is_new:
            return redirect(url_for('atletas.novo'))
        else:
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

    try:
        data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
    except ValueError:
        flash('Data de nascimento inválida.', 'danger')
        if is_new:
            return redirect(url_for('atletas.novo'))
        else:
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

    validade_atestado = None
    if validade_atestado_str:
        try:
            validade_atestado = datetime.strptime(validade_atestado_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Validade do atestado inválida.', 'danger')

    if is_new:
        atleta = Atleta(
            nome=nome,
            data_nascimento=data_nascimento,
            posicao=posicao,
            status='ATIVO'
        )
        db.session.add(atleta)

    atleta.nome = nome
    atleta.data_nascimento = data_nascimento
    atleta.posicao = posicao
    atleta.rg = rg
    atleta.cpf = cpf
    atleta.cep = cep
    atleta.logradouro = logradouro
    atleta.numero = numero
    atleta.complemento = complemento
    atleta.bairro = bairro
    atleta.cidade = cidade
    atleta.estado = estado
    atleta.validade_atestado = validade_atestado

    atleta.doc_rg_ok = doc_rg_ok
    atleta.doc_cpf_ok = doc_cpf_ok
    atleta.doc_comprov_endereco_ok = doc_comprov_endereco_ok
    atleta.doc_decl_escolar_ok = doc_decl_escolar_ok
    atleta.doc_atestado_medico_ok = doc_atestado_medico_ok

    atleta.responsavel_nome = responsavel_nome
    atleta.responsavel_cpf = responsavel_cpf
    atleta.responsavel_telefone = responsavel_telefone

    if not is_new:
        atleta.status = status

    db.session.flush()  # garante atleta.id

    # ---- plano (AtletaPlano) ----
    AtletaPlano.query.filter_by(atleta_id=atleta.id).update({"ativo": False})
    if plano_id:
        ap = AtletaPlano(
            atleta_id=atleta.id,
            plano_id=plano_id,
            ativo=True,
            data_inicio=date.today()
        )
        db.session.add(ap)

    # ---- grupos (AtletaGrupo) ----
    AtletaGrupo.query.filter_by(atleta_id=atleta.id).delete()
    for gid in grupos_ids:
        ag = AtletaGrupo(atleta_id=atleta.id, grupo_id=gid, ativo=True)
        db.session.add(ag)

    db.session.commit()

    flash('Atleta salvo com sucesso!', 'success')
    return redirect(url_for('atletas.listar'))
