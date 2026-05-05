from typing import Dict

import httpx

from app.config import settings
from app.core.exceptions import NoAutorizado, ServicioNoDisponible


async def validar_sesion_usuario(token: str, request_id: str) -> Dict[str, object]:
    try:
        async with httpx.AsyncClient(
            timeout=settings.timeout_ms_autenticacion / 1000
        ) as client:
            respuesta = await client.post(
                f"{settings.ms_autenticacion_url}/auth/validate-session",
                json={"user_token": token},
                headers={"X-Request-ID": request_id},
            )

        if respuesta.status_code != 200:
            raise NoAutorizado(
                "No se pudo validar la sesión con ms-autenticacion."
            )

        contenido = respuesta.json()
        if not contenido.get("data", {}).get("valid", False):
            raise NoAutorizado("Sesión inválida o expirada.")

        return contenido["data"]

    except httpx.TimeoutException:
        raise ServicioNoDisponible(
            "ms-autenticacion no respondió en el tiempo esperado."
        )
    except (httpx.ConnectError, httpx.RequestError):
        raise ServicioNoDisponible("ms-autenticacion no está disponible.")
