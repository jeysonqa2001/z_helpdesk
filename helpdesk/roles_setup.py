from app import app, appbuilder, db

VISTAS_BASE = [
    ("can_userinfo", "UserDBModelView"),
    ("can_userinfoedit", "UserDBModelView"),
    ("resetmypassword", "UserDBModelView"),
    ("can_this_form_get", "ResetMyPasswordView"),
    ("can_this_form_post", "ResetMyPasswordView"),
    ("can_this_form_get", "UserInfoEditView"),
    ("can_this_form_post", "UserInfoEditView"),
    ("can_get", "MenuApi"),
]

SOLICITANTE = VISTAS_BASE + [
    ("can_add", "VistaTicket"),
    ("can_list", "VistaTicket"),
    ("can_show", "VistaTicket"),
    ("can_add", "VistaComentario"),
    ("can_list", "VistaComentario"),
    ("can_show", "VistaComentario"),
    ("menu_access", "Soporte"),
    ("menu_access", "Tickets"),
    ("menu_access", "Comentarios"),
]

TECNICO = VISTAS_BASE + [
    (p, v) for v in ("VistaTicket", "VistaComentario")
    for p in ("can_add", "can_list", "can_edit", "can_show")
] + [
    ("analizar_ia", "VistaTicket"),
    ("can_por_estado", "VistaReportes"),
    ("can_por_agente", "VistaReportes"),
    ("can_por_departamento", "VistaReportes"),
    ("menu_access", "Soporte"),
    ("menu_access", "Tickets"),
    ("menu_access", "Comentarios"),
    ("menu_access", "Reportes"),
    ("menu_access", "Por estado y prioridad"),
    ("menu_access", "Por agente"),
    ("menu_access", "Por departamento"),
]


def configurar(nombre_rol, permisos):
    sm = appbuilder.sm
    rol = sm.find_role(nombre_rol) or sm.add_role(nombre_rol)
    rol.permissions = []          # limpia lo que tenía
    db.session.commit()
    faltantes = []
    for permiso, vista in permisos:
        pv = sm.find_permission_view_menu(permiso, vista)
        if pv:
            sm.add_permission_role(rol, pv)
        else:
            faltantes.append((permiso, vista))
    print(f"✅ {nombre_rol}: {len(permisos) - len(faltantes)} permisos asignados")
    for f in faltantes:
        print("   ⚠️ No existe:", f)


with app.app_context():
    configurar("Solicitante", SOLICITANTE)
    configurar("Tecnico", TECNICO)