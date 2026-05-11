from typing import Any

from fastapi import APIRouter, Depends, Header, Query

from ..schemas.auth import CreateAppTokenRequest, ForceCloseRequest, LoginRequest, UpdateAppTokenRequest, ValidateSessionRequest
from ..services.auth_service import (
    create_app_token,
    force_close_session,
    get_access_history,
    list_app_tokens,
    list_sessions,
    login,
    logout,
    require_admin,
    require_auth,
    update_app_token,
    validate_session,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/auth/login")
def login_controller(req: LoginRequest) -> dict[str, Any]:
    return login(req)


@router.post("/v1/auth/logout")
def logout_controller(
    request_trace_id: str = Header(default=""),
    auth: dict[str, Any] = Depends(require_auth),
) -> dict[str, str]:
    return logout(auth, request_trace_id)


@router.post("/v1/auth/session/validate")
def validate_session_controller(req: ValidateSessionRequest) -> dict[str, Any]:
    return validate_session(req.token)


@router.post("/v1/auth/validate-session")
def validate_session_alias_controller(req: ValidateSessionRequest) -> dict[str, Any]:
    """Alias para compatibilidad con Postman."""
    return validate_session(req.token)


@router.post("/v1/auth/refresh-token")
def refresh_token_controller(
    auth: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Refrescar el token del usuario actual."""
    # Usa el token anterior para obtener un nuevo token
    return validate_session(auth.get("token", ""))


@router.post("/v1/app-tokens")
def create_app_token_controller(req: CreateAppTokenRequest, _: dict[str, Any] = Depends(require_admin)) -> dict[str, str]:
    return create_app_token(req)


@router.get("/v1/app-tokens")
def list_app_tokens_controller(_: dict[str, Any] = Depends(require_admin)) -> list[dict[str, Any]]:
    return list_app_tokens()


@router.put("/v1/app-tokens/{token_id}")
def update_app_token_controller(
    token_id: str,
    req: UpdateAppTokenRequest,
    _: dict[str, Any] = Depends(require_admin),
) -> dict[str, str]:
    return update_app_token(token_id, req)


@router.delete("/v1/app-tokens/{token_id}")
def disable_app_token_controller(
    token_id: str,
    updated_by: str = Query(...),
    _: dict[str, Any] = Depends(require_admin),
) -> dict[str, str]:
    return update_app_token(token_id, UpdateAppTokenRequest(updated_by=updated_by, status="INACTIVE"))


@router.get("/v1/sessions")
def list_sessions_controller(
    user_id: str | None = Query(default=None),
    _: dict[str, Any] = Depends(require_admin),
) -> list[dict[str, Any]]:
    return list_sessions(user_id)


@router.get("/v1/sesiones")
def list_sessions_spanish_alias_controller(
    user_id: str | None = Query(default=None),
    _: dict[str, Any] = Depends(require_admin),
) -> list[dict[str, Any]]:
    """Alias en espanol para compatibilidad con Postman."""
    return list_sessions(user_id)


@router.post("/v1/sessions/{session_id}/force-close")
def force_close_session_controller(
    session_id: str,
    req: ForceCloseRequest,
    auth: dict[str, Any] = Depends(require_admin),
) -> dict[str, str]:
    return force_close_session(session_id, req, auth)


@router.get("/v1/access-history")
def get_access_history_controller(
    user_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _: dict[str, Any] = Depends(require_admin),
) -> list[dict[str, Any]]:
    return get_access_history(user_id, event_type, start_date, end_date)
