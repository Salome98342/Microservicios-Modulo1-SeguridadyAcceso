from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import Estado


class ValidacionTokenRequest(BaseModel):
    token: str = Field(..., description="Token de aplicación recibido del servicio")
    servicio_origen: str = Field(..., description="Nombre del microservicio que envía el token")


class ValidacionTokenResponse(BaseModel):
    valido: bool = Field(..., description="Indica si el token es válido")
    servicio: Optional[str] = Field(None, description="Nombre del servicio identificado por el token")
    estado: Optional[Estado] = Field(None, description="Estado lógico del token")
    mensaje: Optional[str] = Field(None, description="Mensaje legible de validación")
