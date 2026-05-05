"""
app/db/base.py
==============
Define la clase base declarativa de SQLAlchemy y el mixin de timestamps
reutilizable por todos los modelos ORM del microservicio ms-roles.

Responsabilidad:
    - Proveer `Base`: clase padre de todos los modelos ORM.
    - Proveer `TimestampMixin`: agrega automáticamente las columnas
      `created_at` y `updated_at` a cualquier modelo que lo herede.

Uso:
    from app.db.base import Base, TimestampMixin

    class MiModelo(Base, TimestampMixin):
        __tablename__ = "mi_tabla"
        ...
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone


class Base(DeclarativeBase):
    """
    Clase base declarativa de SQLAlchemy.

    Todos los modelos ORM del proyecto deben heredar de esta clase.
    SQLAlchemy la usa para registrar las tablas y construir el
    metadata necesario para Alembic y las migraciones.
    """
    pass


class TimestampMixin:
    """
    Mixin que agrega las columnas de auditoría de tiempo a un modelo ORM.

    Columnas que inyecta:
        created_at (DateTime): Fecha y hora UTC de creación del registro.
                               Se asigna automáticamente al hacer INSERT.
        updated_at (DateTime): Fecha y hora UTC de la última modificación.
                               Se actualiza automáticamente en cada UPDATE.

    Uso:
        class MiModelo(Base, TimestampMixin):
            __tablename__ = "mi_tabla"
            id = Column(Integer, primary_key=True)
            # created_at y updated_at se heredan automáticamente
    """

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )