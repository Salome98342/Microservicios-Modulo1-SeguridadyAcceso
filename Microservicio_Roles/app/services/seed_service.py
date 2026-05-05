"""Seed data loader for initial ms-roles configuration.

This module creates foundational roles, permissions, role-permission assignments,
and trusted application tokens required for the service to start with a valid
security baseline.

Usage in the system:
- `cargar_datos_semilla` is called from startup scripts or a protected seed endpoint.
- It is idempotent and safe to run multiple times without duplicating data.
"""

from typing import Dict, List

from app.core.security import generar_token_aplicacion
from app.models import (
    AsignacionRolPermiso,
    Permiso,
    Rol,
    RolContradictorio,
    TokenAplicacion,
)
from app.schemas.permiso import PermisoCreate
from app.schemas.rol import RolCreate


def _asegurar_token_aplicacion(
    db,
    nombre_servicio: str,
    descripcion: str,
) -> bool:
    """Crea un token de aplicación si aún no existe.

    Se utiliza para registrar credenciales confiables entre microservicios.
    """
    registro = db.query(TokenAplicacion).filter(
        TokenAplicacion.nombre_servicio == nombre_servicio
    ).first()
    if registro is not None:
        return False

    _, token_cifrado = generar_token_aplicacion()
    registro = TokenAplicacion(
        nombre_servicio=nombre_servicio,
        token_cifrado=token_cifrado,
        descripcion=descripcion,
        estado="activo",
        actualizado_por_usuario_id=None,
    )
    db.add(registro)
    db.commit()
    return True


