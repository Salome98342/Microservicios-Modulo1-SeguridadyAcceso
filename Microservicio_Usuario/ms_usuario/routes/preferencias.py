from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from models.preferencias_notificacion import PreferenciasActualizar, PreferenciasRespuesta
from models.response import RespuestaEstandar
import services.preferencias_service as svc
from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso, es_token_notificaciones
)

router = APIRouter(prefix="/users", tags=["Preferencias de Notificación"])


@router.get("/{usuario_id}/notification-preferences", response_model=RespuestaEstandar)
async def obtener_preferencias(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    USR-RF-018: Consultar preferencias de notificación.
    Accesible por usuario autenticado (USR_PREFERENCES_READ) o ms-notificaciones.
    """
    req_id = obtener_o_generar(x_request_id)

    if not es_token_notificaciones(x_app_token):
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_PREFERENCES_READ", req_id)

    pref, error = svc.obtener_preferencias(usuario_id)
    if error:
        raise HTTPException(404, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Consultar preferencias", "GET",
                        f"/api/v1/users/{usuario_id}/notification-preferences",
                        200, None, "OK")
    return RespuestaEstandar.ok(req_id, pref, "Preferencias de notificación obtenidas")


@router.put("/{usuario_id}/notification-preferences", response_model=RespuestaEstandar)
async def actualizar_preferencias(
    usuario_id: int,
    datos: PreferenciasActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-019: Actualizar preferencias de notificación. Permiso: USR_PREFERENCES_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_PREFERENCES_UPDATE", req_id)

    datos_dict = {k: v for k, v in datos.model_dump().items() if v is not None}
    pref, error = svc.crear_o_actualizar_preferencias(usuario_id, datos_dict)
    if error:
        raise HTTPException(400, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Actualizar preferencias", "PUT",
                        f"/api/v1/users/{usuario_id}/notification-preferences",
                        200, sesion.get("user_id"), "Actualizado")
    return RespuestaEstandar.ok(req_id, pref, "Preferencias actualizadas exitosamente")

