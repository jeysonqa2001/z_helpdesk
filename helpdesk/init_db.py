from flask_appbuilder import Model
from app import app, db
from app.models import Departamento, Categoria, Prioridad, Estado


def init_db():
    with app.app_context():
        Model.metadata.create_all(db.engine)
        print("✅ Tablas creadas correctamente en MySQL")

        if db.session.query(Estado).first():
            print("ℹ️ Los datos iniciales ya existen")
            return

        db.session.add_all([
            Estado(nombre="Abierto", es_cerrado=False),
            Estado(nombre="En progreso", es_cerrado=False),
            Estado(nombre="Resuelto", es_cerrado=True),
            Estado(nombre="Cerrado", es_cerrado=True),
            Prioridad(nombre="Baja", horas_sla=72),
            Prioridad(nombre="Media", horas_sla=48),
            Prioridad(nombre="Alta", horas_sla=24),
            Prioridad(nombre="Crítica", horas_sla=4),
        ])
        soporte = Departamento(nombre="Soporte técnico", descripcion="Hardware y software")
        redes = Departamento(nombre="Redes", descripcion="Conectividad e infraestructura")
        db.session.add_all([soporte, redes])
        db.session.commit()

        db.session.add_all([
            Categoria(nombre="Computadoras", departamento_id=soporte.id),
            Categoria(nombre="Impresoras", departamento_id=soporte.id),
            Categoria(nombre="Internet / WiFi", departamento_id=redes.id),
            Categoria(nombre="VPN", departamento_id=redes.id),
        ])
        db.session.commit()
        print("✅ Datos iniciales cargados")


if __name__ == "__main__":
    init_db()