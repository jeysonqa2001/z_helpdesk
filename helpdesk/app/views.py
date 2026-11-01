from datetime import datetime

from flask import g, flash, redirect
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import BaseFilter
from flask_appbuilder.actions import action

from . import appbuilder, db
from .models import Departamento, Categoria, Prioridad, Estado, Ticket, Comentario
from .ia import analizar_ticket

ETIQUETAS_AUDITORIA = {
    "created_by": "Creado por",
    "created_on": "Fecha de creación",
    "changed_by": "Modificado por",
    "changed_on": "Fecha de modificación",
}


class FiltroTicketsPorRol(BaseFilter):
    """Admin y Tecnico ven todo; el Solicitante solo ve sus propios tickets."""
    name = "Por rol"
    arg_name = "rol"

    def apply(self, query, value):
        roles = [r.name for r in g.user.roles]
        if "Admin" in roles or "Tecnico" in roles:
            return query
        return query.filter(Ticket.created_by_fk == g.user.id)


class VistaComentario(ModelView):
    datamodel = SQLAInterface(Comentario)
    route_base = "/comentarios"
    list_title = "Lista de comentarios"
    add_title = "Agregar comentario"
    edit_title = "Editar comentario"
    show_title = "Detalle del comentario"
    list_columns = ["ticket", "texto", "created_by", "created_on"]
    add_columns = ["ticket", "texto"]
    edit_columns = ["ticket", "texto"]
    label_columns = {"ticket": "Ticket", "texto": "Comentario", **ETIQUETAS_AUDITORIA}


class VistaTicket(ModelView):
    datamodel = SQLAInterface(Ticket)
    route_base = "/tickets"
    related_views = [VistaComentario]
    base_filters = [["id", FiltroTicketsPorRol, ""]]
    base_order = ("id", "desc")

    list_title = "Lista de tickets"
    add_title = "Nuevo ticket"
    edit_title = "Editar ticket"
    show_title = "Detalle del ticket"

    list_columns = ["id", "titulo", "solicitante", "categoria", "prioridad", "estado",
                    "tecnico", "tiempo_respuesta", "tiempo_resolucion"]
    order_columns = ["id", "titulo", "created_on", "fecha_atencion", "fecha_cierre"]
    search_columns = ["titulo", "solicitante", "categoria", "prioridad", "estado", "asignado_a"]
    add_columns = ["titulo", "descripcion", "categoria", "prioridad", "estado"]
    edit_columns = ["titulo", "descripcion", "categoria", "prioridad", "estado", "asignado_a"]
    show_fieldsets = [
        ("Ticket", {"fields": ["titulo", "descripcion", "categoria", "prioridad", "estado"]}),
        ("Responsables", {"fields": ["solicitante", "asignado_a"]}),
        ("Tiempos", {"fields": ["created_on", "fecha_atencion", "fecha_cierre",
                                "tiempo_respuesta", "tiempo_resolucion"]}),
        ("Análisis con IA", {"fields": ["analisis_ia"], "expanded": True}),
    ]
    label_columns = {
        "id": "N°",
        "titulo": "Título",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "prioridad": "Prioridad",
        "estado": "Estado",
        "solicitante": "Solicitante",
        "asignado_a": "Técnico asignado",
        "tecnico": "Técnico asignado",
        "fecha_atencion": "Inicio de atención",
        "fecha_cierre": "Fecha de cierre",
        "tiempo_respuesta": "Tiempo de respuesta",
        "tiempo_resolucion": "Tiempo de resolución",
        "analisis_ia": "Análisis de IA",
        **ETIQUETAS_AUDITORIA,
    }

    def _actualizar_tiempos(self, item):
        ahora = datetime.now()
        if item.estado and item.estado.nombre != "Abierto" and not item.fecha_atencion:
            item.fecha_atencion = ahora
            if not item.asignado_a_fk:  # quien empieza a atender queda como técnico
                item.asignado_a_fk = g.user.id
        if item.estado and item.estado.es_cerrado:
            if not item.fecha_cierre:
                item.fecha_cierre = ahora
        else:
            item.fecha_cierre = None  # si se reabre, se limpia el cierre

    def pre_add(self, item):
        self._actualizar_tiempos(item)

    def pre_update(self, item):
        self._actualizar_tiempos(item)

    @action("analizar_ia", "Analizar con IA", "¿Analizar este ticket con IA?", "fa-magic", single=True)
    def analizar_ia(self, item):
        try:
            item.analisis_ia = analizar_ticket(item)
            self.datamodel.edit(item)
            flash("Análisis generado correctamente", "success")
        except Exception as e:
            flash(f"Error con la IA: {e}", "danger")
        return redirect(self.get_redirect())


class VistaDepartamento(ModelView):
    datamodel = SQLAInterface(Departamento)
    route_base = "/departamentos"
    list_title = "Lista de departamentos"
    add_title = "Agregar departamento"
    edit_title = "Editar departamento"
    show_title = "Detalle del departamento"
    label_columns = {"nombre": "Nombre", "descripcion": "Descripción"}


class VistaCategoria(ModelView):
    datamodel = SQLAInterface(Categoria)
    route_base = "/categorias"
    list_title = "Lista de categorías"
    add_title = "Agregar categoría"
    edit_title = "Editar categoría"
    show_title = "Detalle de la categoría"
    list_columns = ["nombre", "departamento"]
    label_columns = {"nombre": "Nombre", "departamento": "Departamento"}


class VistaPrioridad(ModelView):
    datamodel = SQLAInterface(Prioridad)
    route_base = "/prioridades"
    list_title = "Lista de prioridades"
    add_title = "Agregar prioridad"
    edit_title = "Editar prioridad"
    show_title = "Detalle de la prioridad"
    label_columns = {"nombre": "Nombre", "horas_sla": "Horas de atención (SLA)"}


class VistaEstado(ModelView):
    datamodel = SQLAInterface(Estado)
    route_base = "/estados"
    list_title = "Lista de estados"
    add_title = "Agregar estado"
    edit_title = "Editar estado"
    show_title = "Detalle del estado"
    label_columns = {"nombre": "Nombre", "es_cerrado": "¿Cierra el ticket?"}


db.create_all()

appbuilder.add_view(VistaTicket, "Tickets", icon="fa-ticket", category="Soporte")
appbuilder.add_view(VistaComentario, "Comentarios", icon="fa-comments", category="Soporte")
appbuilder.add_view(VistaDepartamento, "Departamentos", icon="fa-building", category="Configuración")
appbuilder.add_view(VistaCategoria, "Categorías", icon="fa-tags", category="Configuración")
appbuilder.add_view(VistaPrioridad, "Prioridades", icon="fa-flag", category="Configuración")
appbuilder.add_view(VistaEstado, "Estados", icon="fa-tasks", category="Configuración")