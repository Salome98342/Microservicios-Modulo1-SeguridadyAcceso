# 🗄️ Creación de Base de Datos - Microservicio de Usuarios

## Información General

**Sistema de Base de Datos:** PostgreSQL 12+  
**Nombre de la Base de Datos:** `db_usuarios`  
**Schema:** `public`  
**Encoding:** UTF-8  

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de PostgreSQL](#instalación-de-postgresql)
3. [Creación de Base de Datos](#creación-de-base-de-datos)
4. [Estructura de Tablas](#estructura-de-tablas)
5. [Datos Predeterminados](#datos-predeterminados)
6. [Conexión desde la Aplicación](#conexión-desde-la-aplicación)
7. [Backup y Restauración](#backup-y-restauración)

---

## ✅ Requisitos Previos

- PostgreSQL 12 o superior instalado
- Usuario `postgres` con contraseña configurada
- Herramienta `psql` disponible en la terminal
- Permisos de administrador en el sistema

---

## 🔧 Instalación de PostgreSQL

### En Windows

1. Descargar desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Configurar puerto (por defecto 5432)
4. Establecer contraseña para usuario `postgres`
5. Completar instalación

### En Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### En macOS

```bash
brew install postgresql
brew services start postgresql
```

---

## 📦 Creación de Base de Datos

### Opción 1: Usando psql (Línea de Comandos)

```bash
# Conectarse como postgres
psql -U postgres -h localhost

# En la consola psql:
CREATE DATABASE db_usuarios
    OWNER postgres
    ENCODING 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE template0;

# Conectarse a la nueva base de datos
\c db_usuarios

# Ejecutar el script SQL (ver siguiente sección)
```

### Opción 2: Usando Variables de Entorno

```bash
export PGUSER=postgres
export PGPASSWORD=tu_contraseña
export PGHOST=localhost
export PGPORT=5432

psql -c "CREATE DATABASE db_usuarios OWNER postgres ENCODING 'UTF8';"
```

### Opción 3: Usando archivo .sql

Crear archivo `init_db.sql` con el contenido de la sección siguiente y ejecutar:

```bash
psql -U postgres -h localhost -f init_db.sql
```

---

## 🏗️ Estructura de Tablas

### Script Completo de Creación

```sql
-- Conectarse a la base de datos
\c db_usuarios;

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

CREATE INDEX idx_tipos_documento_codigo ON usr_tipos_documento(codigo);
CREATE INDEX idx_tipos_documento_activo ON usr_tipos_documento(activo);

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

CREATE INDEX idx_usuarios_username ON usr_usuarios(username);
CREATE INDEX idx_usuarios_email ON usr_usuarios(email);
CREATE INDEX idx_usuarios_estado ON usr_usuarios(estado);
CREATE INDEX idx_usuarios_rol_id ON usr_usuarios(rol_id);

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

CREATE INDEX idx_perfiles_usuario_id ON usr_perfiles(usuario_id);
CREATE INDEX idx_perfiles_tipo_documento_id ON usr_perfiles(tipo_documento_id);
CREATE INDEX idx_perfiles_numero_documento ON usr_perfiles(numero_documento);
CREATE INDEX idx_perfiles_ciudad ON usr_perfiles(ciudad);
CREATE INDEX idx_perfiles_primer_nombre ON usr_perfiles(primer_nombre);
CREATE INDEX idx_perfiles_primer_apellido ON usr_perfiles(primer_apellido);

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

CREATE INDEX idx_preferencias_usuario_id ON usr_preferencias_notificacion(usuario_id);

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

CREATE INDEX idx_historial_usuario_id ON usr_historial_estados(usuario_id);
CREATE INDEX idx_historial_created_at ON usr_historial_estados(created_at);

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
CREATE TRIGGER trigger_actualizar_timestamp_tipos_documento
BEFORE UPDATE ON usr_tipos_documento
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_usuarios
CREATE TRIGGER trigger_actualizar_timestamp_usuarios
BEFORE UPDATE ON usr_usuarios
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_perfiles
CREATE TRIGGER trigger_actualizar_timestamp_perfiles
BEFORE UPDATE ON usr_perfiles
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- Trigger para usr_preferencias_notificacion
CREATE TRIGGER trigger_actualizar_timestamp_preferencias
BEFORE UPDATE ON usr_preferencias_notificacion
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();
```

### Ejecutar el Script

```bash
# Opción 1: Desde la terminal
psql -U postgres -h localhost -d db_usuarios < creacion_tablas.sql

# Opción 2: Desde psql interactivo
psql -U postgres -h localhost
\c db_usuarios
\i creacion_tablas.sql
```

---

## 🌱 Datos Predeterminados

### Insertar Tipos de Documento

```sql
INSERT INTO usr_tipos_documento (codigo, nombre, descripcion, activo)
VALUES
    ('CC', 'Cédula de Ciudadanía', 'Documento de identidad para ciudadanos colombianos', true),
    ('PA', 'Pasaporte', 'Documento de viaje internacional', true),
    ('CE', 'Cédula de Extranjería', 'Documento de identidad para extranjeros residentes', true),
    ('TI', 'Tarjeta de Identidad', 'Documento de identidad complementario', true),
    ('RC', 'Registro Civil', 'Acta de nacimiento', false)
ON CONFLICT (codigo) DO NOTHING;
```

### Verificar Datos Insertados

```sql
SELECT * FROM usr_tipos_documento WHERE activo = true;
```

---

## 🔌 Conexión desde la Aplicación

### Variables de Entorno (.env)

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_usuarios
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui

# Application Configuration
APP_TITULO=ms-usuarios [USR]
APP_DESCRIPCION=Microservicio de gestion de usuarios
APP_VERSION=1.0.0
APP_PREFIX=/api/v1

# Crypto and Authentication
AES_SECRET_KEY=tu_clave_aes_256_aqui
BCRYPT_ROUNDS=12
USR_APP_TOKEN=token_interno_usuarios

# External Services
AUTH_SERVICE_URL=http://ms-autenticacion:8001
ROL_SERVICE_URL=http://ms-roles:8002
NOT_SERVICE_URL=http://ms-notificaciones:8003
AUD_SERVICE_URL=http://ms-auditoria:8004

# Timeouts (en segundos)
TIMEOUT_AUTH=3
TIMEOUT_ROL=3
TIMEOUT_NOT=1
TIMEOUT_AUD=0.5

# Debug Mode
DEBUG_MODE=false
```

### Configuración en Python

```python
from config import DATABASE_URL
import psycopg2

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn
```

---

## 🧪 Verificación de la Base de Datos

### Listar Tablas Creadas

```sql
-- Conectarse a la base de datos
\c db_usuarios

-- Listar todas las tablas
\dt

-- Ver detalle de estructura
\d usr_usuarios
\d usr_perfiles
\d usr_preferencias_notificacion
\d usr_historial_estados
\d usr_tipos_documento
```

### Verificar Índices

```sql
-- Ver todos los índices
SELECT * FROM pg_indexes WHERE schemaname = 'public';
```

### Verificar Restricciones

```sql
-- Ver restricciones de check
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name IN ('usr_usuarios', 'usr_perfiles', 'usr_preferencias_notificacion', 'usr_historial_estados');
```

---

## 📊 Consultas Útiles

### Estadísticas de Tablas

```sql
-- Contar usuarios por estado
SELECT estado, COUNT(*) as cantidad
FROM usr_usuarios
GROUP BY estado;

-- Usuarios con perfil completo
SELECT u.id, u.username, p.numero_documento
FROM usr_usuarios u
LEFT JOIN usr_perfiles p ON u.id = p.usuario_id
WHERE p.id IS NOT NULL;

-- Últimos usuarios creados
SELECT id, username, email, created_at
FROM usr_usuarios
ORDER BY created_at DESC
LIMIT 10;

-- Historial de cambios de un usuario
SELECT *
FROM usr_historial_estados
WHERE usuario_id = 1
ORDER BY created_at DESC;
```

---

## 💾 Backup y Restauración

### Realizar Backup

```bash
# Backup completo de la base de datos
pg_dump -U postgres -h localhost db_usuarios > backup_usuarios_$(date +%Y%m%d_%H%M%S).sql

# Backup solo de esquema (sin datos)
pg_dump -U postgres -h localhost -s db_usuarios > backup_usuarios_schema.sql

# Backup solo de datos
pg_dump -U postgres -h localhost -a db_usuarios > backup_usuarios_data.sql

# Backup en formato comprimido
pg_dump -U postgres -h localhost -F c db_usuarios > backup_usuarios.dump
```

### Restaurar Backup

```bash
# Restaurar desde archivo SQL
psql -U postgres -h localhost db_usuarios < backup_usuarios.sql

# Restaurar desde archivo dump comprimido
pg_restore -U postgres -h localhost -d db_usuarios backup_usuarios.dump

# Restaurar con opciones adicionales
pg_restore -U postgres -h localhost -d db_usuarios -v --no-acl --no-owner backup_usuarios.dump
```

---

## 🧹 Mantenimiento de Base de Datos

### Optimización de Tablas

```sql
-- Analizar tablas (recomendado después de muchas operaciones)
ANALYZE;

-- Reindex para optimizar búsquedas
REINDEX DATABASE db_usuarios;

-- Vacuum para limpiar espacio
VACUUM ANALYZE;
```

### Monitoreo

```sql
-- Ver tamaño de base de datos
SELECT pg_size_pretty(pg_database_size('db_usuarios')) as tamaño;

-- Ver tamaño de tablas
SELECT 
    relname as tabla,
    pg_size_pretty(pg_total_relation_size(relid)) as tamaño
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Ver tamaño de índices
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as tamaño
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 🔐 Seguridad

### Crear Usuario de Base de Datos Específico

```sql
-- Conectarse como superusuario
sudo -u postgres psql

-- Crear usuario específico
CREATE USER usr_ms_usuarios WITH PASSWORD 'contraseña_segura';

-- Otorgar permisos
GRANT CONNECT ON DATABASE db_usuarios TO usr_ms_usuarios;
GRANT USAGE ON SCHEMA public TO usr_ms_usuarios;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO usr_ms_usuarios;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO usr_ms_usuarios;

-- Hacer permanentes para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO usr_ms_usuarios;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO usr_ms_usuarios;
```

### Configurar pg_hba.conf para Autenticación

```bash
# Editar archivo de configuración (Linux)
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Agregar o modificar (usar md5 o scram-sha-256):
host    db_usuarios    usr_ms_usuarios    127.0.0.1/32    scram-sha-256
host    db_usuarios    usr_ms_usuarios    ::1/128         scram-sha-256
```

---

## ⚠️ Troubleshooting

### Conexión Rechazada

```bash
# Verificar que PostgreSQL está ejecutándose
sudo systemctl status postgresql  # Linux
brew services list                 # macOS
Get-Service postgresql             # Windows (PowerShell)

# Verificar puerto
netstat -an | grep 5432  # Linux/macOS
netstat -ano | findstr 5432  # Windows

# Reiniciar servicio
sudo systemctl restart postgresql  # Linux
brew services restart postgresql   # macOS
```

### Problema: "Base de datos no existe"

```bash
# Verificar bases de datos existentes
psql -U postgres -h localhost -l

# Si falta db_usuarios, crearla manualmente
psql -U postgres -h localhost -c "CREATE DATABASE db_usuarios;"
```

### Problema: "Permiso denegado"

```sql
-- Verificar permisos del usuario
SELECT grantee, privilege_type 
FROM information_schema.role_table_grants 
WHERE table_name = 'usr_usuarios';

-- Restaurar permisos si es necesario
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

---

## 📚 Recursos Adicionales

- [Documentación PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación Python psycopg2](https://www.psycopg.org/)
- [Guía de Triggers PostgreSQL](https://www.postgresql.org/docs/current/plpgsql-trigger.html)
- [Best Practices para Indexes](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## ✨ Notas Importantes

1. **Backup Regular:** Realizar backups regularmente (mínimo semanal)
2. **Monitoring:** Usar herramientas como pgAdmin para monitoreo
3. **Versionado:** Mantener scripts de esquema bajo control de versiones
4. **Testing:** Probar restauración de backups periódicamente
5. **Logs:** Revisar logs de PostgreSQL para detectar problemas
6. **Índices:** Revisar periódicamente índices no utilizados
7. **Actualización:** Mantener PostgreSQL actualizado a versión estable

