from extensions import db
from flask_login import UserMixin
from datetime import datetime, date

# =========================
# USUÁRIOS & RESPONSÁVEIS
# =========================

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(30))
    role = db.Column(db.Enum('ADMIN', 'COACH', 'PARENT'), nullable=False, default='PARENT')
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    responsavel = db.relationship("Responsavel", backref="usuario", uselist=False)


class Responsavel(db.Model):
    __tablename__ = 'responsaveis'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    observacoes = db.Column(db.String(255))

    atletas = db.relationship("AtletaResponsavel", back_populates="responsavel")


# =========================
# ATLETAS
# =========================

class Atleta(db.Model):
    __tablename__ = 'atletas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)

    # Campos de documento pessoais
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(14))

    posicao = db.Column(db.String(50))

    # campo antigo genérico que já existia
    documento = db.Column(db.String(50))

    # Telefones
    telefone_residencial = db.Column(db.String(30))
    telefone = db.Column(db.String(30))

    status = db.Column(db.Enum('ATIVO', 'INATIVO'), default='ATIVO')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Endereço (vamos criar via SQL)
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(80))
    bairro = db.Column(db.String(80))
    cidade = db.Column(db.String(80))
    estado = db.Column(db.String(2))

    # Médico / docs
    validade_atestado = db.Column(db.Date)
    informacoes_adicionais = db.Column(db.String(255))

    doc_rg_ok = db.Column(db.Boolean, default=False)
    doc_cpf_ok = db.Column(db.Boolean, default=False)
    doc_comprov_endereco_ok = db.Column(db.Boolean, default=False)
    doc_decl_escolar_ok = db.Column(db.Boolean, default=False)
    doc_atestado_medico_ok = db.Column(db.Boolean, default=False)

    # Dados do responsável atrelados direto ao atleta
    responsavel_nome = db.Column(db.String(150))
    responsavel_cpf = db.Column(db.String(14))
    responsavel_telefone = db.Column(db.String(30))

    # Relacionamentos que já existiam
    fotos = db.relationship("AtletaFoto", backref="atleta", lazy=True)
    responsaveis = db.relationship("AtletaResponsavel", back_populates="atleta")
    grupos = db.relationship("AtletaGrupo", back_populates="atleta")
    planos = db.relationship("AtletaPlano", back_populates="atleta")
    financeiro = db.relationship("ContaReceber", backref="atleta", lazy=True)


class AtletaFoto(db.Model):
    __tablename__ = 'atletas_fotos'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    foto_path = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class AtletaResponsavel(db.Model):
    __tablename__ = 'atletas_responsaveis'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsaveis.id'), nullable=False)
    parentesco = db.Column(db.String(50))

    atleta = db.relationship("Atleta", back_populates="responsaveis")
    responsavel = db.relationship("Responsavel", back_populates="atletas")


# =========================
# GRUPOS & PLANOS
# =========================

class Grupo(db.Model):
    __tablename__ = 'grupos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    faixa_etaria_min = db.Column(db.Integer)
    faixa_etaria_max = db.Column(db.Integer)
    descricao = db.Column(db.String(255))

    atletas = db.relationship("AtletaGrupo", back_populates="grupo")
    atividades = db.relationship("Atividade", backref="grupo", lazy=True)


class AtletaGrupo(db.Model):
    __tablename__ = 'atletas_grupos'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    atleta = db.relationship("Atleta", back_populates="grupos")
    grupo = db.relationship("Grupo", back_populates="atletas")


class Plano(db.Model):
    __tablename__ = 'planos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Numeric(10, 2), nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=True)
    forma_pagamento_padrao = db.Column(
        db.Enum('PIX', 'CREDITO', 'DEBITO', 'DINHEIRO'),
        default='PIX'
    )
    periodicidade_cobranca = db.Column(
        db.Enum('MENSAL', 'TRIMESTRAL', 'SEMESTRAL', 'ANUAL'),
        default='MENSAL'
    )
    descricao = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)

    atletas = db.relationship("AtletaPlano", back_populates="plano")


class AtletaPlano(db.Model):
    __tablename__ = 'atletas_planos'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    plano_id = db.Column(db.Integer, db.ForeignKey('planos.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False, default=date.today)
    data_fim = db.Column(db.Date)
    ativo = db.Column(db.Boolean, default=True)

    atleta = db.relationship("Atleta", back_populates="planos")
    plano = db.relationship("Plano", back_populates="atletas")


# =========================
# ATIVIDADES & PRESENÇAS
# =========================

class Atividade(db.Model):
    __tablename__ = 'atividades'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time)
    local = db.Column(db.String(150))
    descricao = db.Column(db.String(255))

    presencas = db.relationship("Presenca", backref="atividade", lazy=True)


class Presenca(db.Model):
    __tablename__ = 'presencas'

    id = db.Column(db.Integer, primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    status = db.Column(db.Enum('PRESENTE', 'AUSENTE', 'JUSTIFICADO'), nullable=False)
    observacao = db.Column(db.String(255))
    registrado_em = db.Column(db.DateTime, default=datetime.utcnow)

    atleta = db.relationship("Atleta")

    __table_args__ = (
        db.UniqueConstraint('atividade_id', 'atleta_id', name='uk_presenca_atividade_atleta'),
    )


# =========================
# FINANCEIRO
# =========================

class ContaReceber(db.Model):
    __tablename__ = 'contas_receber'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'))
    descricao = db.Column(db.String(255))
    competencia = db.Column(db.Date)
    vencimento = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum('PENDENTE', 'PAGO', 'ATRASADO', 'CANCELADO'),
        default='PENDENTE'
    )
    metodo_pagamento = db.Column(
        db.Enum('PIX', 'CREDITO', 'DEBITO', 'DINHEIRO', 'ISENTO'),
        default='PIX'
    )
    mercadopago_payment_id = db.Column(db.String(100))
    pago_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class ContaPagar(db.Model):
    __tablename__ = 'contas_pagar'

    id = db.Column(db.Integer, primary_key=True)
    fornecedor = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.String(255))
    vencimento = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum('PENDENTE', 'PAGO', 'ATRASADO', 'CANCELADO'),
        default='PENDENTE'
    )
    pago_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class FluxoCaixa(db.Model):
    __tablename__ = 'fluxo_caixa'

    id = db.Column(db.Integer, primary_key=True)
    data_movimento = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum('ENTRADA', 'SAIDA'), nullable=False)
    origem = db.Column(
        db.Enum('MENSALIDADE', 'OUTRO_RECEBIMENTO', 'CONTA_PAGAR', 'AJUSTE'),
        nullable=False
    )
    referencia_id = db.Column(db.Integer)
    descricao = db.Column(db.String(255))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class MpWebhookLog(db.Model):
    __tablename__ = 'mp_webhook_logs'

    id = db.Column(db.Integer, primary_key=True)
    evento = db.Column(db.String(50))
    raw_body = db.Column(db.Text)
    recebido_em = db.Column(db.DateTime, default=datetime.utcnow)
