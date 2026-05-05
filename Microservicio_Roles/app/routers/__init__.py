from .roles import router as roles_router
from .permisos import router as permisos_router
from .asignaciones_rol_permiso import router as asignaciones_rol_permiso_router
from .asignaciones_usuario_rol import router as asignaciones_usuario_rol_router
from .validacion import router as validacion_router
from .seed import router as seed_router

__all__ = [
    "roles_router",
    "permisos_router",
    "asignaciones_rol_permiso_router",
    "asignaciones_usuario_rol_router",
    "validacion_router",
    "seed_router",
]