<<<<<<< HEAD
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from extensions import db
from models import Atleta, AtletaFoto
import base64, os
=======
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Atleta
from datetime import datetime
>>>>>>> f57ce4cdbec38f48fbcbbdbdc779ca0235635612

atletas_bp = Blueprint('atletas', __name__, url_prefix='/atletas')

@atletas_bp.route('/listar')
@login_required
def listar():
    atletas = Atleta.query.order_by(Atleta.nome).all()
    return render_template('atletas_listar.html', atletas=atletas)

@atletas_bp.route('/novo', methods=['GET','POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        dn = request.form.get('data_nascimento')
        posicao = request.form.get('posicao') or None
        if not nome or not dn:
            flash('Preencha nome e data de nascimento', 'danger')
            return redirect(url_for('atletas.novo'))
        atleta = Atleta(
            nome=nome,
            data_nascimento=datetime.strptime(dn, '%Y-%m-%d').date(),
            posicao=posicao,
            status='ATIVO'
        )
        db.session.add(atleta)
        db.session.commit()
        flash('Atleta cadastrado!', 'success')
        return redirect(url_for('atletas.listar'))
    return render_template('atletas_novo.html')
