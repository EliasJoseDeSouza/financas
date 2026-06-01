from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Lancamento(db.Model):
    __tablename__ = 'lancamentos'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)          # 'receita' ou 'despesa'
    competencia = db.Column(db.String(7), nullable=False)    # '06/2026'
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    forma = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'competencia': self.competencia,
            'descricao': self.descricao,
            'valor': self.valor,
            'forma': self.forma,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M') if self.criado_em else ''
        }
