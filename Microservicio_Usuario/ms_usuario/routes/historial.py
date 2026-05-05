from fastapi import APIRouter, Header
from typing import Optional

from models.response import RespuestaEstandar
import services.historial_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import validar_sesion_activa, validar_permiso

router = APIRouter(prefix="/users", tags=["Historial de Estados"])


@router.get("/{usuario_id}/state-history", response_model=RespuestaEstandar)
async def listar_historial(
    usuario_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-016: Consultar historial de cambios de estado. Permiso: USR_HISTORY_READ."""
    req_id   = obtener_o_generar(x_request_id)
    sesion   = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_HISTORY_READ", req_id)

    historial = svc.listar_historial(usuario_id)
    msg       = "Historial obtenido" if historial else "No hay historial de cambios para este usuario"
    registrar_log_async(req_id, "Consultar historial", "GET",
                        f"/api/v1/users/{usuario_id}/state-history",
                        200, sesion.get("user_id"), f"{len(historial)} registros")
    return RespuestaEstandar.ok(req_id, historial, msg)

