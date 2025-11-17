from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Atleta, Responsavel, AtletaResponsavel, AtletaFoto, AtletaGrupo, AtletaPlano, Plano, Grupo
from datetime import datetime
import os

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@atletas_bp.route('/listar')
@login_required
def listar():
    atletas = Atleta.query.order_by(Atleta.nome).all()
    return render_template('atletas_listar.html', atletas=atletas)


@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    planos = Plano.query.filter_by(ativo=True).order_by(Plano.nome).all()
    grupos = Grupo.query.order_by(Grupo.nome).all()

    if request.method == 'POST':
        # Dados do atleta
        nome = request.form.get('nome')
        dn = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        rg = request.form.get('rg')
        cpf = request.form.get('cpf')
        validade_atestado = request.form.get('validade_atestado')
        informacoes = request.form.get('informacoes_adicionais')

        if not nome or not dn:
            flash('Preencha nome e data de nascimento', 'danger')
            return redirect(url_for('atletas.novo'))

        atleta = Atleta(
            nome=nome,
            data_nascimento=datetime.strptime(dn, '%Y-%m-%d').date(),
            telefone=telefone or None,
            rg=rg or None,
            cpf=cpf or None,
            validade_atestado=datetime.strptime(validade_atestado, '%Y-%m-%d').date()
            if validade_atestado else None,
            informacoes_adicionais=informacoes or None,
            status='ATIVO'
        )
        db.session.add(atleta)
        db.session.flush()  # pega id

        # Responsável (mínimo: nome + CPF)
        nome_resp = request.form.get('nome_responsavel')
        cpf_resp = request.form.get('cpf_responsavel')
        tel_resp = request.form.get('telefone_responsavel')
        cep = request.form.get('cep')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')

        if nome_resp and cpf_resp:
            resp = Responsavel(
                nome=nome_resp,
                cpf=cpf_resp,
                telefone=tel_resp,
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                estado=estado
            )
            db.session.add(resp)
            db.session.flush()

            link = AtletaResponsavel(
                atleta_id=atleta.id,
                responsavel_id=resp.id,
                parentesco=request.form.get('parentesco') or None
            )
            db.session.add(link)

        # Plano do atleta
        plano_id = request.form.get('plano_id', type=int)
        if plano_id:
            ap = AtletaPlano(
                atleta_id=atleta.id,
                plano_id=plano_id,
                ativo=True
            )
            db.session.add(ap)

        # Grupos selecionados
        grupos_ids = request.form.getlist('grupos_ids')
        for gid in grupos_ids:
            ag = AtletaGrupo(atleta_id=atleta.id, grupo_id=int(gid), ativo=True)
            db.session.add(ag)

        # Foto (upload)
        foto = request.files.get('foto')
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            path_fs = os.path.join(upload_folder, filename)
            foto.save(path_fs)

            # caminho relativo pra servir no template, ex: /static/uploads/atletas/filename
            rel_path = os.path.join('static', 'uploads', 'atletas', filename)
            af = AtletaFoto(
                atleta_id=atleta.id,
                foto_path=rel_path
            )
            db.session.add(af)

        db.session.commit()
        flash('Atleta cadastrado!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', planos=planos, grupos=grupos)


@atletas_bp.route('/<int:atleta_id>/inativar', methods=['POST'])
@login_required
def inativar(atleta_id):
    atleta = Atleta.query.get_or_404(atleta_id)
    atleta.status = 'INATIVO'
    # opcional: desativar planos/relacionamentos
    for ap in atleta.planos:
        ap.ativo = False
    db.session.commit()
    flash('Atleta inativado. Não serão geradas novas cobranças.', 'info')
    return redirect(url_for('atletas.listar'))