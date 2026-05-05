-- PostgreSQL Initialization Script for ms-autenticacion
-- This script creates all necessary tables and indexes for the authentication microservice

-- =============================================
-- TABLE: sessions_user
-- Description: Stores user session tokens and metadata
-- =============================================
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
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_user_token ON sessions_user(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_user_id ON sessions_user(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON sessions_user(status);
CREATE INDEX IF NOT EXISTS idx_sessions_user_user_status ON sessions_user(user_id, status);

-- =============================================
-- TABLE: app_tokens
-- Description: Stores encrypted tokens for service-to-service authentication
-- =============================================
CREATE TABLE IF NOT EXISTS app_tokens (
    id TEXT PRIMARY KEY,
    name_service TEXT NOT NULL UNIQUE,
    encrypted_token TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_app_tokens_name_service ON app_tokens(name_service);
CREATE INDEX IF NOT EXISTS idx_app_tokens_status ON app_tokens(status);

-- =============================================
-- TABLE: access_history
-- Description: Logs all login and access attempts for auditing
-- =============================================
CREATE TABLE IF NOT EXISTS access_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    ip_origin TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    event_at TEXT NOT NULL,
    request_trace_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_access_history_user_id ON access_history(user_id);
CREATE INDEX IF NOT EXISTS idx_access_history_event_type ON access_history(event_type);
CREATE INDEX IF NOT EXISTS idx_access_history_event_at ON access_history(event_at);
CREATE INDEX IF NOT EXISTS idx_access_history_request_trace_id ON access_history(request_trace_id);
CREATE INDEX IF NOT EXISTS idx_access_history_user_event_at ON access_history(user_id, event_type, event_at);

-- =============================================
-- TABLE: login_attempt_control
-- Description: Tracks failed login attempts to prevent brute force attacks
-- =============================================
CREATE TABLE IF NOT EXISTS login_attempt_control (
    user_id TEXT PRIMARY KEY,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    is_blocked INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

-- =============================================
-- TABLE: invalidated_tokens
-- Description: Stores tokens that have been invalidated (logout, password reset, etc.)
-- =============================================
CREATE TABLE IF NOT EXISTS invalidated_tokens (
    token TEXT PRIMARY KEY,
    invalidated_at TEXT NOT NULL
);

-- =============================================
-- Permission Management
-- =============================================
-- Grant all privileges to the application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO auth;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO auth;
GRANT USAGE ON SCHEMA public TO auth;

-- =============================================
-- Initial Setup Success Message
-- =============================================
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully at %', NOW();
END $$;
