from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Estado = Literal["activo", "inactivo"]


class OrmModel(BaseModel):
    model_config = {
        "from_attributes": True,
    }


class TimestampedModel(OrmModel):
    created_at: Optional[datetime] = Field(
        None,
        description="Fecha y hora de creación en UTC"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Fecha y hora de última modificación en UTC"
    )
