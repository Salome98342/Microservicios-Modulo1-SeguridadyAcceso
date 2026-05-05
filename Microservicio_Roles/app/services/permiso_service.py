"""Business logic for permission management in ms-roles.

This module handles creation, lookup, listing, updating, and deletion of
permissions in the ms-roles service. It ensures that permission codes are
unique, operation methods are normalized, and permissions assigned to roles
cannot be deleted without first removing the assignment.

Usage in the system:
- `crear_permiso` is called by the permissions router when a new permission is created.
- `listar_permisos` and `listar_permisos_por_modulo` are used to serve read operations.
- `actualizar_permiso` validates partial updates from API requests.
- `eliminar_permiso` enforces business rules before deleting records.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeNegocio, RecursoNoEncontrado
from app.models import AsignacionRolPermiso, Permiso
from app.schemas.permiso import PermisoCreate, PermisoUpdate

_VALID_OPERACIONES = {
    "consulta",
    "creacion",
    "actualizacion",
    "eliminacion",
}

_OPERACION_MAP = {
    "READ": "consulta",
    "CREATE": "creacion",
    "UPDATE": "actualizacion",
    "DELETE": "eliminacion",
    "CONSULTA": "consulta",
    "CREACION": "creacion",
    "ACTUALIZACION": "actualizacion",
    "ELIMINACION": "eliminacion",
}


def _normalizar_metodo_operacion(valor: str) -> str:
    """Normaliza la operación recibida a los valores internos del sistema.

    Acepta valores en inglés (READ, CREATE, UPDATE, DELETE) o en español.
    Retorna uno de los valores esperados por el modelo `Permiso`.
    """
    if valor is None:
        return valor
    operacion = valor.strip().upper()
    return _OPERACION_MAP.get(operacion, valor.strip().lower())


def crear_permiso(db: Session, permiso_data: PermisoCreate) -> Permiso:
    """Crea un nuevo permiso si no existe un código duplicado.

    Normaliza el código y el método de operación antes de persistir.
    Lanza `ConflictoDeNegocio` si el código ya existe o el método es inválido.
    """
    codigo_normalizado = permiso_data.codigo.strip().upper()
    if db.query(Permiso).filter(Permiso.codigo == codigo_normalizado).first():
        raise ConflictoDeNegocio(
            f"Ya existe un permiso con el código '{codigo_normalizado}'."
        )

    metodo_operacion = _normalizar_metodo_operacion(permiso_data.metodo_operacion)
    if metodo_operacion not in _VALID_OPERACIONES:
        raise ConflictoDeNegocio(
            f"El valor '{permiso_data.metodo_operacion}' no es un metodo_operacion válido."
        )

    permiso = Permiso(
        codigo=codigo_normalizado,
        nombre=permiso_data.nombre.strip(),
        descripcion=permiso_data.descripcion,
        modulo=permiso_data.modulo.strip(),
        microservicio_origen=permiso_data.microservicio_origen.strip(),
        funcionalidad_asociada=permiso_data.funcionalidad_asociada.strip(),
        metodo_operacion=metodo_operacion,
    )
    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    return permiso


def obtener_permiso_por_id(db: Session, permiso_id: int) -> Permiso:
    """Obtiene un permiso por su identificador interno.

    Utilizado en endpoints de consulta y en la lógica de asignación de permisos.
    """
    permiso = db.get(Permiso, permiso_id)
    if permiso is None:
        raise RecursoNoEncontrado(f"Permiso con id {permiso_id} no encontrado.")
    return permiso


def obtener_permiso_por_codigo(db: Session, codigo: str) -> Permiso:
    """Busca un permiso por su código único.

    Usado en validaciones de negocio y en operaciones de asignación de permisos a roles.
    """
    permiso = db.query(Permiso).filter(Permiso.codigo == codigo.strip().upper()).first()
    if permiso is None:
        raise RecursoNoEncontrado(f"Permiso con código '{codigo}' no encontrado.")
    return permiso


def listar_permisos(
    db: Session,
    codigo: Optional[str] = None,
    modulo: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Permiso]:
    """Lista permisos con filtros opcionales de código y módulo.

    Esta función se utiliza para los endpoints de consulta y para filtros
    internos cuando se requiere paginación simple.
    """
    query = db.query(Permiso)
    if codigo is not None:
        query = query.filter(Permiso.codigo == codigo.strip().upper())
    if modulo is not None:
        query = query.filter(Permiso.modulo == modulo.strip())
    return query.offset(skip).limit(limit).all()


def listar_permisos_por_modulo(db: Session) -> List[Dict[str, object]]:
    """Agrupa los permisos por módulo y devuelve el total por grupo.

    Este agrupamiento es útil para vistas administrativas que muestran el
    catálogo de permisos organizados por módulo.
    """
    permisos = db.query(Permiso).order_by(Permiso.modulo, Permiso.codigo).all()
    grupos: Dict[str, Dict[str, object]] = {}

    for permiso in permisos:
        modulo = permiso.modulo
        if modulo not in grupos:
            grupos[modulo] = {
                "modulo": modulo,
                "total": 0,
                "permisos": [],
            }
        grupos[modulo]["permisos"].append(permiso)
        grupos[modulo]["total"] += 1

    return list(grupos.values())


def actualizar_permiso(db: Session, permiso: Permiso, permiso_data: PermisoUpdate) -> Permiso:
    """Actualiza los campos editables de un permiso existente.

    Valida los valores de operación y solo modifica los campos proporcionados.
    """
    if permiso_data.nombre is not None:
        permiso.nombre = permiso_data.nombre.strip()

    if permiso_data.descripcion is not None:
        permiso.descripcion = permiso_data.descripcion

    if permiso_data.modulo is not None:
        permiso.modulo = permiso_data.modulo.strip()

    if permiso_data.microservicio_origen is not None:
        permiso.microservicio_origen = permiso_data.microservicio_origen.strip()

    if permiso_data.funcionalidad_asociada is not None:
        permiso.funcionalidad_asociada = permiso_data.funcionalidad_asociada.strip()

    if permiso_data.metodo_operacion is not None:
        metodo_operacion = _normalizar_metodo_operacion(permiso_data.metodo_operacion)
        if metodo_operacion not in _VALID_OPERACIONES:
            raise ConflictoDeNegocio(
                f"El valor '{permiso_data.metodo_operacion}' no es un metodo_operacion válido."
            )
        permiso.metodo_operacion = metodo_operacion

    db.commit()
    db.refresh(permiso)
    return permiso


def eliminar_permiso(db: Session, permiso: Permiso) -> None:
    """Elimina un permiso si no está asignado a ningún rol activo.

    Esta regla de negocio evita inconsistencias en el catálogo de permisos.
    """
    asignaciones = db.query(AsignacionRolPermiso).filter(
        AsignacionRolPermiso.permiso_id == permiso.id
    ).first()
    if asignaciones is not None:
        raise ConflictoDeNegocio(
            "No se puede eliminar un permiso que ya está asignado a un rol."
        )

    db.delete(permiso)
    db.commit()
