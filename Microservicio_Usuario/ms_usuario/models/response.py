from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


class RespuestaEstandar(BaseModel):
    request_id: str
    success: bool
    data: Any = None
    message: str
    timestamp: str

    @classmethod
    def ok(cls, request_id: str, data: Any, message: str):
        return cls(
            request_id=request_id,
            success=True,
            data=data,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def fail(cls, request_id: str, message: str, data: Any = None):
        return cls(
            request_id=request_id,
            success=False,
            data=data,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
