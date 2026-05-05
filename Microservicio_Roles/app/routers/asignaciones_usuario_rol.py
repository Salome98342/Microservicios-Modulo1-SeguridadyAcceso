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
    asignar_rol_a_usuario,
    remover_rol_de_usuario,
    listar_roles_de_usuario,
    obtener_usuarios_de_rol,
)
from app.schemas.asignacion import AsignacionUsuarioRolCreate, AsignacionUsuarioRolResponse
from app.core.response import build_response
from app.core.audit import log_auditoria

router = APIRouter(prefix="/asignaciones/usuario-rol", tags=["asignaciones-usuario-rol"])


@router.post("/")
async def asignar_rol_a_usuario_endpoint(
    asignacion_data: AsignacionUsuarioRolCreate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_ASSIGN_USER", usuario, request_id)

    try:
        asignacion = asignar_rol_a_usuario(db, asignacion_data.usuario_id, asignacion_data.rol_id, usuario.get("usuario_id"))
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="ASIGNAR_ROL_USUARIO",
            recurso=f"asignacion_usuario:{asignacion.usuario_id}-{asignacion.rol_id}",
            detalles=f"Rol {asignacion.rol_id} asignado a usuario {asignacion.usuario_id}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Rol asignado al usuario exitosamente",
            data=AsignacionUsuarioRolResponse.from_orm(asignacion),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/")
async def remover_rol_de_usuario_endpoint(
    usuario_id: str,
    rol_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_ASSIGN_USER", usuario, request_id)

    try:
        asignacion = remover_rol_de_usuario(db, usuario_id, rol_id)
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="REMOVER_ROL_USUARIO",
            recurso=f"asignacion_usuario:{usuario_id}-{rol_id}",
            detalles=f"Rol {rol_id} removido de usuario {usuario_id}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Rol removido del usuario exitosamente",
            data=AsignacionUsuarioRolResponse.from_orm(asignacion),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usuario/{usuario_id}")
async def obtener_roles_de_usuario_endpoint(
    usuario_id: str,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_PERM_READ", usuario, request_id)

    roles = listar_roles_de_usuario(db, usuario_id)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_ROLES_USUARIO",
        recurso=f"usuario:{usuario_id}:roles",
        detalles=f"{len(roles)} roles obtenidos para usuario {usuario_id}",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Roles del usuario obtenidos exitosamente",
        data=[
            {
                "id": r.rol.id, 
                # r.rol accede al objeto Rol relacionado mediante la relación ORM
            # definida en AsignacionUsuarioRol como:
            #   rol = relationship("Rol", back_populates="asignaciones_usuarios")
            # Sin el .rol estaríamos accediendo a atributos de la asignación
            # (que no tiene .nombre ni .descripcion), no del rol en sí.
                "nombre": r.rol.nombre, 
                "descripcion": r.rol.descripcion,
                "estado": r.estado
            } 
            for r in roles
            ],
    )


@router.get("/rol/{rol_id}")
async def obtener_usuarios_de_rol_endpoint(
    rol_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_PERM_READ", usuario, request_id)

    usuarios = obtener_usuarios_de_rol(db, rol_id)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_USUARIOS_ROL",
        recurso=f"rol:{rol_id}:usuarios",
        detalles=f"{len(usuarios)} usuarios obtenidos para rol {rol_id}",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Usuarios del rol obtenidos exitosamente",
        data=[{"usuario_id": u.usuario_id} for u in usuarios],
    )