from fastapi import APIRouter, HTTPException, Header, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AsignacionRolPermiso, AsignacionUsuarioRol, Permiso


router = APIRouter(prefix="/internal/roles", tags=["internal-roles"])


@router.get("/users/{user_id}/permissions")
async def obtener_rol_y_permisos_de_usuario(
    user_id: str,
    request_trace_id: str = Header(default="", alias="request_trace_id"),
    db: Session = Depends(get_db),
):
    if not user_id.isdigit():
        raise HTTPException(status_code=404, detail="Usuario sin rol asignado")

    asignacion = (
        db.query(AsignacionUsuarioRol)
        .join(AsignacionUsuarioRol.rol)
        .filter(
            AsignacionUsuarioRol.usuario_id == int(user_id),
            AsignacionUsuarioRol.estado == "activo",
        )
        .order_by(AsignacionUsuarioRol.fecha_asignacion.desc())
        .first()
    )

    if asignacion is None or asignacion.rol is None or asignacion.rol.estado != "activo":
        raise HTTPException(status_code=404, detail="Usuario sin rol asignado")

    permisos = (
        db.query(Permiso.codigo)
        .join(AsignacionRolPermiso, AsignacionRolPermiso.permiso_id == Permiso.id)
        .filter(AsignacionRolPermiso.rol_id == asignacion.rol_id)
        .order_by(Permiso.codigo.asc())
        .all()
    )

    return {
        "role": asignacion.rol.nombre,
        "permissions": [codigo for (codigo,) in permisos],
        "request_trace_id": request_trace_id,
    }