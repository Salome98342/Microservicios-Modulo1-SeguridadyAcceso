import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger("ms-roles.audit")


async def enviar_log_auditoria(
    request_id:   str,
    funcionalidad: str,
    metodo_http:  str,
    codigo_respuesta: int,
    duracion_ms:  int,
    usuario_id:   Optional[int],
    detalle:      str,
) -> None:
    """
    RT-003 — Envía un registro de log a ms-auditoria.

    - Es fire-and-forget: no bloquea la respuesta al cliente.
    - Si falla (timeout, servicio caído), registra en log local y continúa.
    - NUNCA debe propagarse como excepción al router.
    """
    payload = {
        "fecha_hora":        datetime.now(timezone.utc).isoformat(),
        "request_id":        request_id,
        "microservicio":     "ms-roles",
        "funcionalidad":     funcionalidad,
        "metodo_http":       metodo_http,
        "codigo_respuesta":  codigo_respuesta,
        "duracion_ms":       duracion_ms,
        "usuario_id":        usuario_id,
        "detalle":           detalle,
    }

    try:
        async with httpx.AsyncClient(
            timeout=settings.timeout_ms_auditoria / 1000  # convertir ms a segundos
        ) as client:
            await client.post(
                f"{settings.ms_auditoria_url}/audit/logs",
                json=payload,
            )
    except Exception as e:
        # Fallo silencioso — solo registra localmente (RT-003 secuencia alterna 2A)
        logger.warning(
            "Fallo envío log a ms-auditoria | "
            f"request_id={request_id} | "
            f"funcionalidad={funcionalidad} | "
            f"error={type(e).__name__}: {e}"
        )


def disparar_auditoria(
    request_id:       str,
    funcionalidad:    str,
    metodo_http:      str,
    codigo_respuesta: int,
    duracion_ms:      int,
    usuario_id:       Optional[int],
    detalle:          str,
) -> None:
    """
    Wrapper sincrónico para llamar desde los routers.
    Crea la tarea async sin bloquear.
    """
    asyncio.create_task(
        enviar_log_auditoria(
            request_id=request_id,
            funcionalidad=funcionalidad,
            metodo_http=metodo_http,
            codigo_respuesta=codigo_respuesta,
            duracion_ms=duracion_ms,
            usuario_id=usuario_id,
            detalle=detalle,
        )
    )


async def log_auditoria(
    db,
    usuario_id: Optional[int],
    accion: str,
    recurso: str,
    detalles: str,
    request_id: str,
    duracion_ms: int,
) -> None:
    """
    Función para logging de acciones de negocio.
    Por ahora, solo registra localmente. En el futuro podría enviar a ms-auditoria.
    """
    logger.info(
        f"AUDITORIA | request_id={request_id} | usuario_id={usuario_id} | "
        f"accion={accion} | recurso={recurso} | duracion_ms={duracion_ms} | "
        f"detalles={detalles}"
    )