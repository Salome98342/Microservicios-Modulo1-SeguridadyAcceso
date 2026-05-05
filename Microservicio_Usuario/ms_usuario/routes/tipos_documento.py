from fastapi import APIRouter, Header
from typing import Optional

from models.response import RespuestaEstandar
import services.tipo_documento_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import validar_sesion_activa, validar_permiso

router = APIRouter(prefix="/document-types", tags=["Tipos de Documento"])


@router.get("", response_model=RespuestaEstandar)
async def listar_tipos(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-017: Catálogo de tipos de documento activos. Permiso: USR_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_READ", req_id)

    tipos = svc.listar_activos()
    registrar_log_async(req_id, "Listar tipos de documento", "GET",
                        "/api/v1/document-types", 200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, tipos, "Tipos de documento obtenidos")

