from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import (
    dep_request_id,
    dep_usuario_activo,
    dep_verificar_permiso,
    get_db,
    dep_inicio_tiempo,
    calcular_duracion_ms,
)
from app.services.seed_service import cargar_datos_semilla
from app.core.response import build_response
from app.core.audit import log_auditoria

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/")
async def cargar_datos_semilla_endpoint(
    request_id: str = Depends(dep_request_id),
    usuario: dict = Depends(dep_usuario_activo),
    db: Session = Depends(get_db),
    inicio: float = Depends(dep_inicio_tiempo),
):
    await dep_verificar_permiso("SEED_EXECUTE", usuario, request_id)

    try:
        resultado = cargar_datos_semilla(db)
        duracion = calcular_duracion_ms(inicio)

        await log_auditoria(
            db=db,
            usuario_id=usuario.get("usuario_id"),
            accion="CARGAR_SEED",
            recurso="seed",
            detalles=f"Datos semilla cargados: {resultado}",
            request_id=request_id,
            duracion_ms=duracion,
        )

        return build_response(
            request_id=request_id,
            success=True,
            message="Datos semilla cargados exitosamente",
            data=resultado,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))