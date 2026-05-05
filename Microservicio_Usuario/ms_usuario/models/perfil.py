from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class GeneroEnum(str, Enum):
    masculino         = "masculino"
    femenino          = "femenino"
    otro              = "otro"
    prefiero_no_decir = "prefiero_no_decir"


class PerfilCrearActualizar(BaseModel):
    """Crear o actualizar perfil extendido (USR-RF-014)."""
    tipo_documento_id:            int
    numero_documento:             str
    primer_nombre:                str
    segundo_nombre:               Optional[str] = None
    primer_apellido:              str
    segundo_apellido:             Optional[str] = None
    fecha_nacimiento:             date
    genero:                       GeneroEnum
    direccion_residencia:         str
    ciudad:                       str
    departamento:                 str
    telefono_fijo:                Optional[str] = None
    telefono_movil:               str
    contacto_emergencia_nombre:   str
    contacto_emergencia_telefono: str
    biografia:                    Optional[str] = None

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_edad_minima(cls, v: date) -> date:
        from datetime import date as d
        hoy  = d.today()
        edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
        if edad < 14:
            raise ValueError("Fecha de nacimiento inválida o usuario menor de 14 años")
        return v


class PerfilRespuesta(BaseModel):
    id:                           int
    usuario_id:                   int
    tipo_documento_id:            int
    tipo_documento_codigo:        Optional[str] = None
    tipo_documento_nombre:        Optional[str] = None
    numero_documento:             str
    primer_nombre:                str
    segundo_nombre:               Optional[str]
    primer_apellido:              str
    segundo_apellido:             Optional[str]
    fecha_nacimiento:             date
    genero:                       str
    direccion_residencia:         str
    ciudad:                       str
    departamento:                 str
    telefono_fijo:                Optional[str]
    telefono_movil:               str
    contacto_emergencia_nombre:   str
    contacto_emergencia_telefono: str
    biografia:                    Optional[str]
    created_at:                   datetime
    updated_at:                   datetime

    model_config = {"from_attributes": True}

