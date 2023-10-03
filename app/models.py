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
    tipo = db.Column(db.String(100), nullable=False)
    # atendentes = db.relationship('Profissional', secondary=beneficiario_profissional, back_populates='beneficiarios')
    atendente_1_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
    atendente_2_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
    atendente_3_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))

    atendente_1 = db.relationship('Profissional', foreign_keys=[atendente_1_id], backref='beneficiario_atendente_1')
    atendente_2 = db.relationship('Profissional', foreign_keys=[atendente_2_id], backref='beneficiario_atendente_2')
    atendente_3 = db.relationship('Profissional', foreign_keys=[atendente_3_id], backref='beneficiario_atendente_3')

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    def beneficiarios_relacionados(self):
        return Beneficiario.query.filter(
            (Beneficiario.atendente_1 == self) |
            (Beneficiario.atendente_2 == self) |
            (Beneficiario.atendente_3 == self)
        ).all()

    # beneficiarios = db.relationship('Beneficiario', secondary=beneficiario_profissional, back_populates='atendentes')

# Crie uma nova classe de modelo para representar a nova tabela
class ResumoProducao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beneficiario_id = db.Column(db.Integer, nullable=False)
    qtd_total = db.Column(db.Integer, nullable=False)
    producao_id = db.Column(db.Integer, nullable=False)

# class TabelaResultadoProducao(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     beneficiario = db.Column(db.String(100), nullable=False)
#     qtd_paga = db.Column(db.Integer, nullable=False)
#     valor_atendimento = db.Column(db.Float, nullable=False)
#     tipo = db.Column(db.String(100), nullable=False)
#     atendente_1_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
#     atendente_2_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
#     atendente_3_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
#     producao_id = db.Column(db.Integer, db.ForeignKey('producao.id'))

#     atendente_1 = db.relationship('Profissional', foreign_keys=[atendente_1_id], backref='beneficiario_atendente_1')
#     atendente_2 = db.relationship('Profissional', foreign_keys=[atendente_2_id], backref='beneficiario_atendente_2')
#     atendente_3 = db.relationship('Profissional', foreign_keys=[atendente_3_id], backref='beneficiario_atendente_3')






