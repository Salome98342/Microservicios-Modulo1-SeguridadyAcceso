from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import time, datetime


class PreferenciasActualizar(BaseModel):
    """Actualizar preferencias de notificación (USR-RF-019)."""
    notif_email:                Optional[bool] = None
    notif_sms:                  Optional[bool] = None
    notif_push:                 Optional[bool] = None
    canal_preferido:            Optional[str]  = None
    horario_no_molestar_inicio: Optional[time] = None
    horario_no_molestar_fin:    Optional[time] = None

    @model_validator(mode="after")
    def validar_horarios(self) -> "PreferenciasActualizar":
        inicio = self.horario_no_molestar_inicio
        fin    = self.horario_no_molestar_fin
        if (inicio is None) != (fin is None):
            raise ValueError("Debe proporcionar ambos horarios de no molestar o ninguno")
        if inicio and fin and inicio >= fin:
            raise ValueError("El horario de inicio debe ser anterior al horario de fin")
        return self


class PreferenciasRespuesta(BaseModel):
    id:                         int
    usuario_id:                 int
    notif_email:                bool
    notif_sms:                  bool
    notif_push:                 bool
    canal_preferido:            str
    horario_no_molestar_inicio: Optional[time]
    horario_no_molestar_fin:    Optional[time]
    created_at:                 datetime
    updated_at:                 datetime

    model_config = {"from_attributes": True}
