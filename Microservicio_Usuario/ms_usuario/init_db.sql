-- ═══════════════════════════════════════════════════════════════════════════
-- TABLA: usr_tipos_documento
-- Propósito: Catálogo maestro de tipos de documentos válidos
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usr_tipos_documento (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tipos_documento_codigo ON usr_tipos_documento(codigo);
CREATE INDEX IF NOT EXISTS idx_tipos_documento_activo ON usr_tipos_documento(activo);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLA: usr_usuarios
-- Propósito: Almacena información de usuarios del sistema
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usr_usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo' NOT NULL,
    rol_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usr_usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usr_usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usr_usuarios(estado);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol_id ON usr_usuarios(rol_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLA: usr_perfiles
-- Propósito: Información extendida de perfil de usuario
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usr_perfiles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usr_usuarios(id) ON DELETE CASCADE,
    tipo_documento_id INTEGER NOT NULL REFERENCES usr_tipos_documento(id),
    numero_documento VARCHAR(50) UNIQUE NOT NULL,
    primer_nombre VARCHAR(100) NOT NULL,
    segundo_nombre VARCHAR(100),
    primer_apellido VARCHAR(100) NOT NULL,
    segundo_apellido VARCHAR(100),
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) NOT NULL,
    direccion_residencia VARCHAR(255) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    telefono_fijo VARCHAR(20),
    telefono_movil VARCHAR(20) NOT NULL,
    contacto_emergencia_nombre VARCHAR(150) NOT NULL,
    contacto_emergencia_telefono VARCHAR(20) NOT NULL,
    biografia TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_perfiles_usuario_id ON usr_perfiles(usuario_id);
CREATE INDEX IF NOT EXISTS idx_perfiles_tipo_documento_id ON usr_perfiles(tipo_documento_id);
CREATE INDEX IF NOT EXISTS idx_perfiles_numero_documento ON usr_perfiles(numero_documento);
CREATE INDEX IF NOT EXISTS idx_perfiles_ciudad ON usr_perfiles(ciudad);
CREATE INDEX IF NOT EXISTS idx_perfiles_primer_nombre ON usr_perfiles(primer_nombre);
CREATE INDEX IF NOT EXISTS idx_perfiles_primer_apellido ON usr_perfiles(primer_apellido);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLA: usr_preferencias_notificacion
-- Propósito: Preferencias de notificación para cada usuario
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usr_preferencias_notificacion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usr_usuarios(id) ON DELETE CASCADE,
    notif_email BOOLEAN DEFAULT true NOT NULL,
    notif_sms BOOLEAN DEFAULT true NOT NULL,
    notif_push BOOLEAN DEFAULT true NOT NULL,
    canal_preferido VARCHAR(20) DEFAULT 'email',
    horario_no_molestar_inicio TIME,
    horario_no_molestar_fin TIME,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_preferencias_usuario_id ON usr_preferencias_notificacion(usuario_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLA: usr_historial_estados
-- Propósito: Registra los cambios de estado de los usuarios
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usr_historial_estados (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usr_usuarios(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20) NOT NULL,
    motivo TEXT NOT NULL,
    usuario_modificador_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_historial_usuario_id ON usr_historial_estados(usuario_id);
CREATE INDEX IF NOT EXISTS idx_historial_created_at ON usr_historial_estados(created_at);

-- ═══════════════════════════════════════════════════════════════════════════
-- Restricciones de CHECK para garantizar integridad de datos
-- ═══════════════════════════════════════════════════════════════════════════

-- Estados válidos de usuario
ALTER TABLE usr_usuarios
ADD CONSTRAINT chk_usuario_estado 
CHECK (estado IN ('activo', 'inactivo', 'suspendido', 'eliminado'));

-- Géneros válidos
ALTER TABLE usr_perfiles
ADD CONSTRAINT chk_perfil_genero 
CHECK (genero IN ('masculino', 'femenino', 'otro', 'prefiero_no_decir'));

-- Estados válidos en historial
ALTER TABLE usr_historial_estados
ADD CONSTRAINT chk_historial_estado 
CHECK (estado_nuevo IN ('activo', 'inactivo', 'suspendido', 'eliminado'));

-- Canales de notificación válidos
ALTER TABLE usr_preferencias_notificacion
ADD CONSTRAINT chk_pref_canal 
CHECK (canal_preferido IN ('email', 'sms', 'push'));

-- ═══════════════════════════════════════════════════════════════════════════
-- Trigger para actualizar updated_at automáticamente
-- ═══════════════════════════════════════════════════════════════════════════

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para usr_tipos_documento
DROP TRIGGER IF EXISTS trigger_actualizar_timestamp_tipos_documento ON usr_tipos_documento;
CREATE TRIGGER trigger_actualizar_timestamp_tipos_documento
BEFORE UPDATE ON usr_tipos_documento
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_usuarios
DROP TRIGGER IF EXISTS trigger_actualizar_timestamp_usuarios ON usr_usuarios;
CREATE TRIGGER trigger_actualizar_timestamp_usuarios
BEFORE UPDATE ON usr_usuarios
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_perfiles
DROP TRIGGER IF EXISTS trigger_actualizar_timestamp_perfiles ON usr_perfiles;
CREATE TRIGGER trigger_actualizar_timestamp_perfiles
BEFORE UPDATE ON usr_perfiles
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_preferencias_notificacion
DROP TRIGGER IF EXISTS trigger_actualizar_timestamp_preferencias ON usr_preferencias_notificacion;
CREATE TRIGGER trigger_actualizar_timestamp_preferencias
BEFORE UPDATE ON usr_preferencias_notificacion
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();
