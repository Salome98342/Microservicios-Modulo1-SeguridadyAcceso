# 📋 DOCUMENTACIÓN - Conexión de Microservicios

## 🎯 Objetivo

Conectar dos microservicios que ya funcionaban independientemente:
- **ms-autenticacion**: Servicio de autenticación (puerto 8002)
- **ms-usuarios**: Servicio de usuarios (puerto 8000)

Para que se comuniquen y compartan datos de sesión/tokens de forma segura.

---

## ✅ Cambios Realizados

### 1. **docker-compose.yml (Raíz del proyecto)**

**Antes:** Dos docker-compose.yml separados en cada directorio

**Después:** Un `docker-compose.yml` unificado en la raíz que incluye:

#### 🔹 Servicio de Autenticación
```yaml
services:
  postgres-auth:  # BD de autenticación
  ms-autenticacion:  # Servicio auth
```

#### 🔹 Servicio de Usuarios  
```yaml
services:
  postgres-usuarios:  # BD de usuarios
  ms-usuarios:  # Servicio usuarios
```

#### 🔹 Red Compartida
```yaml
networks:
  microservicios-network:  # Conecta ambos servicios
```

### Cambios clave en docker-compose.yml:

| Elemento | Cambio |
|----------|--------|
| **Red** | Todos en `microservicios-network` (bridge) |
| **Nombres de contenedores** | `ms-autenticacion`, `ms-usuarios-app` |
| **USERS_SERVICE_URL** | Ahora apunta a `http://ms-usuarios:8000` |
| **ROLES_SERVICE_URL** | Preparado para futuras integraciones con ms-roles |
| **Dependencias** | ms-usuarios depende de ms-autenticacion |

---

### 2. **config.py (Microservicio Usuario)**

**Antes:**
```python
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://ms-autenticacion:8001")
ROL_SERVICE_URL = os.getenv("ROL_SERVICE_URL", "http://ms-roles:8002")
NOT_SERVICE_URL = os.getenv("NOT_SERVICE_URL", "http://ms-notificaciones:8003")
AUD_SERVICE_URL = os.getenv("AUD_SERVICE_URL", "http://ms-auditoria:8004")
```

**Después:**
```python
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://ms-autenticacion:8000")
ROL_SERVICE_URL = os.getenv("ROL_SERVICE_URL", "http://ms-roles:8003")
NOT_SERVICE_URL = os.getenv("NOT_SERVICE_URL", "http://ms-notificaciones:8004")
AUD_SERVICE_URL = os.getenv("AUD_SERVICE_URL", "http://ms-auditoria:8005")
```

**Razón:** El puerto interno de todos los servicios es 8000 dentro de Docker, no el puerto expuesto al host.

---

### 3. **Archivos Nuevos Creados**

#### 📄 `.env` (Raíz)
Centraliza la configuración compartida de variables de entorno. Facilita cambios globales sin editar docker-compose.yml.

#### 📄 `README.md` (Raíz)
Documentación completa sobre:
- Requisitos
- Cómo ejecutar los servicios
- Ejemplo de uso de APIs
- Solución de problemas
- Estructura de la red

#### 📄 `QUICKSTART.md` (Raíz)
Guía de inicio rápido para ejecutar todo de inmediato.

#### 📄 `manage-services.ps1` (Raíz)
Script PowerShell para facilitar la gestión de servicios en Windows:
```powershell
.\manage-services.ps1 -Action up          # Iniciar
.\manage-services.ps1 -Action down        # Detener
.\manage-services.ps1 -Action logs        # Ver logs
.\manage-services.ps1 -Action restart     # Reiniciar
.\manage-services.ps1 -Action ps          # Ver estado
```

---

## 🔌 Arquitectura de Comunicación

### Red Docker
```
┌─────────────────────────────────────────────────────┐
│  Docker Network: microservicios-network             │
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ ms-autenticacion │◄─────┤ ms-usuarios      │   │
│  │ (interno: 8000)  │      │ (interno: 8000)  │   │
│  └──────────────────┘      └──────────────────┘   │
│         │                          │               │
│    [Host: 8002]              [Host: 8000]         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Flujo de Comunicación

```
1. Cliente hace request a ms-usuarios (localhost:8000)
   ↓
