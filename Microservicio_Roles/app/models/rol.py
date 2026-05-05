"""
app/models/rol.py
=================
Modelo ORM SQLAlchemy que representa la tabla `rol_roles` en la base
de datos `db_roles` del microservicio ms-roles [ROL].

Tabla:
    rol_roles

Responsabilidad:
    Almacena la definición de los roles del sistema ERP universitario.
    Cada rol agrupa un conjunto de permisos que se asignan directamente
    (sin herencia entre roles).

Relaciones:
    - AsignacionRolPermiso  (1:N): permisos asignados a este rol.
    - AsignacionUsuarioRol  (1:N): usuarios que tienen este rol.
    - RolContradictorio     (1:N): pares de roles incompatibles donde
                                   este rol es parte del par (como A o como B).

Restricciones de negocio:
    - `nombre` es único en todo el sistema.
    - `estado` solo admite los valores: 'activo' | 'inactivo'.
    - La baja es lógica (soft delete): se cambia estado a 'inactivo',
      el registro nunca se elimina físicamente.

Referencias al documento maestro:
    ROL-RF-001 (Crear rol)
    ROL-RF-002 (Consultar rol por ID)
    ROL-RF-003 (Listar roles)
    ROL-RF-004 (Actualizar rol)
    ROL-RF-005 (Desactivar rol)
    ROL-RS-003 (Reactivar rol)
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Rol(Base, TimestampMixin):
    """
    Representa un rol del sistema ERP universitario.

    Un rol es una agrupación lógica de permisos que se asigna a uno
    o varios usuarios. Los roles no tienen herencia; cada rol recibe
    sus permisos de forma directa e independiente.

    Attributes:
        id          (int):  Identificador interno autoincremental. Clave primaria.
        nombre      (str):  Nombre único del rol en el sistema.
                            Ejemplos: 'Administrador', 'Docente', 'Estudiante'.
        descripcion (str):  Descripción detallada del propósito del rol.
                            Puede ser nulo.
        estado      (str):  Estado lógico del rol. Valores permitidos:
                            'activo' (por defecto) | 'inactivo'.
        created_at  (datetime): Heredado de TimestampMixin.
        updated_at  (datetime): Heredado de TimestampMixin.
    """

    __tablename__ = "rol_roles"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    nombre      = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    estado      = Column(String(10), nullable=False, default="activo")

    # ── Relaciones ────────────────────────────────────────────────────────────

    asignaciones_permisos = relationship(
        "AsignacionRolPermiso",
        back_populates="rol",
        doc="Lista de permisos asignados a este rol (tabla rol_asignaciones_rol_permiso)."
    )

    asignaciones_usuarios = relationship(
        "AsignacionUsuarioRol",
        back_populates="rol",
        doc="Lista de usuarios que tienen este rol asignado (tabla rol_asignaciones_usuario_rol)."
    )

    contradicciones_a = relationship(
        "RolContradictorio",
        foreign_keys="RolContradictorio.rol_a_id",
        back_populates="rol_a",
        doc="Pares de contradicción donde este rol ocupa la posición A."
    )

    contradicciones_b = relationship(
        "RolContradictorio",
        foreign_keys="RolContradictorio.rol_b_id",
        back_populates="rol_b",
        doc="Pares de contradicción donde este rol ocupa la posición B."
    )

    def __repr__(self) -> str:
        """Representación legible del objeto para depuración."""
        return f"<Rol id={self.id} nombre={self.nombre} estado={self.estado}>"