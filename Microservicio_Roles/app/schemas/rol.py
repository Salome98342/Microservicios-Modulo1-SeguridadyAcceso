from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import Estado, TimestampedModel


class RolBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre único del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    estado: Estado = Field("activo", description="Estado lógico del rol")


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    estado: Optional[Estado] = Field(None, description="Estado lógico del rol")


class RolResponse(RolBase, TimestampedModel):
    id: int = Field(..., description="Identificador único del rol")

    model_config = {
        "from_attributes": True,
    }
