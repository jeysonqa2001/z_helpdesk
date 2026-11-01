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
    """Admin y Agente ven todo; el Usuario solo ve sus propios tickets."""
    name = "Por rol"
    arg_name = "rol"

    def apply(self, query, value):
        roles = [r.name for r in g.user.roles]
        if "Admin" in roles or "Agente" in roles:
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

    list_columns = ["id", "titulo", "categoria", "prioridad", "estado", "asignado_a", "created_on"]
    search_columns = ["titulo", "categoria", "prioridad", "estado", "asignado_a"]
    add_columns = ["titulo", "descripcion", "categoria", "prioridad", "estado", "asignado_a"]
    edit_columns = add_columns
    show_fieldsets = [
        ("Ticket", {"fields": ["titulo", "descripcion", "categoria", "prioridad", "estado", "asignado_a"]}),
        ("Análisis con IA", {"fields": ["analisis_ia"], "expanded": True}),
    ]
    label_columns = {
        "id": "N°",
        "titulo": "Título",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "prioridad": "Prioridad",
        "estado": "Estado",
        "asignado_a": "Asignado a",
        "analisis_ia": "Análisis de IA",
        **ETIQUETAS_AUDITORIA,
    }

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