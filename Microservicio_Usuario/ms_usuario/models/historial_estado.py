from pydantic import BaseModel
from datetime import datetime


class HistorialRespuesta(BaseModel):
    id:                     int
    usuario_id:             int
    estado_anterior:        str
    estado_nuevo:           str
    motivo:                 str
    usuario_modificador_id: int
    created_at:             datetime

    model_config = {"from_attributes": True}
