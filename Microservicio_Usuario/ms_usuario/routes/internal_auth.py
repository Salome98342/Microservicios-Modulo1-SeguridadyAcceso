from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import services.usuario_service as svc


router = APIRouter(prefix="/internal/users", tags=["Internal Auth"])


class VerifyCredentialsRequest(BaseModel):
    username: str
    encrypted_password: str
    request_trace_id: str = ""


@router.post("/credentials/verify")
async def verify_credentials(req: VerifyCredentialsRequest):
    data, error = svc.verificar_credenciales_internas(req.username, req.encrypted_password)
    if error == "INVALID_CREDENTIALS":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if data and data.get("status") == "BLOCKED":
        raise HTTPException(status_code=423, detail="Usuario bloqueado")

    return data
