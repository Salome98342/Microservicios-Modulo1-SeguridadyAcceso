from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from models.usuario  import (
    UsuarioCrear, UsuarioActualizar, CambiarPassword, CambiarEstadoBody,
    UsuarioRespuesta, CifrarPasswordDebug
)
from models.response import RespuestaEstandar
import services.usuario_service  as svc
import services.historial_service as hist_svc

from utils.request_id    import obtener_o_generar
from utils.audit         import registrar_log_async
from utils.inter_service import (
    validar_sesion_activa, validar_permiso,
    notificar_async, es_token_autenticacion,
)
from utils.crypto        import cifrar_aes256
from config import PAGINA_DEFAULT, ITEMS_POR_PAGINA_DEFAULT, ITEMS_POR_PAGINA_MAX, DEBUG_MODE

router = APIRouter(prefix="/users", tags=["Usuarios"])


def _parsear_error(error: str) -> tuple[int, str]:
    if error and len(error) > 3 and error[:3].isdigit() and error[3] == ":":
        return int(error[:3]), error[4:]
    return 400, error


# ── POST /users ───────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED, response_model=RespuestaEstandar)
async def crear_usuario(
    datos: UsuarioCrear,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:   Optional[str] = Header(None, alias="X-App-Token"),
):
    """USR-RF-006: Crear nuevo usuario. Permiso requerido: USR_CREATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)   # USR-RF-001
    validar_permiso(sesion["rol_id"], "USR_CREATE", req_id) # USR-RF-002

    usuario, error = svc.crear_usuario(
        datos.username, 
        str(datos.email), 
        password_encrypted=datos.password_encrypted,
        password_plana=datos.password_plana if DEBUG_MODE else None,
        rol_id=datos.rol_id
    )
    if error:
        codigo, msg = _parsear_error(error)
        registrar_log_async(req_id, "Crear usuario", "POST", "/api/v1/users",
                            codigo, sesion.get("user_id"), msg)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_welcome", usuario["id"],
                    {"username": usuario["username"], "email": usuario["email"]},
                    req_id)
    registrar_log_async(req_id, "Crear usuario", "POST", "/api/v1/users",
                        201, sesion.get("user_id"),
                        f"Usuario '{usuario['username']}' creado")

    return RespuestaEstandar.ok(
        req_id, UsuarioRespuesta(**usuario), "Usuario creado exitosamente"
    )


# ── GET /users (búsqueda avanzada) ────────────────────────────────────────────
@router.get("", response_model=RespuestaEstandar)
async def busqueda_avanzada(
    nombre:           Optional[str] = None,
    numero_documento: Optional[str] = None,
    email:            Optional[str] = None,
    estado:           Optional[str] = None,
    ciudad:           Optional[str] = None,
    pagina:           int = PAGINA_DEFAULT,
    items_por_pagina: int = ITEMS_POR_PAGINA_DEFAULT,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-012: Búsqueda avanzada con filtros y paginación. Permiso: USR_SEARCH."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_SEARCH", req_id)

    if pagina < 1:
        raise HTTPException(400, detail="El número de página debe ser mayor o igual a 1")
    if not (1 <= items_por_pagina <= ITEMS_POR_PAGINA_MAX):
        raise HTTPException(400, detail=f"items_por_pagina debe estar entre 1 y {ITEMS_POR_PAGINA_MAX}")

    resultado = svc.busqueda_avanzada(
        nombre, numero_documento, email, estado, ciudad, pagina, items_por_pagina
    )
    registrar_log_async(req_id, "Búsqueda avanzada", "GET", "/api/v1/users",
                        200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, resultado, "Búsqueda completada")


# ── GET /users/stats/by-state ─────────────────────────────────────────────────
@router.get("/stats/by-state", response_model=RespuestaEstandar)
async def estadisticas(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-024: Estadísticas por estado. Permiso: USR_STATS_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_STATS_READ", req_id)
    return RespuestaEstandar.ok(req_id, svc.obtener_estadisticas(), "Estadísticas obtenidas")


# ── GET /users/by-role/{rol_id} ───────────────────────────────────────────────
@router.get("/by-role/{rol_id}", response_model=RespuestaEstandar)
async def listar_por_rol(
    rol_id: int,
    estado: Optional[str] = None,
    pagina: int = PAGINA_DEFAULT,
    items_por_pagina: int = ITEMS_POR_PAGINA_DEFAULT,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-023: Listar usuarios por rol. Permiso: USR_LIST_BY_ROLE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_LIST_BY_ROLE", req_id)
    return RespuestaEstandar.ok(
        req_id, svc.listar_por_rol(rol_id, estado, pagina, items_por_pagina), "OK"
    )


# ── GET /users/by-email/{email} ───────────────────────────────────────────────
@router.get("/by-email/{email}", response_model=RespuestaEstandar)
async def obtener_por_email(
    email: str,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    USR-RF-008: Consultar usuario por email.
    Si el X-App-Token pertenece a ms-autenticacion → incluye password_hash.
    """
    req_id  = obtener_o_generar(x_request_id)
    es_auth = es_token_autenticacion(x_app_token)

    if es_auth:
        usuario = svc.obtener_por_email_con_hash(email)
    else:
        sesion = validar_sesion_activa(authorization, req_id)
        validar_permiso(sesion["rol_id"], "USR_READ", req_id)
        usuario = svc.obtener_por_email_publico(email)

    if not usuario:
        raise HTTPException(404, detail="Usuario no encontrado")

    registrar_log_async(req_id, "Consultar por email", "GET",
                        f"/api/v1/users/by-email/{email}", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, usuario, "Usuario encontrado")


