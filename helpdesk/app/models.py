from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Departamento(Model):
    __tablename__ = "departamento"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(250))

    def __repr__(self):
        return self.nombre


class Categoria(Model):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamento.id"), nullable=False)
    departamento = relationship("Departamento")

    def __repr__(self):
        return self.nombre


class Prioridad(Model):
    __tablename__ = "prioridad"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(40), unique=True, nullable=False)
    horas_sla = Column(Integer, default=24)

    def __repr__(self):
        return self.nombre


class Estado(Model):
    __tablename__ = "estado"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(40), unique=True, nullable=False)
    es_cerrado = Column(Boolean, default=False)

    def __repr__(self):
        return self.nombre


class Ticket(AuditMixin, Model):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categoria.id"), nullable=False)
    categoria = relationship("Categoria")
    prioridad_id = Column(Integer, ForeignKey("prioridad.id"), nullable=False)
    prioridad = relationship("Prioridad")
    estado_id = Column(Integer, ForeignKey("estado.id"), nullable=False)
    estado = relationship("Estado")
    asignado_a_fk = Column(Integer, ForeignKey("ab_user.id"))
    asignado_a = relationship("User", foreign_keys=[asignado_a_fk])
    analisis_ia = Column(Text)

    def __repr__(self):
        return f"#{self.id} {self.titulo}"


class Comentario(AuditMixin, Model):
    __tablename__ = "comentario"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=False)
    ticket = relationship("Ticket", backref="comentarios")
    texto = Column(Text, nullable=False)

    def __repr__(self):
        return self.texto