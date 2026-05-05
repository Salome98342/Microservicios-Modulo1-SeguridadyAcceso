import base64
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib import error, parse, request

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from psycopg import IntegrityError
from fastapi import Depends, Header, HTTPException

from ..core.config import AES256_KEY_B64, AUTH_USE_STUB_FALLBACK, HTTP_TIMEOUT_SECONDS, JWT_ALGORITHM, JWT_ISSUER, JWT_SECRET, ROLES_SERVICE_URL, USERS_SERVICE_URL
from ..core.database import get_conn


DEMO_USERS = {
    "admin": {
        "user_id": "u-admin",
        "encrypted_password": "enc_admin123",
        "status": "ACTIVE",
    },
    "maria": {
        "user_id": "u-maria",
        "encrypted_password": "enc_maria123",
        "status": "ACTIVE",
    },
}

DEMO_ROLES = {
    "u-admin": {"role": "ADMIN", "permissions": ["auth:manage", "sessions:force_close"]},
    "u-maria": {"role": "DOCENTE", "permissions": ["auth:use"]},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    conn: Any,
    user_id: str,
    event_type: str,
    ip_origin: str,
    user_agent: str,
    request_trace_id: str,
) -> None:
    conn.execute(
        """
        INSERT INTO access_history (id, user_id, event_type, ip_origin, user_agent, event_at, request_trace_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (str(uuid.uuid4()), user_id, event_type, ip_origin, user_agent, now_iso(), request_trace_id),
    )


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def _http_post_json(url: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any] | None]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            status = int(resp.status)
            raw = resp.read().decode("utf-8")
            return status, json.loads(raw) if raw else None
    except error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8") if exc.fp else ""
        return status, json.loads(raw) if raw else None


def _http_get_json(url: str, headers: dict[str, str]) -> tuple[int, dict[str, Any] | None]:
    req = request.Request(
        url,
        method="GET",
        headers={"Accept": "application/json", **headers},
    )
    try:
        with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            status = int(resp.status)
            raw = resp.read().decode("utf-8")
            return status, json.loads(raw) if raw else None
    except error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8") if exc.fp else ""
        return status, json.loads(raw) if raw else None


def verify_credentials_with_users_service(
    username: str,
    encrypted_password: str,
    request_trace_id: str,
) -> dict[str, Any]:
    if USERS_SERVICE_URL:
        url = _join_url(USERS_SERVICE_URL, "/internal/users/credentials/verify")
        payload = {
            "username": username,
            "encrypted_password": encrypted_password,
            "request_trace_id": request_trace_id,
        }
        try:
            status, data = _http_post_json(url, payload)
            if status == 200 and data:
                return {
                    "ok": True,
                    "user": {
                        "user_id": data.get("user_id", ""),
                        "status": data.get("status", "ACTIVE"),
                    },
                }
            if status == 423:
                return {
                    "ok": False,
                    "reason": "BLOCKED",
                    "user": {"user_id": data.get("user_id", "") if data else "", "status": "BLOCKED"},
                }
            if status == 401:
                return {"ok": False, "reason": "INVALID_CREDENTIALS"}
            if not AUTH_USE_STUB_FALLBACK:
                raise HTTPException(status_code=503, detail="ms-usuarios no disponible")
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            if not AUTH_USE_STUB_FALLBACK:
                raise HTTPException(status_code=503, detail="Error consultando ms-usuarios")

    user = DEMO_USERS.get(username)
    if not user:
        return {"ok": False, "reason": "INVALID_CREDENTIALS"}
    if user["status"] == "BLOCKED":
        return {"ok": False, "reason": "BLOCKED", "user": user}
    if user["encrypted_password"] != encrypted_password:
        return {"ok": False, "reason": "INVALID_CREDENTIALS", "user": user}
    return {"ok": True, "user": user}


def get_role_permissions_from_roles_service(user_id: str) -> dict[str, Any]:
    if ROLES_SERVICE_URL:
        encoded_user_id = parse.quote(user_id, safe="")
        url = _join_url(ROLES_SERVICE_URL, f"/internal/roles/users/{encoded_user_id}/permissions")
        try:
            status, data = _http_get_json(url, headers={"request_trace_id": str(uuid.uuid4())})
            if status == 200 and data:
                role = data.get("role", "BASIC")
                permissions = data.get("permissions", [])
                if not isinstance(permissions, list):
                    permissions = []
                return {"role": role, "permissions": permissions}
            if not AUTH_USE_STUB_FALLBACK:
                raise HTTPException(status_code=503, detail="ms-roles no disponible")
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            if not AUTH_USE_STUB_FALLBACK:
                raise HTTPException(status_code=503, detail="Error consultando ms-roles")

    return DEMO_ROLES.get(user_id, {"role": "BASIC", "permissions": []})


def increment_failed_attempt(conn: Any, user_id: str) -> tuple[int, bool]:
    row = conn.execute(
        "SELECT failed_attempts, is_blocked FROM login_attempt_control WHERE user_id = %s",
        (user_id,),
    ).fetchone()
    current = int(row["failed_attempts"]) if row else 0
    new_count = current + 1
    blocked = new_count >= 5
    if row:
        conn.execute(
            """
            UPDATE login_attempt_control
            SET failed_attempts = %s, is_blocked = %s, updated_at = %s
            WHERE user_id = %s
            """,
            (new_count, 1 if blocked else int(row["is_blocked"]), now_iso(), user_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO login_attempt_control (user_id, failed_attempts, is_blocked, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, new_count, 1 if blocked else 0, now_iso()),
        )
    return new_count, blocked


def reset_failed_attempts(conn: Any, user_id: str) -> None:
    row = conn.execute(
        "SELECT user_id FROM login_attempt_control WHERE user_id = %s",
        (user_id,),
    ).fetchone()
    if row:
        conn.execute(
            """
            UPDATE login_attempt_control
            SET failed_attempts = 0, is_blocked = 0, updated_at = %s
            WHERE user_id = %s
            """,
            (now_iso(), user_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO login_attempt_control (user_id, failed_attempts, is_blocked, updated_at)
            VALUES (%s, 0, 0, %s)
            """,
            (user_id, now_iso()),
        )


