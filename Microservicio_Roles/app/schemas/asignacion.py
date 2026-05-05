from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import Estado


class RolMinimo(BaseModel):
    id: int = Field(..., description="Identificador único del rol")
    nombre: str = Field(..., description="Nombre del rol")

    model_config = {
        "from_attributes": True,
    }


class PermisoMinimo(BaseModel):
    id: int = Field(..., description="Identificador único del permiso")
    codigo: str = Field(..., description="Código del permiso")
    nombre: str = Field(..., description="Nombre del permiso")

    model_config = {
        "from_attributes": True,
    }


class AsignacionUsuarioRolBase(BaseModel):
    usuario_id: int = Field(..., description="Identificador externo del usuario")
    rol_id: int = Field(..., description="Identificador del rol asignado")
    asignado_por_usuario_id: int = Field(
        ..., description="Identificador externo del usuario que realizó la asignación"
    )
    estado: Estado = Field("activo", description="Estado lógico de la asignación")
    fecha_asignacion: Optional[datetime] = Field(
        None,
        description="Fecha y hora UTC en que se realizó la asignación"
    )


class AsignacionUsuarioRolCreate(AsignacionUsuarioRolBase):
    pass


class AsignacionUsuarioRolUpdate(BaseModel):
    usuario_id: Optional[int] = Field(None, description="Identificador externo del usuario")
    rol_id: Optional[int] = Field(None, description="Identificador del rol asignado")
    asignado_por_usuario_id: Optional[int] = Field(
        None,
        description="Identificador externo del usuario que realizó la asignación"
    )
    estado: Optional[Estado] = Field(None, description="Estado lógico de la asignación")


class AsignacionUsuarioRolResponse(AsignacionUsuarioRolBase):
    id: int = Field(..., description="Identificador único de la asignación")
    rol: Optional[RolMinimo] = Field(None, description="Datos del rol asignado")

    model_config = {
        "from_attributes": True,
    }


class AsignacionRolPermisoBase(BaseModel):
    rol_id: int = Field(..., description="Identificador del rol")
    permiso_id: int = Field(..., description="Identificador del permiso")
    asignado_por_usuario_id: int = Field(
        ..., description="Identificador externo del usuario que realizó la asignación"
    )
    fecha_asignacion: Optional[datetime] = Field(
        None,
        description="Fecha y hora UTC en que se realizó la asignación"
    )


class AsignacionRolPermisoCreate(AsignacionRolPermisoBase):
    pass


class AsignacionRolPermisoUpdate(BaseModel):
    rol_id: Optional[int] = Field(None, description="Identificador del rol")
    permiso_id: Optional[int] = Field(None, description="Identificador del permiso")
    asignado_por_usuario_id: Optional[int] = Field(
        None,
        description="Identificador externo del usuario que realizó la asignación"
    )


class AsignacionRolPermisoResponse(AsignacionRolPermisoBase):
    id: int = Field(..., description="Identificador único de la asignación")
    rol: Optional[RolMinimo] = Field(None, description="Datos del rol asociado")
    permiso: Optional[PermisoMinimo] = Field(None, description="Datos del permiso asociado")

    model_config = {
        "from_attributes": True,
    }