def cargar_datos_semilla(db) -> Dict[str, int]:
    """Carga datos semilla iniciales para ms-roles.

    Genera roles base, permisos básicos, asignaciones por rol,
    contradicciones de roles y tokens de aplicación.
    Retorna un resumen de los elementos creados.
    """
    resumen = {
        "roles_creados": 0,
        "permisos_creados": 0,
        "asignaciones_creadas": 0,
        "roles_contradictorios_creados": 0,
        "token_aplicacion_creado": False,
    }

    roles_base: List[RolCreate] = [
        RolCreate(nombre="ADMIN", descripcion="Rol con acceso total al sistema."),
        RolCreate(nombre="USUARIO", descripcion="Rol para usuarios generales."),
        RolCreate(nombre="MODERADOR", descripcion="Rol para gestión moderada del sistema."),
    ]

    for rol_payload in roles_base:
        if db.query(Rol).filter(Rol.nombre == rol_payload.nombre).first() is None:
            rol = Rol(
                nombre=rol_payload.nombre,
                descripcion=rol_payload.descripcion,
                estado="activo",
            )
            db.add(rol)
            resumen["roles_creados"] += 1

    db.commit()

    permisos_base: List[PermisoCreate] = [
        PermisoCreate(
            codigo="ROL_CREATE",
            nombre="Crear roles",
            descripcion="Permite crear nuevos roles en el sistema.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Crear roles",
            metodo_operacion="creacion",
        ),
        PermisoCreate(
            codigo="ROL_READ",
            nombre="Consultar roles",
            descripcion="Permite ver los roles registrados en el sistema.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Consultar roles",
            metodo_operacion="consulta",
        ),
        PermisoCreate(
            codigo="ROL_UPDATE",
            nombre="Actualizar roles",
            descripcion="Permite modificar datos de un rol existente.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Actualizar roles",
            metodo_operacion="actualizacion",
        ),
        PermisoCreate(
            codigo="ROL_DELETE",
            nombre="Desactivar roles",
            descripcion="Permite desactivar roles del sistema.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Desactivar roles",
            metodo_operacion="eliminacion",
        ),
        PermisoCreate(
            codigo="PERM_CREATE",
            nombre="Registrar permisos",
            descripcion="Permite crear nuevos códigos de permiso.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Registrar permisos",
            metodo_operacion="creacion",
        ),
        PermisoCreate(
            codigo="PERM_READ",
            nombre="Consultar permisos",
            descripcion="Permite listar y consultar permisos del sistema.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Consultar permisos",
            metodo_operacion="consulta",
        ),
        PermisoCreate(
            codigo="PERM_UPDATE",
            nombre="Actualizar permisos",
            descripcion="Permite modificar datos descriptivos de un permiso.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Actualizar permisos",
            metodo_operacion="actualizacion",
        ),
        PermisoCreate(
            codigo="PERM_DELETE",
            nombre="Eliminar permisos",
            descripcion="Permite eliminar permisos no usados.",
            modulo="Seguridad y Acceso",
            microservicio_origen="ms-roles",
            funcionalidad_asociada="Eliminar permisos",
            metodo_operacion="eliminacion",
        ),
    ]

    for permiso_payload in permisos_base:
        if db.query(Permiso).filter(Permiso.codigo == permiso_payload.codigo).first() is None:
            permiso = Permiso(
                codigo=permiso_payload.codigo,
                nombre=permiso_payload.nombre,
                descripcion=permiso_payload.descripcion,
                modulo=permiso_payload.modulo,
                microservicio_origen=permiso_payload.microservicio_origen,
                funcionalidad_asociada=permiso_payload.funcionalidad_asociada,
                metodo_operacion=permiso_payload.metodo_operacion,
            )
            db.add(permiso)
            resumen["permisos_creados"] += 1

    db.commit()

    asignaciones_por_rol = {
        "ADMIN": [
            "ROL_CREATE",
            "ROL_READ",
            "ROL_UPDATE",
            "ROL_DELETE",
            "PERM_CREATE",
            "PERM_READ",
            "PERM_UPDATE",
            "PERM_DELETE",
        ],
        "USUARIO": ["ROL_READ", "PERM_READ"],
        "MODERADOR": ["ROL_READ"],
    }

    for nombre_rol, codigos in asignaciones_por_rol.items():
        rol = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
        if rol is None:
            continue

        for codigo in codigos:
            permiso = db.query(Permiso).filter(Permiso.codigo == codigo).first()
            if permiso is None:
                continue
            existe = db.query(AsignacionRolPermiso).filter(
                AsignacionRolPermiso.rol_id == rol.id,
                AsignacionRolPermiso.permiso_id == permiso.id,
            ).first()
            if existe is None:
                db.add(
                    AsignacionRolPermiso(
                        rol_id=rol.id,
                        permiso_id=permiso.id,
                        asignado_por_usuario_id=0,
                    )
                )
                resumen["asignaciones_creadas"] += 1

    db.commit()

    roles_contradicciones: List[tuple[str, str, str]] = [
        ("USUARIO", "MODERADOR", "No puede combinarse con roles de usuario final."),
        ("USUARIO", "ADMIN", "Roles operativos y administrativos no pueden coexistir."),
        ("MODERADOR", "ADMIN", "Roles de moderador y administrador son incompatibles."),
        ("ADMIN", "USUARIO", "El rol Administrador no debe mezclarse con el rol Usuario."),
    ]

    for rol_a_nombre, rol_b_nombre, motivo in roles_contradicciones:
        rol_a = db.query(Rol).filter(Rol.nombre == rol_a_nombre).first()
        rol_b = db.query(Rol).filter(Rol.nombre == rol_b_nombre).first()
        if rol_a is None or rol_b is None:
            continue

        existe = db.query(RolContradictorio).filter(
            ((RolContradictorio.rol_a_id == rol_a.id) & (RolContradictorio.rol_b_id == rol_b.id))
            | ((RolContradictorio.rol_a_id == rol_b.id) & (RolContradictorio.rol_b_id == rol_a.id))
        ).first()
        if existe is None:
            db.add(
                RolContradictorio(
                    rol_a_id=rol_a.id,
                    rol_b_id=rol_b.id,
                    motivo=motivo,
                )
            )
            resumen["roles_contradictorios_creados"] += 1

    db.commit()

    if _asegurar_token_aplicacion(db, "ms-roles", "Token de aplicación propio de ms-roles."):
        resumen["token_aplicacion_creado"] = True
    if _asegurar_token_aplicacion(db, "ms-autenticacion", "Token de aplicación de confianza mutua con ms-autenticacion."):
        resumen["token_aplicacion_creado"] = True

    return resumen
