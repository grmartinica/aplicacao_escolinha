from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from aplicacao_escolinha.extensions import db
from aplicacao_escolinha.models import Atleta, AtletaFoto
import base64, os

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')

@atletas_bp.route('/')
def listar():
    atletas = Atleta.query.all()
    return render_template('atletas/listar.html', atletas=atletas)

@atletas_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_nasc = request.form.get('data_nascimento')
        posicao = request.form.get('posicao')
        
        atleta = Atleta(nome=nome, data_nascimento=data_nasc, posicao=posicao)
        db.session.add(atleta)
        db.session.commit()

        foto_base64 = request.form.get('foto_base64')
        if foto_base64:
            foto_data = base64.b64decode(foto_base64.split(',')[1])
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'atleta_{atleta.id}.jpg')
            with open(path, 'wb') as f:
                f.write(foto_data)
            db.session.add(AtletaFoto(atleta_id=atleta.id, foto_path=path))
            db.session.commit()

        
        flash('Atleta criado com sucesso!', 'success')
        return redirect(url_for('atletas.listar'))
    
    return render_template('atletas_novo.html')