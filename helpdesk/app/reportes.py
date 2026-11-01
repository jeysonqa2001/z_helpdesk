from datetime import datetime, timedelta

from flask import request
from flask_appbuilder import BaseView, expose, has_access
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import func, case

from . import appbuilder, db
from .models import Departamento, Categoria, Prioridad, Estado, Ticket


def _fechas():
    def p(v):
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except ValueError:
            return None
    return p(request.args.get("desde")), p(request.args.get("hasta"))


def _filtrar_fechas(q):
    desde, hasta = _fechas()
    if desde:
        q = q.filter(Ticket.created_on >= desde)
    if hasta:
        # "Hasta" incluye todo el día seleccionado
        q = q.filter(Ticket.created_on < hasta + timedelta(days=1))
    return q


class VistaReportes(BaseView):
    route_base = "/reportes"
    default_view = "por_estado"

    def _mostrar(self, titulo, columnas, filas):
        return self.render_template(
            "reporte.html", titulo=titulo, columnas=columnas, filas=filas,
            desde=request.args.get("desde", ""), hasta=request.args.get("hasta", ""),
        )

    @expose("/por_estado/")
    @has_access
    def por_estado(self):
        q = (db.session.query(Estado.nombre, Prioridad.nombre, func.count(Ticket.id))
             .select_from(Ticket).join(Estado).join(Prioridad)
             .group_by(Estado.nombre, Prioridad.nombre))
        return self._mostrar("Tickets por estado y prioridad",
                             ["Estado", "Prioridad", "Cantidad"], _filtrar_fechas(q).all())

    @expose("/por_agente/")
    @has_access
    def por_agente(self):
        q = (db.session.query(
                User.username,
                func.count(Ticket.id),
                func.sum(case((Estado.es_cerrado == True, 1), else_=0)))
             .select_from(Ticket)
             .join(User, Ticket.asignado_a_fk == User.id)
             .join(Estado).group_by(User.username))
        return self._mostrar("Carga de trabajo por agente",
                             ["Agente", "Asignados", "Cerrados"], _filtrar_fechas(q).all())

    @expose("/por_departamento/")
    @has_access
    def por_departamento(self):
        q = (db.session.query(Departamento.nombre, Categoria.nombre, func.count(Ticket.id))
             .select_from(Ticket).join(Categoria).join(Departamento)
             .group_by(Departamento.nombre, Categoria.nombre))
        return self._mostrar("Tickets por departamento y categoría",
                             ["Departamento", "Categoría", "Cantidad"], _filtrar_fechas(q).all())


appbuilder.add_view(VistaReportes, "Por estado y prioridad", href="/reportes/por_estado/",
                    category="Reportes", icon="fa-bar-chart")
appbuilder.add_link("Por agente", href="/reportes/por_agente/", category="Reportes", icon="fa-user")
appbuilder.add_link("Por departamento", href="/reportes/por_departamento/", category="Reportes", icon="fa-sitemap")