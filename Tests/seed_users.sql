-- Script SQL para insertar usuarios de prueba
-- Ejecutar con: psql -U postgres -d db_usuarios -h 127.0.0.1 -p 5434 -f seed_users.sql

-- Crear tabla de usuarios si no existe
CREATE TABLE IF NOT EXISTS usr_usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(50) DEFAULT 'activo',
    rol_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario admin
INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
VALUES ('admin', 'admin@universidad.edu.co', 'f240652348e4161d2282d0b9b8911249fb0c0e98470b990f1a0949c4c66db6b4', 'activo', 1)
ON CONFLICT (username) DO NOTHING;

-- Insertar usuario de prueba
INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
VALUES ('estudiante', 'estudiante@universidad.edu.co', 'bd9d2f1c23f7f4c8e37d6e8e4e5d4c7a1b9d2e5f7c8e9f0d1a2b3c4e5f6a7b8', 'activo', 2)
ON CONFLICT (username) DO NOTHING;

-- Verificar datos
SELECT id, username, email, rol_id FROM usr_usuarios;
