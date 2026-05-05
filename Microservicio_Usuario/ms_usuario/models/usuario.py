from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UsuarioCrear(BaseModel):
    """Datos para crear un usuario (USR-RF-006)."""
    username:            str
    email:               EmailStr
    password_encrypted:  str = None   # AES-256 Base64 (producción)
    password_plana:      str = None   # Texto plano (DEBUG_MODE solo)
    rol_id:              int

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        return v.strip()


class UsuarioActualizar(BaseModel):
    """Campos actualizables (USR-RF-010). Todos opcionales."""
    username: Optional[str]      = None
    email:    Optional[EmailStr] = None
    rol_id:   Optional[int]      = None

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        return v.strip() if v else v


class CambiarPassword(BaseModel):
    """Cambio de contraseña autenticado (USR-RF-022)."""
    password_actual_encrypted: str
    password_nueva_encrypted:  str


class CambiarEstadoBody(BaseModel):
    """Cuerpo para cambio de estado o desactivación."""
    estado_nuevo: Optional[str] = None
    motivo:       str


class UsuarioRespuesta(BaseModel):
    """Datos de usuario expuestos al cliente. Sin password_hash."""
    id:         int
    username:   str
    email:      str
    estado:     str
    rol_id:     int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UsuarioConHash(UsuarioRespuesta):
    """
    Incluye password_hash.
    SOLO para uso interno de ms-autenticacion [AUTH].
    Nunca retornar en endpoints públicos.
    """
    password_hash: str


class ResultadoPaginado(BaseModel):
    resultados:       list[UsuarioRespuesta]
    total_registros:  int
    total_paginas:    int
    pagina_actual:    int
    items_por_pagina: int


class CifrarPasswordDebug(BaseModel):
    """[DEBUG ONLY] Utilidad para cifrar contraseñas en desarrollo."""
    password_plana: str

