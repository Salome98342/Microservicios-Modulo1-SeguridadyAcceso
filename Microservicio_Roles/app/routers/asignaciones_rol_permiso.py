from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import (
    dep_request_id,
    dep_usuario_activo,
    dep_verificar_permiso,
    get_db,
    dep_inicio_tiempo,
    calcular_duracion_ms,
)
from app.services.asignacion_service import (
    asignar_permiso_a_rol,
    remover_permiso_de_rol,
    obtener_permisos_de_rol,
    obtener_roles_de_permiso,
)
from app.schemas.asignacion import AsignacionRolPermisoCreate, AsignacionRolPermisoResponse
from app.core.response import build_response
from app.core.audit import log_auditoria

router = APIRouter(prefix="/asignaciones/rol-permiso", tags=["asignaciones-rol-permiso"])


@router.post("/")
async def asignar_permiso_a_rol_endpoint(
    asignacion_data: AsignacionRolPermisoCreate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_ASSIGN_PERM", usuario, request_id)

    try:
        asignacion = asignar_permiso_a_rol(db, asignacion_data.rol_id, asignacion_data.permiso_id, usuario.get("usuario_id"))
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="ASIGNAR_PERMISO_ROL",
            recurso=f"asignacion:{asignacion.rol_id}-{asignacion.permiso_id}",
            detalles=f"Permiso {asignacion.permiso_id} asignado a rol {asignacion.rol_id}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Permiso asignado al rol exitosamente",
            data=AsignacionRolPermisoResponse.from_orm(asignacion),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/")
async def remover_permiso_de_rol_endpoint(
    rol_id: int,
    permiso_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_ASSIGN_PERM", usuario, request_id)

    try:
        asignacion = remover_permiso_de_rol(db, rol_id, permiso_id)
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="REMOVER_PERMISO_ROL",
            recurso=f"asignacion:{rol_id}-{permiso_id}",
            detalles=f"Permiso {permiso_id} removido de rol {rol_id}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Permiso removido del rol exitosamente",
            data=AsignacionRolPermisoResponse.from_orm(asignacion),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rol/{rol_id}")
async def obtener_permisos_de_rol_endpoint(
    rol_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_PERM_READ", usuario, request_id)

    permisos = obtener_permisos_de_rol(db, rol_id)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_PERMISOS_ROL",
        recurso=f"rol:{rol_id}:permisos",
        detalles=f"{len(permisos)} permisos obtenidos para rol {rol_id}",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permisos del rol obtenidos exitosamente",
        data=[{"id": p.id, "codigo": p.codigo, "nombre": p.nombre, "modulo": p.modulo} for p in permisos],
    )


@router.get("/permiso/{permiso_id}")
async def obtener_roles_de_permiso_endpoint(
    permiso_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_PERM_READ", usuario, request_id)

    roles = obtener_roles_de_permiso(db, permiso_id)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_ROLES_PERMISO",
        recurso=f"permiso:{permiso_id}:roles",
        detalles=f"{len(roles)} roles obtenidos para permiso {permiso_id}",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Roles del permiso obtenidos exitosamente",
        data=[{"id": r.id, "nombre": r.nombre, "descripcion": r.descripcion} for r in roles],
    )