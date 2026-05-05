from fastapi import FastAPI

from .api.auth import router
from .core.database import init_db
from .core.config import APP_TITULO, APP_DESCRIPCION, APP_VERSION

app = FastAPI(title=APP_TITULO, description=APP_DESCRIPCION, version=APP_VERSION)
app.include_router(router, prefix="/api")


@app.get("/", tags=["Health Check"])
def health_check():
    return {"service": APP_TITULO, "version": APP_VERSION, "status": "ok"}


@app.get("/health", tags=["Health Check"])
def health_check_simple():
    return {"status": "ok"}


@app.get("/api/health", tags=["Health Check"])
def health_check_api():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    init_db()
