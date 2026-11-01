from flask import g, redirect
from flask_appbuilder import IndexView, expose
from sqlalchemy import func


class VistaInicio(IndexView):
    index_template = "inicio.html"

    @expose("/")
    def index(self):
        from . import db
        from .models import Ticket, Estado

        # Solicitante y Tecnico van directo a la lista de tickets.
        # Solo el Admin ve el dashboard de inicio.
        if g.user and g.user.is_authenticated:
            roles = [r.name for r in g.user.roles]
            if "Admin" not in roles and ("Solicitante" in roles or "Tecnico" in roles):
                return redirect("/tickets/list/")

        s = db.session
        estadisticas = {
            "total": s.query(func.count(Ticket.id)).scalar() or 0,
            "abiertos": s.query(func.count(Ticket.id))
                         .join(Estado, Ticket.estado_id == Estado.id)
                         .filter(Estado.es_cerrado == False).scalar() or 0,
            "cerrados": s.query(func.count(Ticket.id))
                         .join(Estado, Ticket.estado_id == Estado.id)
                         .filter(Estado.es_cerrado == True).scalar() or 0,
        }
        return self.render_template(
            self.index_template,
            appbuilder=self.appbuilder,
            estadisticas=estadisticas,
        )