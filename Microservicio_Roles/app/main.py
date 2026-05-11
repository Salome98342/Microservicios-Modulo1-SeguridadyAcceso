from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer                    # ← agregar
from app.config import settings
from app.core.request_id import RequestIDMiddleware
from app.core.exceptions import registrar_exception_handlers

from app.routers import (
    roles,
    permisos,
    asignaciones_rol_permiso,
    asignaciones_usuario_rol,
    internal,
    validacion,
    seed,
)

app = FastAPI(
    title="ms-roles",
    version=settings.app_version,
    description="Microservicio de roles y permisos — ERP Universitario",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestIDMiddleware)
registrar_exception_handlers(app)

app.include_router(roles.router,                    prefix="/api/v1")
app.include_router(permisos.router,                 prefix="/api/v1")
app.include_router(asignaciones_rol_permiso.router, prefix="/api/v1")
app.include_router(asignaciones_usuario_rol.router, prefix="/api/v1")
app.include_router(internal.router)
app.include_router(validacion.router,               prefix="/api/v1")
app.include_router(seed.router,                     prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "ok"
    }


@app.get("/health", tags=["Health Check"])
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/api/health", tags=["Health Check"])
def health_api():
    return {
        "status": "ok"
    }


@app.get("/api/v1/health", tags=["Health Check"])
def health_api_v1():
    return {
        "status": "ok"
    }