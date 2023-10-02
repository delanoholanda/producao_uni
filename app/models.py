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

# # Tabela intermediária para a relação M2M entre Beneficiario e Profissional
# beneficiario_profissional = db.Table(
#     'beneficiario_profissional',
#     db.Column('beneficiario_id', db.Integer, db.ForeignKey('beneficiario.id'), primary_key=True),
#     db.Column('profissional_id', db.Integer, db.ForeignKey('profissional.id'), primary_key=True)
# )

class Beneficiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    # atendentes = db.relationship('Profissional', secondary=beneficiario_profissional, back_populates='beneficiarios')
    atendente_1_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
    atendente_2_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
    atendente_3_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))

    atendente_1 = db.relationship('Profissional', foreign_keys=[atendente_1_id], backref='beneficiario_atendente_1')
    atendente_2 = db.relationship('Profissional', foreign_keys=[atendente_2_id], backref='beneficiario_atendente_2')
    atendente_3 = db.relationship('Profissional', foreign_keys=[atendente_3_id], backref='beneficiario_atendente_3')

# class Beneficiario(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(100), nullable=False)
#     tipo = db.Column(db.String(100))
#     atendentes = db.relationship('Profissional', secondary=beneficiario_profissional, back_populates='beneficiarios')

#     # atendente_1 = db.Column(db.String(100))
#     # atendente_2 = db.Column(db.String(100))
#     # atendente_3 = db.Column(db.String(100))

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    # beneficiarios = db.relationship('Beneficiario', secondary=beneficiario_profissional, back_populates='atendentes')

