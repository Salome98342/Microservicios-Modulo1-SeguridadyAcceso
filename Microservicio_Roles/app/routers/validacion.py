from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import (
    dep_request_id,
    dep_usuario_activo,
    dep_verificar_permiso,
    get_db,
    dep_inicio_tiempo,
    calcular_duracion_ms,
)
from app.services.validacion_service import (
    validar_permiso_de_rol,
    verificar_existencia_rol,
)
from app.core.response import build_response
from app.core.audit import log_auditoria

router = APIRouter(prefix="/validacion", tags=["validacion"])


@router.get("/permiso")
async def validar_permiso_de_rol_endpoint(
    rol: str = Query(..., description="Nombre o ID del rol"),
    permiso: str = Query(..., description="Código o ID del permiso"),
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("VALIDACION_READ", usuario, request_id)

    try:
        valido = validar_permiso_de_rol(db, rol, permiso)
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="VALIDAR_PERMISO_ROL",
            recurso=f"validacion:rol:{rol}:permiso:{permiso}",
            detalles=f"Validación de permiso '{permiso}' para rol '{rol}': {'válido' if valido else 'inválido'}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Validación de permiso realizada exitosamente",
            data={"autorizado": valido},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rol")
async def verificar_existencia_rol_endpoint(
    rol: str = Query(..., description="Nombre o ID del rol"),
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("VALIDACION_READ", usuario, request_id)

    existe, activo = verificar_existencia_rol(db, rol)
    duracion = calcular_duracion_ms(inicio)

    await log_auditoria(
        db=db,
        usuario_id=usuario.get("usuario_id"),
        accion="VERIFICAR_ROL",
        recurso=f"validacion:rol:{rol}",
        detalles=f"Verificación de rol '{rol}': {'existe y activo' if existe and activo else 'no existe o inactivo'}",
        request_id=request_id,
        duracion_ms=duracion,
    )

    return build_response(
        request_id=request_id,
        success=True,
        message="Verificación de rol realizada exitosamente",
        data={"existe": existe, "activo": activo},
    )