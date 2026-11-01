from flask import request, jsonify
from flask_appbuilder import BaseView, expose, has_access

from . import appbuilder, db
from .models import Ticket, Estado
from .ia import chat_ia


def _resumen(t, con_descripcion=False):
    linea = f"#{t.id} | {t.titulo} | {t.categoria} | prioridad {t.prioridad} | estado {t.estado}"
    if con_descripcion:
        linea += f" | {str(t.descripcion)[:200]}"
    return linea


def _contexto(ticket_id=None):
    s = db.session
    partes = []

    abiertos = (s.query(Ticket).join(Estado, Ticket.estado_id == Estado.id)
                .filter(Estado.es_cerrado == False)
                .order_by(Ticket.id.desc()).limit(10).all())
    partes.append("Tickets abiertos recientes:\n" +
                  ("\n".join(_resumen(t) for t in abiertos) or "ninguno"))

    cerrados = (s.query(Ticket).join(Estado, Ticket.estado_id == Estado.id)
                .filter(Estado.es_cerrado == True)
                .order_by(Ticket.id.desc()).limit(10).all())
    partes.append("Tickets ya resueltos (sirven como referencia de casos parecidos):\n" +
                  ("\n".join(_resumen(t, True) for t in cerrados) or "ninguno"))

    if ticket_id:
        t = s.get(Ticket, ticket_id)
        if t:
            partes.append(
                f"TICKET EN CONSULTA #{t.id}\nTítulo: {t.titulo}\n"
                f"Descripción: {t.descripcion}\nCategoría: {t.categoria}\n"
                f"Prioridad: {t.prioridad}\nEstado: {t.estado}\n"
                f"Solicitante: {t.solicitante}\nTécnico: {t.asignado_a}"
            )
    return "\n\n".join(partes)


class VistaAsistente(BaseView):
    route_base = "/asistente"
    default_view = "chat"

    @expose("/")
    @has_access
    def chat(self):
        return self.render_template("asistente.html")

    @expose("/preguntar/", methods=["POST"])
    @has_access
    def preguntar(self):
        datos = request.get_json(silent=True) or {}

        historial = []
        for m in (datos.get("historial") or [])[-8:]:
            rol = m.get("role")
            texto = str(m.get("content", ""))[:2000]
            if rol in ("user", "assistant") and texto.strip():
                historial.append({"role": rol, "content": texto})

        if not historial or historial[-1]["role"] != "user":
            return jsonify({"error": "Escribe una pregunta."}), 400

        ticket_id = None
        try:
            ticket_id = int(datos.get("ticket_id")) if datos.get("ticket_id") else None
        except (TypeError, ValueError):
            pass

        try:
            respuesta = chat_ia(historial, _contexto(ticket_id))
            return jsonify({"respuesta": respuesta})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


appbuilder.add_view(VistaAsistente, "Asistente IA", href="/asistente/",
                    icon="fa-comments", category="Soporte")