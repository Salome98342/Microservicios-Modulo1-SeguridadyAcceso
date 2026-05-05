"""
app/models/asignacion_usuario_rol.py
=====================================
Modelo ORM SQLAlchemy que representa la tabla
`rol_asignaciones_usuario_rol` en la base de datos `db_roles`.

Tabla:
    rol_asignaciones_usuario_rol

Responsabilidad:
    Tabla de asociación N:M entre usuarios externos (ms-usuarios [USR])
    y roles del sistema. Registra qué rol tiene asignado cada usuario,
    con soporte de baja lógica mediante el campo `estado`.

Restricciones de negocio:
    - `usuario_id` es una referencia externa a ms-usuarios [USR];
      no existe FK real entre bases de datos de distintos microservicios.
    - `estado` solo admite: 'activo' | 'inactivo'.
    - La baja es lógica: se cambia estado a 'inactivo' para mantener
      el historial completo de asignaciones (ROL-RF-016).
    - La prevención de roles contradictorios se aplica en la capa de
      servicio antes de insertar un nuevo registro (ROL-RF-014).

Referencias externas (sin FK real):
    usuario_id              → ms-usuarios [USR] (usuario al que se asigna el rol)
    asignado_por_usuario_id → ms-usuarios [USR] (administrador que realizó la asignación)

Referencias al documento maestro:
    ROL-RF-014 (Asignar rol a un usuario)
    ROL-RF-015 (Listar roles de un usuario)
    ROL-RF-016 (Remover rol de un usuario)
    ROL-RS-004 (Reactivar asignación usuario-rol)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin


class AsignacionUsuarioRol(Base, TimestampMixin):
    """
    Asociación N:M entre un usuario externo y un rol del sistema.

    Cada registro vincula a un usuario (identificado por su ID externo
    proveniente de ms-usuarios) con un rol activo del sistema.
    El campo `estado` permite desactivar la asignación sin eliminar
    el registro, preservando el historial completo.

    Attributes:
        id                      (int):      Identificador interno autoincremental.
        usuario_id              (int):      Referencia externa al usuario en ms-usuarios [USR].
                                            No se crea FK real entre bases de datos.
        rol_id                  (int):      FK hacia `rol_roles.id`.
        estado                  (str):      Estado de la asignación.
                                            Valores: 'activo' (defecto) | 'inactivo'.
        fecha_asignacion        (datetime): Marca de tiempo UTC de cuando se realizó
                                            la asignación. Se asigna automáticamente.
        asignado_por_usuario_id (int):      Referencia externa al administrador que
                                            realizó la asignación (ms-usuarios [USR]).
        created_at  (datetime):             Heredado de TimestampMixin.
        updated_at  (datetime):             Heredado de TimestampMixin.
    """

    __tablename__ = "rol_asignaciones_usuario_rol"

    id                      = Column(Integer,              primary_key=True, autoincrement=True)
    usuario_id              = Column(Integer,              nullable=False)
    rol_id                  = Column(Integer,              ForeignKey("rol_roles.id"), nullable=False)
    estado                  = Column(String(10),           nullable=False, default="activo")
    fecha_asignacion        = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    asignado_por_usuario_id = Column(Integer, nullable=False)

    # ── Relaciones ────────────────────────────────────────────────────────────

    rol = relationship(
        "Rol",
        back_populates="asignaciones_usuarios",
        doc="Rol asignado al usuario en esta entrada."
    )