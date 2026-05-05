"""
app/models/rol_contradictorio.py
=================================
Modelo ORM SQLAlchemy que representa la tabla
`rol_roles_contradictorios` en la base de datos `db_roles`.

Tabla:
    rol_roles_contradictorios

Responsabilidad:
    Tabla de configuración que define pares de roles mutuamente excluyentes.
    Si un usuario tiene asignado `rol_a`, no puede tener asignado `rol_b`
    y viceversa. Habilita la regla de negocio de prevención de conflictos
    aplicada en ROL-RF-014 durante la asignación de roles a usuarios.

Restricciones de negocio:
    - La combinación (rol_a_id, rol_b_id) debe ser única.
    - Un rol no puede ser contradictorio consigo mismo (rol_a_id ≠ rol_b_id).
    - La relación es BIDIRECCIONAL: si se registra el par (A, B),
      la lógica de aplicación debe tratar (B, A) como equivalente.
      Esta bidireccionalidad se implementa en la capa de servicio,
      no mediante una segunda fila en la base de datos.

Auto-relación:
    Ambas columnas (rol_a_id y rol_b_id) referencian a la misma
    tabla `rol_roles`, formando una auto-relación.

Referencias al documento maestro:
    ROL-RF-014 (Asignar rol a un usuario — verificación de conflictos)
    Datos semilla: 4 pares contradictorios definidos en ROL-RF-018
"""

from sqlalchemy import (
    Column, Integer, Text,
    UniqueConstraint, CheckConstraint, ForeignKey
)
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class RolContradictorio(Base, TimestampMixin):
    """
    Par de roles mutuamente excluyentes en el sistema ERP.

    Un registro en esta tabla significa que ningún usuario puede tener
    activos simultáneamente ambos roles del par. La verificación se
    realiza en la capa de servicio antes de cada asignación usuario-rol.

    Attributes:
        id       (int): Identificador interno autoincremental.
        rol_a_id (int): FK hacia `rol_roles.id`. Primer rol del par contradictorio.
        rol_b_id (int): FK hacia `rol_roles.id`. Segundo rol del par contradictorio.
        motivo   (str): Justificación legible del motivo de incompatibilidad.
                        Puede ser nulo.
        created_at  (datetime): Heredado de TimestampMixin.
        updated_at  (datetime): Heredado de TimestampMixin.

    Restricciones:
        uq_rc_par:    UNIQUE (rol_a_id, rol_b_id) — evita duplicados del mismo par.
        ck_rc_no_self: CHECK (rol_a_id <> rol_b_id) — un rol no contradice a sí mismo.
    """

    __tablename__ = "rol_roles_contradictorios"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    rol_a_id = Column(Integer, ForeignKey("rol_roles.id"), nullable=False)
    rol_b_id = Column(Integer, ForeignKey("rol_roles.id"), nullable=False)
    motivo   = Column(Text, nullable=True)

    # ── Restricciones de tabla ────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("rol_a_id", "rol_b_id", name="uq_rc_par"),
        CheckConstraint("rol_a_id <> rol_b_id",  name="ck_rc_no_self"),
    )

    # ── Relaciones (auto-relación sobre rol_roles) ────────────────────────────

    rol_a = relationship(
        "Rol",
        foreign_keys=[rol_a_id],
        back_populates="contradicciones_a",
        doc="Primer rol del par contradictorio (posición A)."
    )

    rol_b = relationship(
        "Rol",
        foreign_keys=[rol_b_id],
        back_populates="contradicciones_b",
        doc="Segundo rol del par contradictorio (posición B)."
    )