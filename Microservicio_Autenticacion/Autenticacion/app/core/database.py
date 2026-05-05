from typing import Any

from psycopg import connect
from psycopg.rows import dict_row


from .config import DATABASE_URL


def get_conn() -> Any:
    conn = connect(DATABASE_URL, row_factory=dict_row)
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions_user (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL,
            ip_origin TEXT NOT NULL,
            user_agent TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_activity_at TEXT NOT NULL,
            status TEXT NOT NULL,
            record_created_at TEXT NOT NULL,
            record_updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_tokens (
            id TEXT PRIMARY KEY,
            name_service TEXT NOT NULL UNIQUE,
            encrypted_token TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_by TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS access_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            ip_origin TEXT NOT NULL,
            user_agent TEXT NOT NULL,
            event_at TEXT NOT NULL,
            request_trace_id TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempt_control (
            user_id TEXT PRIMARY KEY,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            is_blocked INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS invalidated_tokens (
            token TEXT PRIMARY KEY,
            invalidated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
