from flask_appbuilder import IndexView, expose
from sqlalchemy import func


class VistaInicio(IndexView):
    index_template = "inicio.html"

    @expose("/")
    def index(self):
        from . import db
        from .models import Ticket, Estado

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