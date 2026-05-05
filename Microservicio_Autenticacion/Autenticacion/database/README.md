# Guía de Despliegue de Base de Datos - MS-Autenticación

Este documento proporciona instrucciones para crear y desplegar la base de datos PostgreSQL del microservicio de autenticación en Docker.

## 📋 Requisitos Previos

- Docker instalado y ejecutándose
- Docker Compose instalado (versión 1.29+)
- Acceso a terminal/PowerShell

## 📁 Estructura de Archivos

```
database/
├── schema.postgres.sql    # Schema original (referencia)
├── init.sql              # Script de inicialización mejorado para Docker
└── README.md             # Instrucciones (este archivo)

scripts/
├── deploy-db.sh          # Script de despliegue para Linux/macOS
├── deploy-db.ps1         # Script de despliegue para Windows/PowerShell
└── README.md             # Documentación de scripts

docker-compose.yml       # Configuración actualizada para ejecutar init.sql
```

## 🚀 Despliegue Rápido

### Opción 1: Windows (PowerShell)

```powershell
# Ir al directorio del proyecto
cd "ruta/a/tu/proyecto/Autenticacion"

# Ejecutar el script de despliegue
.\scripts\deploy-db.ps1

# Para limpiar volúmenes antiguos antes de desplegar:
.\scripts\deploy-db.ps1 -Clean
```

### Opción 2: Linux / macOS

```bash
# Ir al directorio del proyecto
cd "ruta/a/tu/proyecto/Autenticacion"

# Hacer el script ejecutable
chmod +x scripts/deploy-db.sh

# Ejecutar el script de despliegue
./scripts/deploy-db.sh

# Para limpiar volúmenes antiguos:
./scripts/deploy-db.sh clean
```

### Opción 3: Docker Compose Directamente

```bash
# Detener contenedores previos
docker-compose down

# Iniciar servicios
docker-compose up -d

# Verificar que PostgreSQL está listo
docker-compose logs postgres
```

## 🗄️ Información de Conexión

Una vez desplegada la base de datos, puedes conectarte usando:

| Parámetro | Valor |
|-----------|-------|
| **Host** | `postgres` (dentro de Docker) |
| **Host** | `localhost` (desde tu máquina) |
| **Puerto** | `5432` |
| **Usuario** | `auth` |
| **Contraseña** | `auth` |
| **Base de datos** | `auth_db` |

**Connection String:**
```
postgresql://auth:auth@postgres:5432/auth_db
```

## 📊 Tablas Creadas

El script de inicialización crea automáticamente las siguientes tablas:

### 1. **sessions_user**
Almacena los tokens de sesión de los usuarios.
- `id` - Identificador único
- `user_id` - ID del usuario
- `token` - Token de sesión
- `ip_origin` - IP de origen
- `user_agent` - Información del navegador
- `status` - Estado de la sesión
- Índices para: token, user_id, status

### 2. **app_tokens**
Almacena tokens encriptados para autenticación entre servicios.
- `id` - Identificador único
- `name_service` - Nombre del servicio (único)
- `encrypted_token` - Token encriptado
- `status` - Estado del token
- Índices para: name_service, status

### 3. **access_history**
Registro de auditoría de accesos y eventos de login.
- `id` - Identificador único
- `user_id` - ID del usuario
- `event_type` - Tipo de evento (login, logout, etc.)
- `ip_origin` - IP de origen
- `request_trace_id` - ID de traza de la solicitud
- Índices para búsquedas rápidas

### 4. **login_attempt_control**
Control de intentos de login fallidos para prevenir ataques de fuerza bruta.
- `user_id` - ID del usuario (PK)
- `failed_attempts` - Número de intentos fallidos
- `is_blocked` - Flag de bloqueo

### 5. **invalidated_tokens**
Almacena tokens que han sido invalidados (logout, cambio de contraseña, etc.).
- `token` - Token invalidado (PK)
- `invalidated_at` - Fecha/hora de invalidación

## 🔧 Comandos Útiles

### Ver logs de la base de datos
```bash
docker-compose logs -f postgres
```

### Conectarse a la base de datos
```bash
docker-compose exec postgres psql -U auth -d auth_db
```

### Ver todas las tablas
```bash
docker-compose exec postgres psql -U auth -d auth_db -c "\dt"
```

### Ver la estructura de una tabla
```bash
docker-compose exec postgres psql -U auth -d auth_db -c "\d sessions_user"
```

### Ver índices
```bash
docker-compose exec postgres psql -U auth -d auth_db -c "\di"
```

### Detener servicios
```bash
docker-compose down
```

### Detener y eliminar volúmenes
```bash
docker-compose down -v
```

### Detener y limpiar todo (incluyendo imágenes)
```bash
docker-compose down -v --rmi all
```

## 📱 Usar la Base de Datos en tu Aplicación

En tu aplicación Python, usa la variable de entorno:

```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://auth:auth@localhost:5432/auth_db"
)

engine = create_engine(DATABASE_URL)
```

En el archivo `docker-compose.yml` ya está configurado:
```yaml
DATABASE_URL: postgresql://auth:auth@postgres:5432/auth_db
```

## 🔐 Seguridad

### Para Producción

⚠️ **Cambiar credenciales predeterminadas:**

Modifica el archivo `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: auth_db_prod
  POSTGRES_USER: auth_user_prod
  POSTGRES_PASSWORD: generador_contraseña_segura
```

O usa un archivo `.env`:

```bash
# .env
POSTGRES_DB=auth_db
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=TuContraseñaSegura123!@#
```

Y actualiza el `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB}
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### Volúmenes Persistentes

Los datos se guardan automáticamente en un volumen Docker nombrado `pgdata`. Esto asegura que los datos persistan incluso si los contenedores se detienen o se eliminen.

## 🐛 Solución de Problemas

### PostgreSQL no inicia
```bash
# Ver logs detallados
docker-compose logs postgres

# Limpiar y reintentar
docker-compose down -v
docker-compose up -d
```

### Permisos denegados (Linux/macOS)
```bash
# Hacer el script ejecutable
chmod +x scripts/deploy-db.sh
```

### Puerto 5432 ya está en uso
Cambia el puerto en `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Cambia a otro puerto disponible
```

### Verificar que todo está funcionando
```bash
docker-compose ps
docker-compose logs
```

## 📝 Notas Adicionales

- El script `init.sql` se ejecuta automáticamente cuando el contenedor PostgreSQL se inicia por primera vez
- Los índices se crean automáticamente para optimizar las búsquedas
- Todos los permisos necesarios se asignan al usuario `auth`
- El contenedor tiene un healthcheck que verifica la disponibilidad cada 5 segundos

## 🔄 Actualizar el Schema

Si necesitas agregar nuevas tablas o modificar el schema:

1. Edita `database/init.sql`
2. Ejecuta `docker-compose down -v` para limpiar volúmenes
3. Ejecuta `docker-compose up -d` para recrear la base de datos

## 📧 Soporte

Para problemas o preguntas:
- Revisa los logs: `docker-compose logs postgres`
- Verifica la conectividad: `docker-compose exec postgres pg_isready`
- Consulta la documentación oficial de PostgreSQL