# ── GET /users/{usuario_id} ───────────────────────────────────────────────────
@router.get("/{usuario_id}", response_model=RespuestaEstandar)
async def obtener_usuario(
    usuario_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-007: Consultar usuario por ID. Permiso: USR_READ."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_READ", req_id)

    usuario = svc.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(404, detail="Usuario no encontrado")

    registrar_log_async(req_id, "Consultar usuario", "GET",
                        f"/api/v1/users/{usuario_id}", 200, sesion.get("user_id"), "OK")
    return RespuestaEstandar.ok(req_id, UsuarioRespuesta(**usuario), "Usuario encontrado")


# ── GET /users/{usuario_id}/validate ─────────────────────────────────────────
@router.get("/{usuario_id}/validate", response_model=RespuestaEstandar)
async def validar_existencia(
    usuario_id: int,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    x_app_token:  Optional[str] = Header(None, alias="X-App-Token"),
):
    """USR-RF-021: Validar existencia (servicio interno para ms-programas)."""
    req_id    = obtener_o_generar(x_request_id)
    resultado = svc.validar_existencia(usuario_id)
    registrar_log_async(req_id, "Validar existencia", "GET",
                        f"/api/v1/users/{usuario_id}/validate", 200, None, "OK")
    return RespuestaEstandar.ok(req_id, resultado, "Validación completada")


