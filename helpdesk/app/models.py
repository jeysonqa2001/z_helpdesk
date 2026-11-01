from datetime import datetime
from flask import g
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


def usuario_actual():
    try:
        return g.user.id
    except Exception:
        return None


def formatear_duracion(inicio, fin):
    if not inicio or not fin:
        return "—"
    segundos = max(int((fin - inicio).total_seconds()), 0)
    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos = resto // 60
    if dias:
        return f"{dias}d {horas}h {minutos}m"
    if horas:
        return f"{horas}h {minutos}m"
    return f"{minutos}m"


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

    solicitante_fk = Column(Integer, ForeignKey("ab_user.id"), default=usuario_actual)
    solicitante = relationship("User", foreign_keys=[solicitante_fk])

    asignado_a_fk = Column(Integer, ForeignKey("ab_user.id"))
    asignado_a = relationship("User", foreign_keys=[asignado_a_fk])

    fecha_atencion = Column(DateTime)
    fecha_cierre = Column(DateTime)
    analisis_ia = Column(Text)

    @property
    def tiempo_respuesta(self):
        return formatear_duracion(self.created_on, self.fecha_atencion)

    @property
    def tiempo_resolucion(self):
        return formatear_duracion(self.created_on, self.fecha_cierre)

    @property
    def tecnico(self):
        return str(self.asignado_a) if self.asignado_a else "Sin asignar"

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