# Microservicios-Modulo1-SeguridadyAcceso

# Microservicios Conectados - Autenticación y Usuarios

Este proyecto contiene dos microservicios comunicados entre sí:
- **ms-autenticacion**: Servicio de autenticación y tokens JWT
- **ms-usuarios**: Servicio de gestión de usuarios

## 📋 Requisitos

- Docker y Docker Compose instalados
- Puerto 8000 disponible (Usuarios)
- Puerto 8002 disponible (Autenticación - external)

## 🚀 Inicio Rápido

### 1. **Ejecutar todos los servicios**

Desde la raíz del proyecto (donde está este README):

```bash
docker-compose up -d
```

Esto levantará:
- Base de datos PostgreSQL para Autenticación (ms-autenticacion-postgres)
- Microservicio de Autenticación (ms-autenticacion) en puerto 8002 → interno 8000
- Base de datos PostgreSQL para Usuarios (ms-usuarios-postgres)
- Microservicio de Usuarios (ms-usuarios) en puerto 8000

### 2. **Verificar que todo está corriendo**

```bash
docker-compose ps
```

Deberías ver:
```
NAME                           STATUS
ms-autenticacion-postgres      Up (healthy)
ms-autenticacion               Up
ms-usuarios-postgres           Up (healthy)
ms-usuarios-app                Up
```

### 3. **Acceso a los servicios**

- **Autenticación**: http://localhost:8002
- **Usuarios**: http://localhost:8000

## 🔌 Comunicación entre servicios

Los servicios se comunican a través de la red `microservicios-network`:

```
ms-usuarios → http://ms-autenticacion:8000 (red interna)
             └─> Valida tokens JWT
```

### Rutas de validación

- **POST** `http://localhost:8002/api/v1/auth/login` - Obtener token
- **POST** `http://localhost:8000/api/v1/users` - Crear usuario (requiere token válido)
- **GET** `http://localhost:8000/api/v1/users` - Listar usuarios (requiere token válido)

## 📝 Ejemplo de uso

### 1. Autenticarse

```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Respuesta:
```json
```

### 2. Crear un usuario

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <TOKEN_FROM_STEP_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password_encrypted": "...encrypted_password..."
  }'
```

## 🛑 Detener los servicios

```bash
docker-compose down
```

Para eliminar también los volúmenes de datos:

```bash
docker-compose down -v
```

## 🔧 Configuración

Las variables de entorno se definen en:
- `.env` (archivo raíz - compartido)
- `docker-compose.yml` (sobrescribe si es necesario)

### Cambios importantes en la configuración:

1. **URL de Autenticación en Usuarios** (`ms_usuario/config.py`):
   ```python
   AUTH_SERVICE_URL = "http://ms-autenticacion:8000"
   ```

2. **URL de Usuarios en Autenticación** (`docker-compose.yml`):
   ```yaml
   USERS_SERVICE_URL: "http://ms-usuarios:8000"
   ```

## 📊 Estructura de la red

```
┌─────────────────────────────────────────────────────────────┐
│          Docker Network: microservicios-network             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │  ms-autenticacion    │◄─────┤   ms-usuarios-app    │   │
│  │  (puerto 8000)       │      │   (puerto 8000)      │   │
│  └──────────────────────┘      └──────────────────────┘   │
│         │                               │                 │
│         └──────────┬────────────────────┘                 │
│                    ▼                                       │
│  ┌──────────────────────────────────────────┐            │
│  │      postgres-auth    postgres-usuarios   │            │
│  │      (port 5432)      (port 5432)        │            │
│  └──────────────────────────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                              │
         └──────────┬───────────────────┘
                    ▼
            Host Machine
         (localhost:8002, localhost:8000)
```

## 🐛 Solución de problemas

### Los servicios no se comunican

1. Verifica que estén en la misma red:
   ```bash
   docker network ls
   docker network inspect microservicios_microservicios-network
   ```

2. Verifica los logs:
   ```bash
   docker-compose logs ms-usuarios
   docker-compose logs ms-autenticacion
   ```

### Error de conexión a base de datos

Asegúrate de que los volúmenes y healthchecks estén pasando:

```bash
docker-compose logs postgres-auth
docker-compose logs postgres-usuarios
```

### Token inválido

Asegúrate de que estés usando el token correcto de `/api/v1/auth/login` en la cabecera `Authorization: Bearer <token>`

## 📚 Documentación

- **General (consolidada):** [Documentacion General](Documentacion_General/index.md)
- [Especificación API - Autenticación](./Microservicio_Autenticacion/Autenticacion/docs/)
- [Especificación API - Usuarios](./Microservicio_Usuario/documentacion/)
- [Contrato OpenAPI](./Microservicio_Autenticacion/Autenticacion/contracts/)

## 👨‍💻 Desarrollo

Para hacer cambios y reconstruir los servicios:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

O si solo necesitas reconstruir un servicio específico:

```bash
docker-compose up -d --build ms-usuarios
docker-compose up -d --build ms-autenticacion
```
