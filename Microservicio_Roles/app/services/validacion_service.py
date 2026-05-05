"""Validation services used by ms-roles to verify role and permission relationships.

This module provides the logic for checking if a role exists, if it is active,
and whether it has a specific permission assigned. It supports both numeric ID
and name-based identifiers for flexibility in API calls.
"""

from typing import Any, Optional, Tuple, Union

from sqlalchemy.orm import Session

from app.models import AsignacionRolPermiso, Permiso, Rol


def _obtener_rol_por_identificador(
    db: Session,
    rol_identificador: Union[int, str],
) -> Optional[Rol]:
    """Resuelve un rol por ID numérico o por nombre.

    Este helper permite que los endpoints de validación acepten tanto
    identificadores numéricos como nombres legibles.
    """
    if isinstance(rol_identificador, int) or (
        isinstance(rol_identificador, str) and rol_identificador.isdigit()
    ):
        rol = db.get(Rol, int(rol_identificador))
        if rol is not None:
            return rol

    return db.query(Rol).filter(Rol.nombre == str(rol_identificador).strip()).first()


def _obtener_permiso_por_identificador(
    db: Session,
    permiso_identificador: Union[int, str],
) -> Optional[Permiso]:
    """Resuelve un permiso por ID numérico o por código.

    Soporta búsquedas con el ID interno del permiso o con el código único.
    """
    if isinstance(permiso_identificador, int) or (
        isinstance(permiso_identificador, str) and permiso_identificador.isdigit()
    ):
        permiso = db.get(Permiso, int(permiso_identificador))
        if permiso is not None:
            return permiso

    return db.query(Permiso).filter(
        Permiso.codigo == str(permiso_identificador).strip().upper()
    ).first()


def validar_permiso_de_rol(
    db: Session,
    rol_identificador: Union[int, str],
    permiso_identificador: Union[int, str],
) -> bool:
    """Valida si un rol activo tiene asignado un permiso específico.

    Regresa `True` cuando el rol existe, está activo y el permiso está asignado.
    Esta función es clave para la autorización interna de ms-roles.
    Soporta tanto identificadores numéricos como nombres/códigos.
    """
    rol = _obtener_rol_por_identificador(db, rol_identificador)
    if rol is None or rol.estado != "activo":
        return False

    permiso = _obtener_permiso_por_identificador(db, permiso_identificador)
    if permiso is None:
        return False

    asignacion = db.query(AsignacionRolPermiso).filter(
        AsignacionRolPermiso.rol_id == rol.id,
        AsignacionRolPermiso.permiso_id == permiso.id,
    ).first()
    return asignacion is not None


def verificar_existencia_rol(
    db: Session,
    rol_identificador: Union[int, str],
) -> Tuple[bool, bool]:
    """Verifica si un rol existe y si está activo.

    Retorna una tupla `(existe, activo)` usada por los endpoints de validación.
    """
    rol = _obtener_rol_por_identificador(db, rol_identificador)
    if rol is None:
        return False, False
    return True, rol.estado == "activo"
