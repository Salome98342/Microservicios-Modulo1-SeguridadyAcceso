from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional


from app.dependencies import (
    dep_request_id,
    dep_usuario_activo,
    dep_verificar_permiso,
    get_db,
    dep_inicio_tiempo,
    calcular_duracion_ms,
)
from app.core.response import build_response
from app.core.audit import log_auditoria
from app.core.security import validar_token_aplicacion
from app.models import AsignacionRolPermiso, AsignacionUsuarioRol, Permiso, Rol, TokenAplicacion
from app.services.rol_service import (
    crear_rol,
    obtener_rol_por_id,
    listar_roles,
    actualizar_rol,
    desactivar_rol,
)
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.services.validacion_service import validar_permiso_de_rol, verificar_existencia_rol

router = APIRouter(prefix="/roles", tags=["roles"])


class ValidarPermisoRequest(BaseModel):
    rol_id: int
    permission_code: str
    request_id: str = ""


def _validar_token_aplicacion_opcional(db: Session, x_app_token: Optional[str]) -> None:
    if not x_app_token:
        return

    token_cifrado_recibido = x_app_token.replace("AES256:", "", 1)
    tokens_activos = db.query(TokenAplicacion).filter(TokenAplicacion.estado == "activo").all()

    for registro in tokens_activos:
        if validar_token_aplicacion(token_cifrado_recibido, registro.token_cifrado):
            return

    raise HTTPException(status_code=401, detail="Token de aplicación inválido o inactivo")


@router.post("/")
async def crear_nuevo_rol(
    rol_data: RolCreate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_CREATE", usuario, request_id)

    try:
        rol = crear_rol(db, rol_data)
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="CREAR_ROL",
            recurso=f"rol:{rol.id}",
            detalles=f"Rol '{rol.nombre}' creado",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Rol creado exitosamente",
            data=RolResponse.from_orm(rol),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def listar_todos_los_roles(
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_READ", usuario, request_id)

    roles = listar_roles(db)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="LISTAR_ROLES",
        recurso="roles",
        detalles=f"{len(roles)} roles listados",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Roles listados exitosamente",
        data=[RolResponse.from_orm(rol) for rol in roles],
    )


@router.get("/{rol_id}")
async def obtener_rol(
    rol_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_READ", usuario, request_id)

    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_ROL",
        recurso=f"rol:{rol_id}",
        detalles=f"Rol '{rol.nombre}' consultado",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Rol obtenido exitosamente",
        data=RolResponse.from_orm(rol),
    )


@router.put("/{rol_id}")
async def actualizar_rol_endpoint(
    rol_id: int,
    rol_data: RolUpdate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_UPDATE", usuario, request_id)

    # Primero buscar el objeto Rol en BD
    rol = obtener_rol_por_id(db, rol_id)

    # Luego pasar el objeto al servicio
    rol_actualizado = actualizar_rol(db, rol, rol_data)
    
    duracion = calcular_duracion_ms(inicio)

    return build_response(
        request_id=request_id,
        success=True,
        message="Rol actualizado exitosamente",
        data=RolResponse.from_orm(rol_actualizado),
    )

@router.delete("/{rol_id}")
async def desactivar_rol_endpoint(
    rol_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("ROL_DELETE", usuario, request_id)

    # Primero buscar el objeto Rol en BD
    rol = obtener_rol_por_id(db, rol_id)

    # Luego pasar el objeto al servicio
    rol_desactivado = desactivar_rol(db, rol)

    duracion = calcular_duracion_ms(inicio)

    return build_response(
        request_id=request_id,
        success=True,
        message="Rol desactivado exitosamente",
        data=RolResponse.from_orm(rol_desactivado),
    )


@router.post("/validate-permission")
async def validar_permiso_para_microservicio(
    payload: ValidarPermisoRequest,
    x_app_token: Optional[str] = Header(default=None, alias="X-App-Token"),
    request_id_header: str = Header(default="", alias="X-Request-ID"),
    db: Session = Depends(get_db),
):
    _validar_token_aplicacion_opcional(db, x_app_token)

    autorizado = validar_permiso_de_rol(db, payload.rol_id, payload.permission_code)
    request_id = payload.request_id or request_id_header

    return build_response(
        request_id=request_id,
        success=True,
        message="Validación de permiso realizada exitosamente",
        data={"authorized": autorizado},
    )


@router.get("/{rol_id}/validate")
async def validar_existencia_rol_para_microservicio(
    rol_id: int,
    x_app_token: Optional[str] = Header(default=None, alias="X-App-Token"),
    request_id: str = Header(default="", alias="X-Request-ID"),
    db: Session = Depends(get_db),
):
    _validar_token_aplicacion_opcional(db, x_app_token)

    existe, activo = verificar_existencia_rol(db, rol_id)

    return build_response(
        request_id=request_id,
        success=True,
        message="Verificación de rol realizada exitosamente",
        data={"exists": existe, "active": activo},
    )