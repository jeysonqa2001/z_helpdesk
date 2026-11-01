from flask_appbuilder import IndexView, expose
from sqlalchemy import func


class VistaInicio(IndexView):
    index_template = "inicio.html"

    @expose("/")
    def index(self):
        from .models import Ticket, Estado
        s = self.appbuilder.get_session
        estadisticas = {
            "total": s.query(func.count(Ticket.id)).scalar(),
            "abiertos": s.query(func.count(Ticket.id)).join(Estado).filter(Estado.es_cerrado == False).scalar(),
            "cerrados": s.query(func.count(Ticket.id)).join(Estado).filter(Estado.es_cerrado == True).scalar(),
        }
        return self.render_template(self.index_template, appbuilder=self.appbuilder, estadisticas=estadisticas)