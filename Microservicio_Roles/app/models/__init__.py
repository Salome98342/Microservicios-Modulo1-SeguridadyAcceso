"""
app/models/__init__.py
======================
Punto de entrada del paquete `models`.

Importa todos los modelos ORM del microservicio ms-roles para que:

    1. SQLAlchemy registre todas las tablas en `Base.metadata` al importar
       este paquete. Esto es requerido por Alembic para detectar los modelos
       y generar las migraciones automáticamente.

    2. Las relaciones entre modelos (relationship) se resuelvan correctamente
       sin importar el orden en que se usan en el código.

    3. Los demás módulos (services, routers) puedan importar desde un
       único punto: `from app.models import Rol, Permiso, ...`

Tablas cubiertas (prefijo `rol_`):
    - rol_roles
    - rol_permisos
    - rol_asignaciones_rol_permiso
    - rol_asignaciones_usuario_rol
    - rol_roles_contradictorios
    - rol_tokens_aplicacion
"""

from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.asignacion_rol_permiso import AsignacionRolPermiso
from app.models.asignacion_usuario_rol import AsignacionUsuarioRol
from app.models.rol_contradictorio import RolContradictorio
from app.models.token_aplicacion import TokenAplicacion

__all__ = [
    "Rol",
    "Permiso",
    "AsignacionRolPermiso",
    "AsignacionUsuarioRol",
    "RolContradictorio",
    "TokenAplicacion",
]