from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255),nullable=False)
    telefone = db.Column(db.String(30), nullable=True)
    role = db.Column(db.Enum('admin', 'coach', 'parent', default='parent'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Responsavel(db.Model):
    __tablename__ = 'responsaveis'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    observacoes = db.Column(db.String(255))

class Atleta(db.Model):
    __tablename__ = 'atletas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    posicao = db.Column(db.String(50))
    documento = db.Column(db.String(50))
    telefone_residencial = db.Column(db.String(30))
    status = db.Column(db.Enum('ATIVO', 'INATIVO', default='ATIVO'))
    criado_em = db.Column(db.dateTime, default=datetime.utcnow)

class AtletaFoto(db.Model):
    __tablename__ = 'atleta_fotos'
    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'))
    foto_path = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Grupo(db.Model):
    __tablename__ = 'grupos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    faixa_etaria_min = db.Column(db.Integer)
    faixa_etaria_max = db.Column(db.Integer)
    descricao = db.Column(db.String(255))

class Plano(db.Model):
    __tablename__ = 'atividades'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data = db.Column(db.Date)
    hora_inicio = db.Column(db.Time)
    hora_fim = db.Column(db.Time)
    local = db.Column(db.String(255))
    descricao = db.Column(db.String(500))

class Presenca(db.MOdel):
    __tablename__ = 'presencas'
    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'))
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'))
    status = db.Column(db.Enum('PRESENTE', 'AUSENTE', 'JUSTIFICADO'))
    observacao = db.Column(db.String(255))
    registrado_em = db.Column(db.DateTime, default=datetime.utcnow)

class ContaReceber(db.Model):
    __tablename__ = 'contas_receber'
    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'))
    descricao = db.Column(db.String(255))
    competencia = db.Column(db.Date)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('PENDENTE', 'PAGO', 'ATRASADO', 'CANCELADO', default='PENDENTE'))
    metodo_pagamento = db.Column(db.Enum('DINHEIRO', 'PIX', 'TRANSFERENCIA', 'CREDITO', 'DEBITO', 'ISENTO', default='PIX'))
    pago_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)