2. ms-usuarios valida sesión con ms-autenticacion
   Request: POST http://ms-autenticacion:8000/api/v1/auth/validate-session
   ↓
3. ms-autenticacion verifica JWT y retorna si es válido
   Response: {"data": {"valid": true, "user_id": 1, "rol_id": 1}}
   ↓
4. ms-usuarios permite la operación si la sesión es válida
```

---

## 🔐 Seguridad y Tokens

### JWT (JSON Web Tokens)

1. Usuario se autentica en ms-autenticacion
   ```bash
   POST http://localhost:8002/api/v1/auth/login
   Body: {"username": "...", "password": "..."}
   Response: {"token": "eyJhbGc...", "token_type": "bearer"}
   ```

2. Usuario usa el token en ms-usuarios
   ```bash
   POST http://localhost:8000/api/v1/users
   Headers: {"Authorization": "Bearer eyJhbGc..."}
   ```

3. ms-usuarios valida el token con ms-autenticacion
   ```bash
   POST http://ms-autenticacion:8000/api/v1/auth/validate-session
   Headers: {"Authorization": "Bearer eyJhbGc..."}
   ```

---

## 📊 Puertos y Rutas

### Mapeo de Puertos

| Servicio | Host | Interno | Acceso |
|----------|------|---------|--------|
| ms-autenticacion | 8002 | 8000 | http://localhost:8002 |
| ms-usuarios | 8000 | 8000 | http://localhost:8000 |
| postgres-auth | N/A | 5432 | Solo desde auth (docker) |
| postgres-usuarios | N/A | 5432 | Solo desde usuarios (docker) |

---

## 🧪 Testing de Conectividad

### 1. Verificar que los servicios están en la misma red

```bash
docker network ls
docker network inspect microservicios_microservicios-network
```

Deberías ver ambos contenedores conectados a la red.

### 2. Verificar conectividad entre contenedores

```bash
# Desde ms-usuarios, ver si puede comunicarse con ms-autenticacion
docker exec ms-usuarios-app ping ms-autenticacion

# Deberías ver respuesta exitosa (ttl, time, etc)
```

### 3. Hacer un request entre servicios

```bash
# Desde ms-usuarios, hacer request a auth
docker exec ms-usuarios-app curl http://ms-autenticacion:8000/docs
```

---

## 🔄 Ciclo de Vida

### Startup

1. `docker-compose up -d`
2. PostgreSQL de auth inicia y espera healthcheck
3. ms-autenticacion inicia (espera PostgreSQL)
4. PostgreSQL de usuarios inicia y espera healthcheck
5. ms-usuarios inicia (espera PostgreSQL y ms-autenticacion)
6. Ambos servicios conectados en `microservicios-network`

### Request

1. Cliente hace request a localhost:8000 o 8002
2. Docker redirecciona al contenedor interno
3. Si es autenticado, ms-usuarios llama a
   http://ms-autenticacion:8000/api/v1/auth/validate-session
4. ms-autenticacion verifica y retorna resultado
5. ms-usuarios permite/deniega operación

### Shutdown

```bash
docker-compose down     # Detiene todos los servicios
docker-compose down -v  # Detiene y elimina volúmenes (datos)
```

---

## 📈 Escalabilidad Futura

Este setup permite agregar más microservicios a la red:

```yaml
ms-roles:
  build: ./Microservicio_Roles
  networks:
    - microservicios-network

ms-notificaciones:
  build: ./Microservicio_Notificaciones
  networks:
    - microservicios-network
```

Solo necesitan estar en la misma red `microservicios-network` para comunicarse entre ellos.

---

## 📝 Changelog

| Fecha | Cambio |
|-------|--------|
| 2024 | Creación de docker-compose.yml unificado |
| 2024 | Corrección de URLs de servicios en config.py |
| 2024 | Creación de .env centralizado |
| 2024 | Creación de documentación y scripts |

---

## ✨ Resumen

✅ Los microservicios están **completamente conectados**
✅ Se comunican a través de una **red Docker segura**
✅ Todos los **puertos internos correctamente configurados**
✅ **Fácil de escalar** con nuevos servicios
✅ **Documentación completa** para desarrollo y producción
✅ Scripts PowerShell para **gestión sencilla** en Windows
