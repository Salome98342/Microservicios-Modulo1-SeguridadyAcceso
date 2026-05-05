from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeNegocio, RecursoNoEncontrado
from app.models import Rol
from app.schemas.rol import RolCreate, RolUpdate


def crear_rol(db: Session, rol_data: RolCreate) -> Rol:
    nombre_normalizado = rol_data.nombre.strip()
    if db.query(Rol).filter(Rol.nombre == nombre_normalizado).first():
        raise ConflictoDeNegocio(
            f"Ya existe un rol con el nombre '{nombre_normalizado}'."
        )

    rol = Rol(
        nombre=nombre_normalizado,
        descripcion=rol_data.descripcion,
        estado=rol_data.estado,
    )
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


def obtener_rol_por_id(db: Session, rol_id: int) -> Rol:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con id {rol_id} no encontrado.")
    return rol


def obtener_rol_por_nombre(db: Session, nombre: str) -> Rol:
    rol = db.query(Rol).filter(Rol.nombre == nombre.strip()).first()
    if rol is None:
        raise RecursoNoEncontrado(f"Rol con nombre '{nombre}' no encontrado.")
    return rol


def listar_roles(
    db: Session,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Rol]:
    query = db.query(Rol)
    if estado is not None:
        query = query.filter(Rol.estado == estado)
    return query.offset(skip).limit(limit).all()


def listar_roles_activos(db: Session) -> List[Rol]:
    return db.query(Rol).filter(Rol.estado == "activo").all()


def actualizar_rol(db: Session, rol: Rol, rol_data: RolUpdate) -> Rol:
    if rol_data.nombre:
        nombre_normalizado = rol_data.nombre.strip()
        if nombre_normalizado != rol.nombre:
            if db.query(Rol).filter(Rol.nombre == nombre_normalizado).first():
                raise ConflictoDeNegocio(
                    f"Ya existe un rol con el nombre '{nombre_normalizado}'."
                )
            rol.nombre = nombre_normalizado

    if rol_data.descripcion is not None:
        rol.descripcion = rol_data.descripcion

    if rol_data.estado is not None:
        rol.estado = rol_data.estado

    db.commit()
    db.refresh(rol)
    return rol


def desactivar_rol(db: Session, rol: Rol) -> Rol:
    if rol.estado == "inactivo":
        return rol
    rol.estado = "inactivo"
    db.commit()
    db.refresh(rol)
    return rol


def reactivar_rol(db: Session, rol: Rol) -> Rol:
    if rol.estado == "activo":
        return rol
    rol.estado = "activo"
    db.commit()
    db.refresh(rol)
    return rol


def existe_rol_activo(db: Session, rol_id: int) -> bool:
    return (
        db.query(Rol)
        .filter(Rol.id == rol_id, Rol.estado == "activo")
        .first()
        is not None
    )
