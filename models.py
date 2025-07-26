from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Cozinheiro(db.Model):
    __tablename__ = 'cozinheiros'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cep = db.Column(db.String(9))
    cpf = db.Column(db.String(14))
    data_nascimento = db.Column(db.Date)
    idade = db.Column(db.Integer)
    senha_hash = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='comum')

    pratos = db.relationship('Prato', backref='cozinheiro')

    @staticmethod
    def calcular_idade(data_nascimento):
        hoje = date.today()
        return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    def to_dict_completo(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cep': self.cep,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.strftime('%Y-%m-%d') if self.data_nascimento else None,
            'idade': self.idade,
            'tipo': self.tipo
        }

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'idade': self.idade
        }

class Tipo(db.Model):
    __tablename__ = 'tipo'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    pratos = db.relationship('Prato', back_populates='tipo', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tipo {self.nome}>'

class Prato(db.Model):
    __tablename__ = 'pratos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(255))
    peso = db.Column(db.Integer, nullable=False)

    cozinheiro_id = db.Column(db.Integer, db.ForeignKey('cozinheiros.id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo.id'), nullable=True)

    tipo = db.relationship('Tipo', back_populates='pratos')
    pedidos = db.relationship('Pedido', back_populates='prato', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prato {self.nome}>'

class Pedido(db.Model):
    __tablename__ = 'pedido'

    id = db.Column(db.Integer, primary_key=True)
    prato_id = db.Column(db.Integer, db.ForeignKey('pratos.id'), nullable=False)

    prato = db.relationship('Prato', back_populates='pedidos')

    def __repr__(self):
        return f'<Pedido prato_id={self.prato_id}>'
