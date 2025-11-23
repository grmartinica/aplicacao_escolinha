from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from extensions import db
from models import Atleta, AtletaFoto
from datetime import datetime
import os
import base64

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


def salvar_foto_base64(atleta, foto_base64):
    """
    Recebe o atleta e a string base64 vinda do form (data:image/jpeg;base64,...),
    salva em static/uploads/atletas e cria/atualiza o registro em AtletaFoto.
    """
    if not foto_base64:
        return

    # foto_base64 vem como 'data:image/jpeg;base64,AAAAA...'
    if ',' in foto_base64:
        header, b64data = foto_base64.split(',', 1)
    else:
        b64data = foto_base64

    try:
        img_bytes = base64.b64decode(b64data)
    except Exception:
        # base64 inválido, não faz nada
        return

    # pasta de destino
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'atletas')
    os.makedirs(upload_dir, exist_ok=True)

    # nome do arquivo (ex: atleta_3.jpg)
    filename = f'atleta_{atleta.id}.jpg'
    filepath = os.path.join(upload_dir, filename)

    # grava o arquivo
    with open(filepath, 'wb') as f:
        f.write(img_bytes)

    # caminho relativo para usar no src do <img>
    relative_path = os.path.join('uploads', 'atletas', filename).replace('\\', '/')

    # se já existe foto, atualiza; senão cria nova
    if atleta.fotos:
        atleta.fotos[0].foto_path = relative_path
    else:
        foto = AtletaFoto(atleta_id=atleta.id, foto_path=relative_path)
        db.session.add(foto)

    db.session.commit()


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

        # base64 da foto
        foto_base64 = (request.form.get('foto_base64') or '').strip()

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
        db.session.commit()  # precisa do ID para salvar a foto

        # salva a foto se enviada
        if foto_base64:
            salvar_foto_base64(atleta, foto_base64)

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

        foto_base64 = (request.form.get('foto_base64') or '').strip()

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

        # se mandou uma nova foto, sobrescreve
        if foto_base64:
            salvar_foto_base64(atleta, foto_base64)

        flash('Dados do atleta atualizados!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', atleta=atleta)
