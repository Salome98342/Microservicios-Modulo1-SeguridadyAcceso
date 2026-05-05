from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone


# ── Excepciones de dominio personalizadas ─────────────────────────────────────

class RecursoNoEncontrado(Exception):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje

class ConflictoDeNegocio(Exception):
    def __init__(self, mensaje: str, detalle: dict = None):
        self.mensaje = mensaje
        self.detalle = detalle or {}

class NoAutorizado(Exception):
    def __init__(self, mensaje: str = "Token inválido o sesión expirada."):
        self.mensaje = mensaje

class SinPermiso(Exception):
    def __init__(self, mensaje: str = "No tiene permiso para esta operación."):
        self.mensaje = mensaje

class ServicioNoDisponible(Exception):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje


# ── Registro de handlers en la app ───────────────────────────────────────────

def registrar_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos los handlers. Se llama una sola vez en main.py.
    Todos retornan RespuestaEstandar para mantener RT-004.
    """

    def _base(request: Request, status: int, success: bool, message: str, data=None):
        request_id = getattr(request.state, "request_id", "sin-request-id")
        return JSONResponse(
            status_code=status,
            headers={"X-Request-ID": request_id},
            content={
                "request_id": request_id,
                "success":    success,
                "data":       data,
                "message":    message,
                "timestamp":  datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(RecursoNoEncontrado)
    async def handler_404(request: Request, exc: RecursoNoEncontrado):
        return _base(request, 404, False, exc.mensaje)

    @app.exception_handler(ConflictoDeNegocio)
    async def handler_409(request: Request, exc: ConflictoDeNegocio):
        return _base(request, 409, False, exc.mensaje, exc.detalle or None)

    @app.exception_handler(NoAutorizado)
    async def handler_401(request: Request, exc: NoAutorizado):
        return _base(request, 401, False, exc.mensaje)

    @app.exception_handler(SinPermiso)
    async def handler_403(request: Request, exc: SinPermiso):
        return _base(request, 403, False, exc.mensaje)

    @app.exception_handler(ServicioNoDisponible)
    async def handler_503(request: Request, exc: ServicioNoDisponible):
        return _base(request, 503, False, exc.mensaje)

    @app.exception_handler(RequestValidationError)
    async def handler_422(request: Request, exc: RequestValidationError):
        return _base(
            request, 422, False,
            "Error de validación en los datos enviados.",
            {"errores": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def handler_500(request: Request, exc: Exception):
        return _base(request, 500, False, "Error interno del servidor.")