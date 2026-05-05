from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeNegocio, RecursoNoEncontrado
from app.models import (
    AsignacionRolPermiso,
    AsignacionUsuarioRol,
    Permiso,
    Rol,
    RolContradictorio,
)


def asignar_permisos_a_rol(
    db: Session,
    rol_id: int,
    permiso_ids: List[int],
    asignado_por_usuario_id: int,
) -> List[AsignacionRolPermiso]:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")

    permisos = db.query(Permiso).filter(Permiso.id.in_(permiso_ids)).all()
    permisos_disponibles = {permiso.id for permiso in permisos}
    faltantes = [permiso_id for permiso_id in permiso_ids if permiso_id not in permisos_disponibles]
    if faltantes:
        raise RecursoNoEncontrado(
            f"Permisos no encontrados: {faltantes}."
        )

    existentes = db.query(AsignacionRolPermiso).filter(
        AsignacionRolPermiso.rol_id == rol_id,
        AsignacionRolPermiso.permiso_id.in_(permiso_ids),
    ).all()
    existentes_ids = {asignacion.permiso_id for asignacion in existentes}

    creadas: List[AsignacionRolPermiso] = []
    for permiso_id in permiso_ids:
        if permiso_id in existentes_ids:
            continue
        asignacion = AsignacionRolPermiso(
            rol_id=rol_id,
            permiso_id=permiso_id,
            asignado_por_usuario_id=asignado_por_usuario_id,
        )
        db.add(asignacion)
        creadas.append(asignacion)

    if creadas:
        db.commit()
        for asignacion in creadas:
            db.refresh(asignacion)

    return creadas


def remover_permiso_de_rol(db: Session, rol_id: int, permiso_id: int) -> None:
    asignacion = db.query(AsignacionRolPermiso).filter(
        AsignacionRolPermiso.rol_id == rol_id,
        AsignacionRolPermiso.permiso_id == permiso_id,
    ).first()
    if asignacion is None:
        raise RecursoNoEncontrado(
            f"No existe la asignación del permiso {permiso_id} al rol {rol_id}."
        )

    db.delete(asignacion)
    db.commit()


def obtener_roles_de_permiso(db: Session, permiso_id: int) -> List[Rol]:
    permiso = db.get(Permiso, permiso_id)
    if permiso is None:
        raise RecursoNoEncontrado(f"Permiso con id {permiso_id} no encontrado.")

    return (
        db.query(Rol)
        .join(AsignacionRolPermiso, AsignacionRolPermiso.rol_id == Rol.id)
        .filter(AsignacionRolPermiso.permiso_id == permiso_id)
        .order_by(Rol.nombre)
        .all()
    )


def obtener_usuarios_de_rol(db: Session, rol_id: int) -> List[AsignacionUsuarioRol]:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")

    return (
        db.query(AsignacionUsuarioRol)
        .filter(
            AsignacionUsuarioRol.rol_id == rol_id,
            AsignacionUsuarioRol.estado == "activo",
        )
        .all()
    )


def asignar_permiso_a_rol(
    db: Session,
    rol_id: int,
    permiso_id: int,
    asignado_por_usuario_id: int,
) -> AsignacionRolPermiso:
    """
    Asigna un solo permiso a un rol.
    """
    asignaciones = asignar_permisos_a_rol(db, rol_id, [permiso_id], asignado_por_usuario_id)
    return asignaciones[0] if asignaciones else None


def asignar_rol_a_usuario(
    db: Session,
    usuario_id: int,
    rol_id: int,
    asignado_por_usuario_id: int,
) -> AsignacionUsuarioRol:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")
    if rol.estado != "activo":
        raise ConflictoDeNegocio(f"No se puede asignar el rol inactivo '{rol.nombre}'.")

    asignacion_existente = db.query(AsignacionUsuarioRol).filter(
        AsignacionUsuarioRol.usuario_id == usuario_id,
        AsignacionUsuarioRol.rol_id == rol_id,
        AsignacionUsuarioRol.estado == "activo",
    ).first()
    if asignacion_existente is not None:
        raise ConflictoDeNegocio(
            f"El usuario {usuario_id} ya tiene asignado el rol '{rol.nombre}'."
        )

    roles_activos_usuario = db.query(AsignacionUsuarioRol).filter(
        AsignacionUsuarioRol.usuario_id == usuario_id,
        AsignacionUsuarioRol.estado == "activo",
    ).all()
    role_ids_activos = [asignacion.rol_id for asignacion in roles_activos_usuario]

    if role_ids_activos:
        contradictorio = db.query(RolContradictorio).filter(
            or_(
                (RolContradictorio.rol_a_id == rol_id) & (RolContradictorio.rol_b_id.in_(role_ids_activos)),
                (RolContradictorio.rol_b_id == rol_id) & (RolContradictorio.rol_a_id.in_(role_ids_activos)),
            )
        ).first()
        if contradictorio is not None:
            raise ConflictoDeNegocio(
                "No se puede asignar el rol porque entra en conflicto con otro rol activo del usuario."
            )

    asignacion = AsignacionUsuarioRol(
        usuario_id=usuario_id,
        rol_id=rol_id,
        estado="activo",
        asignado_por_usuario_id=asignado_por_usuario_id,
    )
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def listar_roles_de_usuario(db: Session, usuario_id: int) -> List[AsignacionUsuarioRol]:
    return (
        db.query(AsignacionUsuarioRol)
        .filter(
            AsignacionUsuarioRol.usuario_id == usuario_id,
            AsignacionUsuarioRol.estado == "activo",
        )
        .all()
    )


