from fastapi import FastAPI
from config import APP_TITULO, APP_DESCRIPCION, APP_VERSION, APP_PREFIX

from routes.usuarios        import router as router_usuarios
from routes.perfiles        import router as router_perfiles
from routes.historial       import router as router_historial
from routes.preferencias    import router as router_preferencias
from routes.tipos_documento import router as router_tipos
from routes.internal_auth   import router as router_internal_auth

app = FastAPI(
    title=APP_TITULO,
    description=APP_DESCRIPCION,
    version=APP_VERSION,
)

app.include_router(router_usuarios,     prefix=APP_PREFIX)
app.include_router(router_perfiles,     prefix=APP_PREFIX)
app.include_router(router_historial,    prefix=APP_PREFIX)
app.include_router(router_preferencias, prefix=APP_PREFIX)
app.include_router(router_tipos,        prefix=APP_PREFIX)
app.include_router(router_internal_auth)


@app.get("/", tags=["Health Check"])
def health_check():
    return {"service": APP_TITULO, "version": APP_VERSION, "status": "ok"}


@app.get("/api/v1/health", tags=["Health Check"])
def health_check_v1():
    return {"service": APP_TITULO, "version": APP_VERSION, "status": "ok"}

