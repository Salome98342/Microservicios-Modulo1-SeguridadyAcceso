import time
import random
import string
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

HEADER_NAME = "X-Request-ID"
PREFIX      = "ROL"


def _generar_request_id() -> str:
    """Genera ROL-{timestamp_unix}-{6_chars_aleatorios}"""
    ts   = int(time.time())
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{PREFIX}-{ts}-{rand}"


def obtener_o_generar_request_id(request: Request) -> str:
    """
    Reglas RT-001:
    - Si la petición trae X-Request-ID válido  → reutilizarlo
    - Si no trae o está vacío                  → generar uno nuevo
    - Si el formato es inválido                → generar uno nuevo
    """
    incoming = request.headers.get(HEADER_NAME, "").strip()

    if incoming and _es_formato_valido(incoming):
        return incoming

    return _generar_request_id()


def _es_formato_valido(valor: str) -> bool:
    """
    Valida que el Request ID tenga un formato razonable.
    No fuerza el prefijo ROL porque puede venir de otro microservicio
    con su propio prefijo (ej: PED-1740000000-a3f8b2).
    """
    partes = valor.split("-")
    return len(partes) == 3 and partes[1].isdigit()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que:
    1. Genera o reutiliza el Request ID al inicio de cada petición
    2. Lo almacena en request.state.request_id
    3. Lo incluye en la cabecera de la respuesta
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = obtener_o_generar_request_id(request)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[HEADER_NAME] = request_id
        return response