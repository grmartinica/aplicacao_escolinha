from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from extensions import db
from models import Atleta, AtletaFoto
from datetime import datetime
import os
import base64

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')


@atletas_bp.route('/listar')
@login_required
def listar():
    # Futuro: você pode colocar filtros aqui se quiser (status, nome, etc.)
    atletas = Atleta.query.order_by(Atleta.nome).all()
    return render_template('atletas_listar.html', atletas=atletas)


def _salvar_foto_base64(atleta_id, foto_base64):
    """
    Recebe um dataURL (data:image/jpeg;base64,xxxx) e salva como arquivo.
    Cria um registro em AtletaFoto.
    """
    if not foto_base64 or not foto_base64.startswith('data:image'):
        return

    try:
        header, encoded = foto_base64.split(',', 1)
    except ValueError:
        return

    try:
        img_data = base64.b64decode(encoded)
    except Exception:
        return

    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    if not upload_folder:
        return

    os.makedirs(upload_folder, exist_ok=True)

    filename = f"atleta_{atleta_id}_{int(datetime.utcnow().timestamp())}.jpg"
    filepath = os.path.join(upload_folder, filename)

    with open(filepath, 'wb') as f:
        f.write(img_data)

    foto = AtletaFoto(
        atleta_id=atleta_id,
        foto_path=f"uploads/atletas/{filename}"
    )
    db.session.add(foto)
    db.session.commit()


@atletas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        dn = request.form.get('data_nascimento')
        posicao = (request.form.get('posicao') or '').strip() or None
        telefone = (request.form.get('telefone') or '').strip() or None

        # Documentos: CPF ou RG (apenas um campo "documento" no banco)
        doc_type = request.form.get('doc_type')  # 'CPF' ou 'RG'
        cpf = (request.form.get('cpf') or '').strip()
        rg = (request.form.get('rg') or '').strip()

        documento = None
        if doc_type == 'CPF' and cpf:
            documento = cpf
        elif doc_type == 'RG' and rg:
            documento = rg

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
        db.session.commit()  # precisa ter ID para salvar foto

        # Foto da câmera (opcional)
        foto_base64 = request.form.get('foto_base64')
        _salvar_foto_base64(atleta.id, foto_base64)

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
        telefone = (request.form.get('telefone') or '').strip() or None
        status = request.form.get('status') or 'ATIVO'

        doc_type = request.form.get('doc_type')
        cpf = (request.form.get('cpf') or '').strip()
        rg = (request.form.get('rg') or '').strip()

        documento = None
        if doc_type == 'CPF' and cpf:
            documento = cpf
        elif doc_type == 'RG' and rg:
            documento = rg

        if not nome or not dn:
            flash('Preencha nome e data de nascimento.', 'danger')
            return redirect(url_for('atletas.editar', atleta_id=atleta.id))

        atleta.nome = nome
        atleta.data_nascimento = datetime.strptime(dn, '%Y-%m-%d').date()
        atleta.posicao = posicao
        atleta.telefone_residencial = telefone
        atleta.status = status
        atleta.documento = documento

        db.session.commit()

        # Se tirar nova foto, salva como novo registro
        foto_base64 = request.form.get('foto_base64')
        _salvar_foto_base64(atleta.id, foto_base64)

        flash('Dados do atleta atualizados!', 'success')
        return redirect(url_for('atletas.listar'))

    return render_template('atletas_novo.html', atleta=atleta)