def ensure_not_blocked_locally(conn: Any, user_id: str) -> None:
    row = conn.execute(
        "SELECT is_blocked FROM login_attempt_control WHERE user_id = %s",
        (user_id,),
    ).fetchone()
    if row and int(row["is_blocked"]) == 1:
        raise HTTPException(status_code=423, detail="Cuenta bloqueada por intentos fallidos")


def create_jwt(user_id: str, role: str, permissions: list[str]) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "permissions": permissions,
        "iss": JWT_ISSUER,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token invalido") from exc


def parse_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization requerido")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization invalido")
    return parts[1]


def require_auth(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = parse_bearer_token(authorization)
    claims = decode_jwt(token)
    conn = get_conn()
    invalidated = conn.execute(
        "SELECT token FROM invalidated_tokens WHERE token = %s",
        (token,),
    ).fetchone()
    conn.close()
    if invalidated:
        raise HTTPException(status_code=401, detail="Token invalidado")
    return {"token": token, "claims": claims}


def require_admin(auth: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    role = auth["claims"].get("role")
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="Se requiere rol ADMIN")
    return auth


def get_aes_key() -> bytes:
    try:
        key = base64.b64decode(AES256_KEY_B64)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AES256_KEY_B64 invalida") from exc
    if len(key) != 32:
        raise HTTPException(status_code=500, detail="AES256_KEY_B64 debe decodificar a 32 bytes")
    return key


def aes_encrypt(plain_text: str) -> str:
    key = get_aes_key()
    nonce = os.urandom(12)
    cipher = AESGCM(key)
    encrypted = cipher.encrypt(nonce, plain_text.encode("utf-8"), None)
    payload = {
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(encrypted).decode("utf-8"),
    }
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def login(req: Any) -> dict[str, Any]:
    conn = get_conn()

    verify_result = verify_credentials_with_users_service(
        req.username,
        req.encrypted_password,
        req.request_trace_id,
    )
    user = verify_result.get("user")

    if user:
        ensure_not_blocked_locally(conn, user["user_id"])

    if not verify_result["ok"]:
        user_id = user["user_id"] if user else "UNKNOWN"
        attempts = 0
        blocked = False
        if user:
            attempts, blocked = increment_failed_attempt(conn, user_id)
        log_event(conn, user_id, "LOGIN_FAIL", req.ip, req.user_agent, req.request_trace_id)
        if blocked:
            log_event(conn, user_id, "ACCOUNT_LOCKED", req.ip, req.user_agent, req.request_trace_id)
        conn.commit()
        conn.close()
        if verify_result.get("reason") == "BLOCKED" or blocked:
            raise HTTPException(status_code=423, detail="Cuenta bloqueada")
        raise HTTPException(status_code=401, detail=f"Credenciales invalidas. Intentos fallidos: {attempts}")

    user_id = user["user_id"]
    reset_failed_attempts(conn, user_id)

    role_data = get_role_permissions_from_roles_service(user_id)
    token = create_jwt(user_id, role_data["role"], role_data["permissions"])

    session_id = str(uuid.uuid4())
    timestamp = now_iso()
    conn.execute(
        """
        INSERT INTO sessions_user (
            id, user_id, token, ip_origin, user_agent,
            created_at, last_activity_at, status,
            record_created_at, record_updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            session_id,
            user_id,
            token,
            req.ip,
            req.user_agent,
            timestamp,
            timestamp,
            "ACTIVE",
            timestamp,
            timestamp,
        ),
    )
    log_event(conn, user_id, "LOGIN_OK", req.ip, req.user_agent, req.request_trace_id)
    conn.commit()
    conn.close()

    return {
        "access_token": token,
        "token_type": "Bearer",
        "session_id": session_id,
        "user_id": user_id,
        "role": role_data["role"],
        "permissions": role_data["permissions"],
    }


def logout(auth: dict[str, Any], request_trace_id: str) -> dict[str, str]:
    token = auth["token"]
    claims = auth["claims"]
    user_id = claims["sub"]

    conn = get_conn()
    now = now_iso()
    conn.execute(
        """
        UPDATE sessions_user
        SET status = 'CLOSED', record_updated_at = %s, last_activity_at = %s
        WHERE token = %s AND status = 'ACTIVE'
        """,
        (now, now, token),
    )
    conn.execute(
        "INSERT INTO invalidated_tokens (token, invalidated_at) VALUES (%s, %s) ON CONFLICT (token) DO NOTHING",
        (token, now),
    )
    log_event(conn, user_id, "LOGOUT_OK", "0.0.0.0", "unknown", request_trace_id)
    conn.commit()
    conn.close()
    return {"message": "Sesion cerrada"}


def validate_session(token: str) -> dict[str, Any]:
    claims = decode_jwt(token)
    user_id = claims.get("sub")

    conn = get_conn()
    invalidated = conn.execute(
        "SELECT token FROM invalidated_tokens WHERE token = %s",
        (token,),
    ).fetchone()
    if invalidated:
        conn.close()
        return {"valid": False, "reason": "TOKEN_INVALIDATED"}

    row = conn.execute(
        "SELECT id FROM sessions_user WHERE token = %s AND status = 'ACTIVE'",
        (token,),
    ).fetchone()
    if not row:
        conn.close()
        return {"valid": False, "reason": "SESSION_NOT_ACTIVE"}

    conn.execute(
        "UPDATE sessions_user SET last_activity_at = %s, record_updated_at = %s WHERE token = %s",
        (now_iso(), now_iso(), token),
    )
    conn.commit()
    conn.close()

    return {
        "valid": True,
        "user_id": user_id,
        "role": claims.get("role"),
        "permissions": claims.get("permissions", []),
    }


def create_app_token(req: Any) -> dict[str, str]:
    conn = get_conn()
    token_id = str(uuid.uuid4())
    now = now_iso()
    encrypted = aes_encrypt(req.token_value)
    try:
        conn.execute(
            """
            INSERT INTO app_tokens (
                id, name_service, encrypted_token, description,
                status, created_at, updated_by, updated_at
            )
            VALUES (%s, %s, %s, %s, 'ACTIVE', %s, %s, %s)
            """,
            (token_id, req.name_service, encrypted, req.description, now, req.updated_by, now),
        )
    except IntegrityError as exc:
        conn.close()
        raise HTTPException(status_code=409, detail="El nombre del servicio ya existe") from exc

    conn.commit()
    conn.close()
    return {"id": token_id, "status": "ACTIVE"}


def list_app_tokens() -> list[dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, name_service, description, status, created_at, updated_by, updated_at FROM app_tokens"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_app_token(token_id: str, req: Any) -> dict[str, str]:
    conn = get_conn()
    row = conn.execute("SELECT id FROM app_tokens WHERE id = %s", (token_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")

    sets = ["updated_by = %s", "updated_at = %s"]
    params: list[Any] = [req.updated_by, now_iso()]

    if req.description is not None:
        sets.append("description = %s")
        params.append(req.description)
    if req.status is not None:
        if req.status not in {"ACTIVE", "INACTIVE"}:
            conn.close()
            raise HTTPException(status_code=422, detail="status debe ser ACTIVE o INACTIVE")
        sets.append("status = %s")
        params.append(req.status)
    if req.token_value is not None:
        sets.append("encrypted_token = %s")
        params.append(aes_encrypt(req.token_value))

    params.append(token_id)
    conn.execute(f"UPDATE app_tokens SET {', '.join(sets)} WHERE id = %s", params)
    conn.commit()
    conn.close()
    return {"message": "Token de aplicacion actualizado"}


def disable_app_token(token_id: str, updated_by: str) -> dict[str, str]:
    conn = get_conn()
    cur = conn.execute(
        """
        UPDATE app_tokens
        SET status = 'INACTIVE', updated_by = %s, updated_at = %s
        WHERE id = %s
        """,
        (updated_by, now_iso(), token_id),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")
    return {"message": "Token de aplicacion desactivado"}


def list_sessions(user_id: str | None = None) -> list[dict[str, Any]]:
    conn = get_conn()
    if user_id:
        rows = conn.execute(
            """
            SELECT id, user_id, ip_origin, user_agent, created_at, last_activity_at, status
            FROM sessions_user WHERE status = 'ACTIVE' AND user_id = %s
            """,
            (user_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, user_id, ip_origin, user_agent, created_at, last_activity_at, status
            FROM sessions_user WHERE status = 'ACTIVE'
            """
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def force_close_session(session_id: str, req: Any, auth: dict[str, Any]) -> dict[str, str]:
    conn = get_conn()
    row = conn.execute(
        "SELECT token, user_id FROM sessions_user WHERE id = %s",
        (session_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Sesion no encontrada")

    now = now_iso()
    conn.execute(
        """
        UPDATE sessions_user
        SET status = 'CLOSED', record_updated_at = %s, last_activity_at = %s
        WHERE id = %s
        """,
        (now, now, session_id),
    )
    conn.execute(
        "INSERT INTO invalidated_tokens (token, invalidated_at) VALUES (%s, %s) ON CONFLICT (token) DO NOTHING",
        (row["token"], now),
    )
    log_event(conn, row["user_id"], "LOGOUT_OK", "0.0.0.0", "admin", req.reason)
    conn.commit()
    conn.close()

    return {"message": f"Sesion {session_id} cerrada por {auth['claims']['sub']}"}


def get_access_history(
    user_id: str | None = None,
    event_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if user_id:
        filters.append("user_id = %s")
        params.append(user_id)
    if event_type:
        filters.append("event_type = %s")
        params.append(event_type)
    if start_date:
        filters.append("event_at >= %s")
        params.append(start_date)
    if end_date:
        filters.append("event_at <= %s")
        params.append(end_date)

    where_clause = ""
    if filters:
        where_clause = " WHERE " + " AND ".join(filters)

    conn = get_conn()
    rows = conn.execute(
        f"SELECT id, user_id, event_type, ip_origin, user_agent, event_at, request_trace_id FROM access_history{where_clause} ORDER BY event_at DESC",
        params,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
