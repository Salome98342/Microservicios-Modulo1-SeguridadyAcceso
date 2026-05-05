"""Schema definitions for permission objects handled by ms-roles.

This module defines the validation contracts for permission creation,
update, and response payloads used in API endpoints and internal services.

Usage in the system:
- `PermisoCreate` validates incoming create requests from HTTP endpoints.
- `PermisoUpdate` validates partial updates for existing permissions.
- `PermisoResponse` serializes persisted permissions for responses.
- The alias `operacion` allows compatibility with external request payloads.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class PermisoBase(BaseModel):
    """Base schema for permiso payloads used across ms-roles.

    Contiene los campos comunes a creación, actualización y respuesta.
    El campo `operacion` se normaliza durante el procesamiento del servicio
    para aceptar tanto valores en mayúsculas como valores en español.
    """

    codigo: str = Field(..., max_length=60, description="Código único del permiso")
    nombre: str = Field(..., max_length=150, description="Nombre del permiso")
    descripcion: Optional[str] = Field(None, description="Descripción del permiso")
    modulo: str = Field(..., max_length=80, description="Módulo al que pertenece el permiso")
    microservicio_origen: str = Field(
        "ms-roles",
        max_length=60,
        description="Microservicio origen del permiso",
    )
    funcionalidad_asociada: str = Field(
        "Gestión de permisos",
        max_length=150,
        description="Funcionalidad asociada al permiso",
    )
    metodo_operacion: str = Field(
        ...,
        alias="operacion",
        description=(
            "Tipo de operación: READ | CREATE | UPDATE | DELETE "
            "o consulta | creacion | actualizacion | eliminacion"
        ),
    )

    model_config = {
        "populate_by_name": True,
    }


class PermisoCreate(PermisoBase):
    """Schema utilizado para crear un permiso nuevo en ms-roles.

    Se emplea en los endpoints de creación de permisos y en el seed de datos.
    """


class PermisoUpdate(BaseModel):
    """Schema utilizado para la actualización parcial de permisos.

    Solo los campos presentes en la petición se aplican sobre el permiso existente.
    """
    nombre: Optional[str] = Field(None, max_length=150, description="Nombre del permiso")
    descripcion: Optional[str] = Field(None, description="Descripción del permiso")
    modulo: Optional[str] = Field(None, max_length=80, description="Módulo al que pertenece el permiso")
    microservicio_origen: Optional[str] = Field(
        None, max_length=60, description="Microservicio origen del permiso"
    )
    funcionalidad_asociada: Optional[str] = Field(
        None, max_length=150, description="Funcionalidad asociada al permiso"
    )
    metodo_operacion: Optional[str] = Field(
        None,
        alias="operacion",
        description=(
            "Tipo de operación: READ | CREATE | UPDATE | DELETE "
            "o consulta | creacion | actualizacion | eliminacion"
        ),
    )

    model_config = {
        "populate_by_name": True,
    }


class PermisoResponse(PermisoBase, TimestampedModel):
    """Response schema for permiso payloads returned by ms-roles.

    Incluye metadatos de auditoría temporal heredados de TimestampedModel.
    """

    id: int = Field(..., description="Identificador único del permiso")

    model_config = {
        "from_attributes": True,
    }
