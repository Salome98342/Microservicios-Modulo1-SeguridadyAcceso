"""
Comunicación con ms-autenticacion [AUTH], ms-roles [ROL] y ms-notificaciones [NOT].
Implementa las reglas transversales USR-RF-001, USR-RF-002 y las notificaciones
descritas en la Sección 3.3 del diseño de integración.
"""
import json
import threading
from typing import Optional, Tuple
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

from fastapi import HTTPException, status

from config import (
    AUTH_SERVICE_URL, ROL_SERVICE_URL, NOT_SERVICE_URL,
    AUTH_APP_TOKEN, ROL_APP_TOKEN, NOT_APP_TOKEN, USR_APP_TOKEN,
    TIMEOUT_AUTH, TIMEOUT_ROL, TIMEOUT_NOT, DEBUG_MODE,
)
from utils.crypto import descifrar_aes256, cifrar_aes256


def _cabeceras(app_token: str, request_id: str = "") -> dict:
    """Construye las cabeceras estándar para llamadas inter-servicio."""
    return {
        "Content-Type": "application/json",
        "X-App-Token":  f"AES256:{cifrar_aes256(app_token)}",
        "X-Request-ID": request_id,
    }


def _post_json(url: str, payload: dict, cabeceras: dict, timeout: float) -> dict:
    """Realiza una petición POST y retorna el JSON de respuesta."""
    data = json.dumps(payload).encode("utf-8")
    req  = urllib_request.Request(url=url, data=data, headers=cabeceras, method="POST")
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, cabeceras: dict, timeout: float) -> dict:
    """Realiza una petición GET y retorna el JSON de respuesta."""
    req = urllib_request.Request(url=url, headers=cabeceras, method="GET")
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── USR-RF-001: Validación de sesión ──────────────────────────────────────────

def validar_sesion_activa(authorization: str, request_id: str) -> dict:
    """
    Consulta ms-autenticacion para validar el token de sesión.
    Lanza HTTPException si no es válido.
    Retorna el payload con user_id y rol_id.
    
    En DEBUG_MODE, retorna una sesión falsa sin validar.
    """
    # ── DEBUG MODE: permitir acceso sin validación ──────────────────────
    if DEBUG_MODE:
        return {"user_id": 1, "rol_id": 1}
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de sesión no proporcionado"
        )

    token = authorization.split(" ", 1)[1]
    try:
        respuesta = _post_json(
            url=f"{AUTH_SERVICE_URL}/api/v1/auth/validate-session",
            payload={"token": token, "request_id": request_id},
            cabeceras={
                **_cabeceras(AUTH_APP_TOKEN, request_id),
                "Authorization": authorization,
            },
            timeout=TIMEOUT_AUTH,
        )
    except HTTPError as e:
        if e.code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión no válida o expirada"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible"
        )

    datos = respuesta.get("data", {})
    if not datos.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no válida o expirada"
        )
    return {"user_id": datos["user_id"], "rol_id": datos["rol_id"]}


# ── USR-RF-002: Validación de permisos ────────────────────────────────────────

def validar_permiso(rol_id: int, codigo_permiso: str, request_id: str) -> None:
    """
    Consulta ms-roles para verificar que el rol tiene el permiso.
    Lanza HTTPException 403 si no tiene autorización.
    
    En DEBUG_MODE, siempre permite acceso.
    """
    # ── DEBUG MODE: permitir todos los permisos ────────────────────────
    if DEBUG_MODE:
        return
    
    try:
        respuesta = _post_json(
            url=f"{ROL_SERVICE_URL}/api/v1/roles/validate-permission",
            payload={
                "rol_id":          rol_id,
                "permission_code": codigo_permiso,
                "request_id":      request_id,
            },
            cabeceras=_cabeceras(ROL_APP_TOKEN, request_id),
            timeout=TIMEOUT_ROL,
        )
    except HTTPError as e:
        if e.code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ejecutar esta operación"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de roles no disponible"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de roles no disponible"
        )

    if not respuesta.get("data", {}).get("authorized"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ejecutar esta operación"
        )


# ── Validar existencia de rol en ms-roles ─────────────────────────────────────

def validar_rol_externo(rol_id: int) -> Tuple[bool, Optional[str]]:
    """
    Verifica que el rol exista y esté activo en ms-roles. Retorna (válido, error).
    
    En DEBUG_MODE, siempre devuelve True sin validar.
    """
    # ── DEBUG MODE: permitir cualquier rol ──────────────────────────────
    if DEBUG_MODE:
        return True, None
    
    try:
        respuesta = _get_json(
            url=f"{ROL_SERVICE_URL}/api/v1/roles/{rol_id}/validate",
            cabeceras=_cabeceras(ROL_APP_TOKEN),
            timeout=TIMEOUT_ROL,
        )
    except HTTPError as e:
        if e.code == 404:
            return False, "El rol especificado no es válido"
        return False, "503:Servicio de roles no disponible"
    except Exception:
        return False, "503:Servicio de roles no disponible"

    datos = respuesta.get("data", {})
    if not datos.get("exists") or not datos.get("active"):
        return False, "El rol especificado no existe o está inactivo"
    return True, None


# ── Notificaciones asíncronas (fire-and-forget) ───────────────────────────────

def _enviar_notificacion(
    notification_type: str, user_id: int, data: dict, request_id: str
) -> None:
    try:
        _post_json(
            url=f"{NOT_SERVICE_URL}/api/v1/notifications/send",
            payload={
                "notification_type": notification_type,
                "user_id":           user_id,
                "data":              data,
                "request_id":        request_id,
            },
            cabeceras=_cabeceras(NOT_APP_TOKEN, request_id),
            timeout=TIMEOUT_NOT,
        )
    except Exception:
        pass  # No crítico — fire-and-forget


def notificar_async(
    notification_type: str, user_id: int, data: dict, request_id: str
) -> None:
    """Lanza la notificación en un thread separado. No bloquea la respuesta."""
    hilo = threading.Thread(
        target=_enviar_notificacion,
        args=(notification_type, user_id, data, request_id),
        daemon=True,
    )
    hilo.start()


# ── Validadores de token de aplicación ───────────────────────────────────────

def es_token_de(x_app_token: Optional[str], token_esperado: str) -> bool:
    """
    Verifica si el X-App-Token pertenece a un microservicio específico.
    El token llega cifrado con AES-256 y prefijo 'AES256:'.
    """
    if not x_app_token:
        return False
    try:
        valor     = x_app_token.replace("AES256:", "", 1)
        descifrado = descifrar_aes256(valor)
        return descifrado == token_esperado
    except Exception:
        return False


def es_token_autenticacion(x_app_token: Optional[str]) -> bool:
    return es_token_de(x_app_token, AUTH_APP_TOKEN)


def es_token_notificaciones(x_app_token: Optional[str]) -> bool:
    return es_token_de(x_app_token, NOT_APP_TOKEN)