# ── PUT /users/{usuario_id} ───────────────────────────────────────────────────
@router.put("/{usuario_id}", response_model=RespuestaEstandar)
async def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-010: Actualizar datos básicos. Permiso: USR_UPDATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_UPDATE", req_id)

    usuario, error = svc.actualizar_usuario(
        usuario_id,
        datos.username,
        str(datos.email) if datos.email else None,
        datos.rol_id,
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    registrar_log_async(req_id, "Actualizar usuario", "PUT",
                        f"/api/v1/users/{usuario_id}", 200,
                        sesion.get("user_id"), "Actualizado")
    return RespuestaEstandar.ok(req_id, UsuarioRespuesta(**usuario),
                                "Usuario actualizado exitosamente")


# ── DELETE /users/{usuario_id} ────────────────────────────────────────────────
@router.delete("/{usuario_id}", response_model=RespuestaEstandar)
async def desactivar_usuario(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-011: Desactivar usuario (soft delete). Permiso: USR_DELETE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_DELETE", req_id)

    if not body.motivo.strip():
        raise HTTPException(400, detail="Debe proporcionar un motivo para la desactivación")

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, "inactivo", body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": "inactivo", "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Desactivar usuario", "DELETE",
                        f"/api/v1/users/{usuario_id}", 200,
                        sesion.get("user_id"), "Usuario desactivado")
    return RespuestaEstandar.ok(req_id, None, "Usuario desactivado exitosamente")


# ── PATCH /users/{usuario_id}/state ──────────────────────────────────────────
@router.patch("/{usuario_id}/state", response_model=RespuestaEstandar)
async def cambiar_estado(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-015: Cambiar estado de usuario. Permiso: USR_CHANGE_STATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_CHANGE_STATE", req_id)

    if not body.estado_nuevo:
        raise HTTPException(400, detail="Debe proporcionar el nuevo estado")

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, body.estado_nuevo, body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": body.estado_nuevo, "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Cambiar estado", "PATCH",
                        f"/api/v1/users/{usuario_id}/state", 200,
                        sesion.get("user_id"), f"Estado → {body.estado_nuevo}")
    return RespuestaEstandar.ok(req_id, None, "Estado actualizado exitosamente")


# ── POST /users/{usuario_id}/reactivate ──────────────────────────────────────
@router.post("/{usuario_id}/reactivate", response_model=RespuestaEstandar)
async def reactivar_usuario(
    usuario_id: int,
    body: CambiarEstadoBody,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-020: Reactivar usuario. Permiso: USR_REACTIVATE."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)
    validar_permiso(sesion["rol_id"], "USR_REACTIVATE", req_id)

    usuario, error = hist_svc.cambiar_estado(
        usuario_id, "activo", body.motivo, sesion["user_id"]
    )
    if error:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_state_change", usuario_id,
                    {"new_state": "activo", "reason": body.motivo}, req_id)
    registrar_log_async(req_id, "Reactivar usuario", "POST",
                        f"/api/v1/users/{usuario_id}/reactivate", 200,
                        sesion.get("user_id"), "Usuario reactivado")
    return RespuestaEstandar.ok(req_id, None, "Usuario reactivado exitosamente")


# ── PATCH /users/{usuario_id}/password ───────────────────────────────────────
@router.patch("/{usuario_id}/password", response_model=RespuestaEstandar)
async def cambiar_password(
    usuario_id: int,
    datos: CambiarPassword,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_request_id:  Optional[str] = Header(None, alias="X-Request-ID"),
):
    """USR-RF-022: Actualizar contraseña. Solo el propio usuario."""
    req_id = obtener_o_generar(x_request_id)
    sesion = validar_sesion_activa(authorization, req_id)

    if sesion["user_id"] != usuario_id:
        raise HTTPException(403, detail="Solo puede cambiar su propia contraseña")

    ok, error = svc.cambiar_password(
        usuario_id, datos.password_actual_encrypted, datos.password_nueva_encrypted
    )
    if not ok:
        codigo, msg = _parsear_error(error)
        raise HTTPException(status_code=codigo, detail=msg)

    notificar_async("user_security_alert", usuario_id, {}, req_id)
    registrar_log_async(req_id, "Cambiar contraseña", "PATCH",
                        f"/api/v1/users/{usuario_id}/password", 200,
                        sesion.get("user_id"), "Contraseña actualizada")
    return RespuestaEstandar.ok(req_id, None, "Contraseña actualizada exitosamente")


# ── POST /users/encrypt-password [DEBUG ONLY] ────────────────────────────────
@router.post("/encrypt-password", response_model=RespuestaEstandar)
async def encriptar_password_debug(
    datos: CifrarPasswordDebug,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
):
    """
    [DEBUG ONLY - Disponible solo en modo DEBUG_MODE=true]
    
    Utilidad para obtener una contraseña cifrada en AES-256 + Base64.
    Esto es necesario para pruebas manuales en Postman.
    
    IMPORTANTE: Esta contraseña debe usarse como "password_encrypted" en 
    el body de POST /users
    
    Ejemplo:
    - Input: {"password_plana": "miPassword123"}
    - Output: {"password_encrypted": "xKG3...base64..."}
    - Usa ese valor en: {"username": "john", "email": "john@test.com", "password_encrypted": "xKG3..."}
    """
    if not DEBUG_MODE:
        raise HTTPException(403, detail="Este endpoint solo está disponible en modo DEBUG")
    
    req_id = obtener_o_generar(x_request_id)
    
    if not datos.password_plana or len(datos.password_plana) < 1:
        raise HTTPException(400, detail="La contraseña no puede estar vacía")
    
    try:
        password_encrypted = cifrar_aes256(datos.password_plana)
        registrar_log_async(req_id, "Encriptar contraseña [DEBUG]", "POST",
                            "/api/v1/users/encrypt-password", 200, None, "Password encriptada")
        return RespuestaEstandar.ok(
            req_id,
            {"password_encrypted": password_encrypted},
            "Contraseña encriptada. Usa este valor como 'password_encrypted' en POST /users"
        )
    except Exception as e:
        registrar_log_async(req_id, "Encriptar contraseña [DEBUG]", "POST",
                            "/api/v1/users/encrypt-password", 500, None, f"Error: {str(e)}")
        raise HTTPException(500, detail=f"Error al encriptar: {str(e)}")

