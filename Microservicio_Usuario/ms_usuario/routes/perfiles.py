from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from models.perfil   import PerfilCrearActualizar, PerfilRespuesta
from models.response import RespuestaEstandar
import services.perfil_service as svc

from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso, es_token_notificaciones
)

router = APIRouter(prefix="/users", tags=["Perfiles"])


@router.get("/{usuario_id}/profile", response_model=RespuestaEstandar)
async def obtener_perfil(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """USR-RF-013: Consultar perfil extendido. Permiso: USR_PROFILE_READ."""
    req_id = obtener_o_generar(x_request_id)

    if not es_token_notificaciones(x_app_token):
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_PROFILE_READ", req_id)

    perfil, error = svc.obtener_perfil(usuario_id)
    if error:
        codigo = int(error[:3]) if error[:3].isdigit() else 404
        raise HTTPException(status_code=codigo, detail=error[4:] if ":" in error else error)

    registrar_log_async(req_id, "Consultar perfil", "GET",
                        f"/api/v1/users/{usuario_id}/profile", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, PerfilRespuesta(**perfil), "Perfil obtenido")


@router.put("/{usuario_id}/profile", response_model=RespuestaEstandar)
async def actualizar_perfil(
    usuario_id: int,
    datos: PerfilCrearActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-014: Crear o actualizar perfil extendido. Permiso: USR_PROFILE_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_PROFILE_UPDATE", req_id)

    datos_dict          = datos.model_dump(exclude_none=False)
    datos_dict["genero"] = datos.genero.value

    perfil, error, fue_creado = svc.crear_o_actualizar_perfil(usuario_id, datos_dict)
    if error:
        codigo = int(error[:3]) if error[:3].isdigit() else 400
        raise HTTPException(status_code=codigo, detail=error[4:] if ":" in error else error)

    http_code = status.HTTP_201_CREATED if fue_creado else status.HTTP_200_OK
    msg       = "Perfil creado exitosamente" if fue_creado else "Perfil actualizado exitosamente"
    registrar_log_async(req_id, "Actualizar perfil", "PUT",
                        f"/api/v1/users/{usuario_id}/profile",
                        http_code, sesion.get("user_id"), msg)
    return RespuestaEstandar.ok(req_id, PerfilRespuesta(**perfil), msg)

