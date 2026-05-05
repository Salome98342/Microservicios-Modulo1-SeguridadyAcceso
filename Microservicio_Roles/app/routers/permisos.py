from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import (
    dep_request_id,
    dep_usuario_activo,
    dep_verificar_permiso,
    get_db,
    dep_inicio_tiempo,
    calcular_duracion_ms,
)
from app.services.permiso_service import (
    crear_permiso,
    obtener_permiso_por_id,
    listar_permisos,
    listar_permisos_por_modulo,
    actualizar_permiso,
    eliminar_permiso,
)
from app.schemas.permiso import PermisoCreate, PermisoUpdate, PermisoResponse
from app.core.response import build_response, RespuestaEstandar
from app.core.audit import log_auditoria

router = APIRouter(prefix="/permisos", tags=["permisos"])


@router.post("/", response_model=RespuestaEstandar)
async def crear_nuevo_permiso(
    permiso_data: PermisoCreate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_CREATE", usuario, request_id)

    permiso = crear_permiso(db, permiso_data)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="CREAR_PERMISO",
        recurso=f"permiso:{permiso.id}",
        detalles=f"Permiso '{permiso.nombre}' creado",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permiso creado exitosamente",
        data=PermisoResponse.from_orm(permiso),
    )


@router.get("/", response_model=RespuestaEstandar)
async def listar_todos_los_permisos(
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_READ", usuario, request_id)

    permisos = listar_permisos(db)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="LISTAR_PERMISOS",
        recurso="permisos",
        detalles=f"{len(permisos)} permisos listados",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permisos listados exitosamente",
        data=[PermisoResponse.from_orm(p) for p in permisos],
    )


@router.get("/modulo", response_model=RespuestaEstandar)
async def listar_permisos_por_modulo_endpoint(
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_READ", usuario, request_id)

    grupos = listar_permisos_por_modulo(db)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="LISTAR_PERMISOS_MODULO",
        recurso="permisos:modulo",
        detalles=f"{len(grupos)} módulos listados",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permisos agrupados por módulo listados exitosamente",
        data=grupos,
    )


@router.get("/{permiso_id}", response_model=RespuestaEstandar)
async def obtener_permiso(
    permiso_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_READ", usuario, request_id)

    permiso = obtener_permiso_por_id(db, permiso_id)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="OBTENER_PERMISO",
        recurso=f"permiso:{permiso_id}",
        detalles=f"Permiso '{permiso.nombre}' consultado",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permiso obtenido exitosamente",
        data=PermisoResponse.from_orm(permiso),
    )


@router.put("/{permiso_id}", response_model=RespuestaEstandar)
async def actualizar_permiso_endpoint(
    permiso_id: int,
    permiso_data: PermisoUpdate,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_UPDATE", usuario, request_id)

    # Buscar objeto primero
    permiso = obtener_permiso_por_id(db, permiso_id)
    permiso_actualizado = actualizar_permiso(db, permiso, permiso_data)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="ACTUALIZAR_PERMISO",
        recurso=f"permiso:{permiso_id}",
        detalles=f"Permiso '{permiso_actualizado.nombre}' actualizado",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permiso actualizado exitosamente",
        data=PermisoResponse.from_orm(permiso_actualizado),
    )


@router.delete("/{permiso_id}", response_model=RespuestaEstandar)
async def eliminar_permiso_endpoint(
    permiso_id: int,
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("PERM_DELETE", usuario, request_id)

    # Buscar objeto primero
    permiso = obtener_permiso_por_id(db, permiso_id)
    eliminar_permiso(db, permiso)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="ELIMINAR_PERMISO",
        recurso=f"permiso:{permiso_id}",
        detalles=f"Permiso '{permiso.nombre}' eliminado",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Permiso eliminado exitosamente",
        data=None,
    )