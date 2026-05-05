from pydantic import BaseModel
from typing import Optional


class TipoDocumentoRespuesta(BaseModel):
    id:          int
    codigo:      str
    nombre:      str
    descripcion: Optional[str]

    model_config = {"from_attributes": True}
