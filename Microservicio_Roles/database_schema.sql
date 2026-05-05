-- ============================================================================
-- Script de creación de la base de datos para ms-roles
-- Base de datos: db_roles
-- Microservicio: ms-roles (Sistema de Roles y Permisos)
-- Motor: PostgreSQL 13+
-- ============================================================================

-- Crear base de datos si no existe
CREATE DATABASE db_roles
    ENCODING 'UTF8'
    LOCALE 'en_US.UTF-8';

-- Conectarse a la base de datos
\c db_roles

-- ============================================================================
-- TABLA: rol_roles
-- Descripción: Almacena los roles del sistema ERP universitario
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    estado VARCHAR(10) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rol_roles_estado ON rol_roles(estado);
CREATE INDEX IF NOT EXISTS idx_rol_roles_nombre ON rol_roles(nombre);

-- ============================================================================
-- TABLA: rol_permisos
-- Descripción: Catálogo centralizado de permisos del sistema
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_permisos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(60) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(80) NOT NULL,
    microservicio_origen VARCHAR(60) NOT NULL,
    funcionalidad_asociada VARCHAR(150) NOT NULL,
    metodo_operacion VARCHAR(20) NOT NULL CHECK (metodo_operacion IN ('consulta', 'creacion', 'actualizacion', 'eliminacion')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rol_permisos_modulo ON rol_permisos(modulo);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_microservicio ON rol_permisos(microservicio_origen);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_metodo ON rol_permisos(metodo_operacion);

-- ============================================================================
-- TABLA: rol_asignaciones_rol_permiso
-- Descripción: Tabla de asociación N:M entre roles y permisos
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_asignaciones_rol_permiso (
    id SERIAL PRIMARY KEY,
    rol_id INTEGER NOT NULL REFERENCES rol_roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    permiso_id INTEGER NOT NULL REFERENCES rol_permisos(id) ON DELETE CASCADE ON UPDATE CASCADE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    asignado_por_usuario_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (rol_id, permiso_id)
);

CREATE INDEX IF NOT EXISTS idx_arp_rol_id ON rol_asignaciones_rol_permiso(rol_id);
CREATE INDEX IF NOT EXISTS idx_arp_permiso_id ON rol_asignaciones_rol_permiso(permiso_id);
CREATE INDEX IF NOT EXISTS idx_arp_asignado_por ON rol_asignaciones_rol_permiso(asignado_por_usuario_id);

-- ============================================================================
-- TABLA: rol_asignaciones_usuario_rol
-- Descripción: Tabla de asociación N:M entre usuarios y roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_asignaciones_usuario_rol (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL REFERENCES rol_roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    estado VARCHAR(10) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_asignacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    asignado_por_usuario_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raur_usuario_id ON rol_asignaciones_usuario_rol(usuario_id);
CREATE INDEX IF NOT EXISTS idx_raur_rol_id ON rol_asignaciones_usuario_rol(rol_id);
CREATE INDEX IF NOT EXISTS idx_raur_estado ON rol_asignaciones_usuario_rol(estado);
CREATE INDEX IF NOT EXISTS idx_raur_asignado_por ON rol_asignaciones_usuario_rol(asignado_por_usuario_id);
CREATE INDEX IF NOT EXISTS idx_raur_usuario_estado ON rol_asignaciones_usuario_rol(usuario_id, estado);

-- ============================================================================
-- TABLA: rol_roles_contradictorios
-- Descripción: Define pares de roles mutuamente excluyentes
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_roles_contradictorios (
    id SERIAL PRIMARY KEY,
    rol_a_id INTEGER NOT NULL REFERENCES rol_roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    rol_b_id INTEGER NOT NULL REFERENCES rol_roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    motivo TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (rol_a_id, rol_b_id),
    CHECK (rol_a_id <> rol_b_id)
);

CREATE INDEX IF NOT EXISTS idx_rrc_rol_a_id ON rol_roles_contradictorios(rol_a_id);
CREATE INDEX IF NOT EXISTS idx_rrc_rol_b_id ON rol_roles_contradictorios(rol_b_id);
CREATE INDEX IF NOT EXISTS idx_rrc_bidireccional ON rol_roles_contradictorios(rol_b_id, rol_a_id);

-- ============================================================================
-- TABLA: rol_tokens_aplicacion
-- Descripción: Tokens de aplicación cifrados AES-256 para inter-servicio
-- ============================================================================
CREATE TABLE IF NOT EXISTS rol_tokens_aplicacion (
    id SERIAL PRIMARY KEY,
    nombre_servicio VARCHAR(60) NOT NULL UNIQUE,
    token_cifrado TEXT NOT NULL,
    descripcion TEXT,
    estado VARCHAR(10) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    actualizado_por_usuario_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rta_estado ON rol_tokens_aplicacion(estado);

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista para consultar permisos activos asignados a un rol
CREATE OR REPLACE VIEW vw_rol_permisos_activos AS
SELECT 
    r.id AS rol_id,
    r.nombre AS rol_nombre,
    r.estado AS rol_estado,
    p.id AS permiso_id,
    p.codigo AS permiso_codigo,
    p.nombre AS permiso_nombre,
    p.modulo,
    p.microservicio_origen,
    p.funcionalidad_asociada,
    p.metodo_operacion,
    arp.fecha_asignacion,
    arp.asignado_por_usuario_id
FROM rol_roles r
INNER JOIN rol_asignaciones_rol_permiso arp ON r.id = arp.rol_id
INNER JOIN rol_permisos p ON arp.permiso_id = p.id
WHERE r.estado = 'activo'
ORDER BY r.nombre, p.codigo;

-- Vista para consultar roles activos asignados a un usuario
CREATE OR REPLACE VIEW vw_usuario_roles_activos AS
SELECT 
    aur.usuario_id,
    r.id AS rol_id,
    r.nombre AS rol_nombre,
    r.descripcion,
    aur.fecha_asignacion,
    aur.asignado_por_usuario_id
FROM rol_asignaciones_usuario_rol aur
INNER JOIN rol_roles r ON aur.rol_id = r.id
WHERE aur.estado = 'activo' AND r.estado = 'activo'
ORDER BY aur.usuario_id, r.nombre;

-- ============================================================================
-- FIN DEL SCRIPT DE CREACIÓN
-- ============================================================================
