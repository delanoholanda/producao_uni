from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DadosProducao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lote = db.Column(db.String(50), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    codigo = db.Column(db.String(20), nullable=False)
    beneficiario_id = db.Column(db.Integer, db.ForeignKey('beneficiario.id'), nullable=False)
    qtd_paga = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    producao_id = db.Column(db.Integer, db.ForeignKey('producao.id'), nullable=False)

class Producao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # descricao = db.Column(db.String(100), nullable=False)
    producao_movimetacao = db.Column(db.String(20), nullable=False, unique=True)
    dados_producao = db.relationship('DadosProducao', backref='producao', lazy=True)

class Beneficiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100))
    atendente_1 = db.Column(db.String(100))
    atendente_2 = db.Column(db.String(100))
    atendente_3 = db.Column(db.String(100))

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    beneficiario_id = db.Column(db.Integer, db.ForeignKey('beneficiario.id'), nullable=False)