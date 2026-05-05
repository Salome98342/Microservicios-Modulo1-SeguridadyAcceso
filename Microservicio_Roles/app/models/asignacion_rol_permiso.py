"""
app/models/asignacion_rol_permiso.py
=====================================
Modelo ORM SQLAlchemy que representa la tabla
`rol_asignaciones_rol_permiso` en la base de datos `db_roles`.

Tabla:
    rol_asignaciones_rol_permiso

Responsabilidad:
    Tabla de asociación N:M entre roles y permisos.
    Registra qué permisos tiene asignado cada rol, con trazabilidad
    completa de quién realizó la asignación y en qué momento.

Restricciones de negocio:
    - La combinación (rol_id, permiso_id) debe ser única: un permiso
      no puede asignarse dos veces al mismo rol.
    - `asignado_por_usuario_id` es una referencia externa al microservicio
      ms-usuarios [USR]; no existe FK real en base de datos entre servicios.

Referencias externas (sin FK real):
    asignado_por_usuario_id → ms-usuarios [USR] (usuario administrador)

Referencias al documento maestro:
    ROL-RF-012 (Asignar permisos a un rol)
    ROL-RF-013 (Remover permiso de un rol)
    ROL-RS-001 (Consultar permisos asignados a un rol)
"""

from sqlalchemy import Column, Integer, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin


class AsignacionRolPermiso(Base, TimestampMixin):
    """
    Asociación N:M entre un rol y un permiso del sistema.

    Cada registro indica que el rol identificado por `rol_id` tiene
    autorización para ejecutar la funcionalidad representada por `permiso_id`.
    La asignación queda trazada con la fecha y el usuario que la realizó.

    Attributes:
        id                      (int):      Identificador interno autoincremental.
        rol_id                  (int):      FK hacia `rol_roles.id`.
        permiso_id              (int):      FK hacia `rol_permisos.id`.
        fecha_asignacion        (datetime): Marca de tiempo UTC de la asignación.
                                            Se asigna automáticamente al crear el registro.
        asignado_por_usuario_id (int):      Referencia externa al usuario administrador
                                            que realizó la asignación (ms-usuarios [USR]).
                                            No se crea FK real entre bases de datos.
        created_at  (datetime):             Heredado de TimestampMixin.
        updated_at  (datetime):             Heredado de TimestampMixin.

    Restricciones:
        uq_arp_rol_permiso: UNIQUE (rol_id, permiso_id) — evita duplicados.
    """

    __tablename__ = "rol_asignaciones_rol_permiso"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    rol_id                  = Column(Integer, ForeignKey("rol_roles.id"),    nullable=False)
    permiso_id              = Column(Integer, ForeignKey("rol_permisos.id"), nullable=False)
    fecha_asignacion        = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    asignado_por_usuario_id = Column(Integer, nullable=False)

    # ── Restricciones de tabla ────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("rol_id", "permiso_id", name="uq_arp_rol_permiso"),
    )

    # ── Relaciones ────────────────────────────────────────────────────────────

    rol = relationship(
        "Rol",
        back_populates="asignaciones_permisos",
        doc="Rol al que pertenece esta asignación."
    )

    permiso = relationship(
        "Permiso",
        back_populates="asignaciones_roles",
        doc="Permiso que fue asignado al rol."
    )