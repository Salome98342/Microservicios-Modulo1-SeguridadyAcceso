import time
from typing import Optional
from fastapi import Header, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import settings
from app.core.request_id import obtener_o_generar_request_id
from app.core.exceptions import NoAutorizado, SinPermiso, ServicioNoDisponible
from app.models.token_aplicacion import TokenAplicacion
from app.core.security import validar_token_aplicacion

import httpx


# ── 1. Request ID ─────────────────────────────────────────────────────────────

def dep_request_id(request: Request) -> str:
    """
    Extrae el Request ID ya procesado por el middleware.
    Si por alguna razón no está en request.state, lo genera.
    Disponible en todos los endpoints como parámetro.
    """
    return getattr(request.state, "request_id", obtener_o_generar_request_id(request))


# ── 2. Token de la cabecera Authorization ─────────────────────────────────────

def dep_auth_header(
    authorization: str = Header(
        None,
        alias="Authorization",
        description=(
            "Token de autenticación. "
            "Usuarios: 'Bearer {token_jwt}'. "
            "Microservicios: 'Bearer {token_app_cifrado_AES256}'."
        ),
        example="Bearer eyJhbGciOiJIUzI1NiJ9..."
    )
) -> str:
    """
    Extrae el token crudo de la cabecera Authorization.
    Solo valida el formato 'Bearer <token>' — la validación
    real ocurre en dep_usuario_activo o dep_token_aplicacion.
    """
    if settings.debug and not authorization:
        return "debug-token"

    if not authorization:
        raise NoAutorizado("Authorization es requerido.")

    if not authorization.startswith("Bearer "):
        raise NoAutorizado(
            "Formato de Authorization inválido. Se esperaba: Bearer <token>."
        )
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise NoAutorizado("El token no puede estar vacío.")
    return token


# ── 3. Sesión de usuario (JWT) — RT-002 para usuarios humanos ─────────────────

async def dep_usuario_activo(
    request:    Request,
    token:      str     = Depends(dep_auth_header),
    request_id: str     = Depends(dep_request_id),
) -> dict:
    """
    Valida el JWT del usuario consultando ms-autenticacion.
    Retorna el payload con usuario_id y rol si la sesión es válida.
    RT-001: propaga el request_id en la llamada saliente.
    """
    if settings.debug:
        return {"usuario_id": 1, "rol": "ADMIN", "valid": True}

    try:
        async with httpx.AsyncClient(
            timeout=settings.timeout_ms_autenticacion / 1000
        ) as client:
            respuesta = await client.post(
                f"{settings.ms_autenticacion_url}/v1/auth/validate-session",
                json={"token": token},
                headers={"X-Request-ID": request_id},
            )

        if respuesta.status_code != 200:
            raise NoAutorizado("No se pudo validar la sesión con ms-autenticacion.")

        data = respuesta.json()
        payload = data.get("data") or data

        # ms-autenticacion puede retornar { data: {...} } o el payload plano
        if not payload.get("valid", False):
            raise NoAutorizado("Sesión inválida o expirada.")

        return payload

    except httpx.TimeoutException:
        raise ServicioNoDisponible(
            "ms-autenticacion no respondió en el tiempo esperado."
        )
    except (httpx.ConnectError, httpx.RequestError):
        raise ServicioNoDisponible(
            "ms-autenticacion no está disponible."
        )


# ── 4. Token de aplicación — RT-002 para microservicios ───────────────────────

def dep_token_aplicacion(
    token: str      = Depends(dep_auth_header),
    db:    Session  = Depends(get_db),
) -> str:
    """
    Valida que el token de aplicación pertenece a un microservicio
    registrado y activo en la tabla rol_tokens_aplicacion.
    Usado en endpoints internos como validate-permission (RF-017).
    """
    # Buscar todos los tokens activos y comparar
    tokens_activos = (
        db.query(TokenAplicacion)
        .filter(TokenAplicacion.estado == "activo")
        .all()
    )

    for registro in tokens_activos:
        if validar_token_aplicacion(token, registro.token_cifrado):
            return registro.nombre_servicio

    raise NoAutorizado("Token de aplicación inválido o inactivo.")


# ── 5. Validación de permiso — RT-002 (paso 2 de toda operación) ──────────────

async def dep_verificar_permiso(
    codigo_permiso: str,
    usuario_data:   dict,
    request_id:     str,
    db:             Session = None,
) -> None:
    from app.services.validacion_service import validar_permiso_de_rol
    from app.db.session import SessionLocal

    if settings.debug:
        return

    rol = usuario_data.get("rol")
    if not rol:
        raise SinPermiso("No se pudo determinar el rol del usuario.")

    _db = db or SessionLocal()
    try:
        autorizado = validar_permiso_de_rol(_db, rol, codigo_permiso)
    finally:
        if not db:
            _db.close()

    if not autorizado:
        raise SinPermiso(
            f"El rol '{rol}' no tiene el permiso '{codigo_permiso}'."
        )

# ── 6. Medición de tiempo — para duracion_ms en auditoría ────────────────────

def dep_inicio_tiempo() -> float:
    """
    Retorna el timestamp de inicio del request.
    Se usa junto con calcular_duracion_ms() en los routers
    para medir cuánto tardó cada operación.
    """
    return time.time()


def calcular_duracion_ms(inicio: float) -> int:
    """
    Calcula los milisegundos transcurridos desde 'inicio'.
    Uso: duracion = calcular_duracion_ms(inicio)
    """
    return int((time.time() - inicio) * 1000)


# ── 7. Base de datos — re-exportada para comodidad ────────────────────────────

# Se re-exporta get_db para que los routers solo importen desde dependencies
__all__ = [
    "dep_request_id",
    "dep_auth_header",
    "dep_usuario_activo",
    "dep_token_aplicacion",
    "dep_verificar_permiso",
    "dep_inicio_tiempo",
    "calcular_duracion_ms",
    "get_db",
]