def remover_rol_de_usuario(db: Session, usuario_id: int, rol_id: int) -> AsignacionUsuarioRol:
    asignacion = db.query(AsignacionUsuarioRol).filter(
        AsignacionUsuarioRol.usuario_id == usuario_id,
        AsignacionUsuarioRol.rol_id == rol_id,
        AsignacionUsuarioRol.estado == "activo",
    ).first()
    if asignacion is None:
        raise RecursoNoEncontrado(
            f"No existe una asignación activa del rol {rol_id} para el usuario {usuario_id}."
        )

    asignacion.estado = "inactivo"
    db.commit()
    db.refresh(asignacion)
    return asignacion


def reactivar_asignacion_usuario_rol(
    db: Session,
    usuario_id: int,
    rol_id: int,
    asignado_por_usuario_id: int,
) -> AsignacionUsuarioRol:
    asignacion = db.query(AsignacionUsuarioRol).filter(
        AsignacionUsuarioRol.usuario_id == usuario_id,
        AsignacionUsuarioRol.rol_id == rol_id,
        AsignacionUsuarioRol.estado == "inactivo",
    ).first()
    if asignacion is None:
        raise RecursoNoEncontrado(
            f"No existe una asignación inactiva del rol {rol_id} para el usuario {usuario_id}."
        )

    roles_activos_usuario = db.query(AsignacionUsuarioRol).filter(
        AsignacionUsuarioRol.usuario_id == usuario_id,
        AsignacionUsuarioRol.estado == "activo",
    ).all()
    role_ids_activos = [item.rol_id for item in roles_activos_usuario]

    contradiction = db.query(RolContradictorio).filter(
        or_(
            (RolContradictorio.rol_a_id == rol_id) & (RolContradictorio.rol_b_id.in_(role_ids_activos)),
            (RolContradictorio.rol_b_id == rol_id) & (RolContradictorio.rol_a_id.in_(role_ids_activos)),
        )
    ).first()
    if contradiction is not None:
        raise ConflictoDeNegocio(
            "No se puede reactivar la asignación porque el rol entra en conflicto con otro rol activo del usuario."
        )

    asignacion.estado = "activo"
    asignacion.asignado_por_usuario_id = asignado_por_usuario_id
    db.commit()
    db.refresh(asignacion)
    return asignacion


def obtener_permisos_de_rol(db: Session, rol_id: int) -> List[Permiso]:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")

    return (
        db.query(Permiso)
        .join(AsignacionRolPermiso, AsignacionRolPermiso.permiso_id == Permiso.id)
        .filter(AsignacionRolPermiso.rol_id == rol_id)
        .order_by(Permiso.codigo)
        .all()
    )


def obtener_roles_de_permiso(db: Session, permiso_id: int) -> List[Rol]:
    permiso = db.get(Permiso, permiso_id)
    if permiso is None:
        raise RecursoNoEncontrado(f"Permiso con id {permiso_id} no encontrado.")

    return (
        db.query(Rol)
        .join(AsignacionRolPermiso, AsignacionRolPermiso.rol_id == Rol.id)
        .filter(AsignacionRolPermiso.permiso_id == permiso_id)
        .order_by(Rol.nombre)
        .all()
    )


def obtener_usuarios_de_rol(db: Session, rol_id: int) -> List[AsignacionUsuarioRol]:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")

    return (
        db.query(AsignacionUsuarioRol)
        .filter(
            AsignacionUsuarioRol.rol_id == rol_id,
            AsignacionUsuarioRol.estado == "activo",
        )
        .all()
    )


def asignar_permiso_a_rol(
    db: Session,
    rol_id: int,
    permiso_id: int,
    asignado_por_usuario_id: int,
) -> AsignacionRolPermiso:
    """
    Asigna un solo permiso a un rol.
    """
    asignaciones = asignar_permisos_a_rol(db, rol_id, [permiso_id], asignado_por_usuario_id)
    return asignaciones[0] if asignaciones else None
