from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime, timezone


class RespuestaEstandar(BaseModel):
    """
    Estructura uniforme para TODAS las respuestas del sistema.
    El request_id se incluye también en la cabecera X-Request-ID.
    """
    request_id: str
    success:    bool
    data:       Optional[Any] = None
    message:    str
    timestamp:  datetime


def build_response(
    request_id: str,
    success:    bool,
    message:    str,
    data:       Any = None,
) -> RespuestaEstandar:
    """
    Helper centralizado. Todos los routers lo llaman
    en lugar de construir el dict manualmente.
    """
    return RespuestaEstandar(
        request_id=request_id,
        success=success,
        data=data,
        message=message,
        timestamp=datetime.now(timezone.utc),
    )